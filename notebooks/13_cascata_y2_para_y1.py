"""
Cascata Y2 -> Y1  (2026-09-02)
==============================

Decisao do Grupo: prever primeiro Y2 (`n_os_ano`) e usar essa previsao para ajudar a
prever Y1 (`custo_ano_real`).

Compara quatro caminhos no MESMO teste temporal (2025):

  A  direto        Y1 ~ features
  B  multiplicativo    Y1 = Y2previsto x Y3previsto            (ja rodado no notebook 05)
  C  cascata        Y1 ~ features + Y2previsto                 <- proposta do Grupo
  D  cascata dupla  Y1 ~ features + Y2previsto + Y3previsto

Disciplina anti-vazamento (dois niveis):
  1. Features: apenas atributos estaticos e historico DEFASADO (cenario preditivo do
     notebook 05). Nada contemporaneo ao ano.
  2. `Y2previsto` do TREINO e out-of-fold (GroupKFold por id_carreta). Usar a previsao
     in-sample tornaria Y2previsto artificialmente precisa no treino, o modelo de Y1
     passaria a confiar nela em excesso e o desempenho cairia no teste. As linhas de
     TESTE recebem a previsao do modelo ajustado em todo o treino.

Etapa 1 tambem testa reincorporar em Y2 as cinco variaveis que a curadoria retirou por
serem fracas em Y1, mas que sao moderadas/fortes em Y2 (cod_montadora, ano_modelo,
suspension_type, tire_size, new_used_indicator). A selecao usa validacao cruzada NO
TREINO — nunca o teste.

Saidas: reports/tables/13_*.csv
"""

from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import GroupKFold, cross_val_predict
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.inspection import permutation_importance

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
TABLES = PROJECT_ROOT / "reports" / "tables"
RANDOM_STATE = 42
Y1, Y2, Y3 = "custo_ano_real", "n_os_ano", "custo_medio_por_os_ano"

df = pd.read_csv(DATA_PROCESSED / "base_anual_carreta_deflacionada.csv")
df = df.sort_values(["id_carreta", "ano"]).reset_index(drop=True)
g = df.groupby("id_carreta")
df["km_acumulado_inicio_ano"] = g["km_acumulado_fim_ano"].shift(1)
df["vmrs_dist_media_5a"] = g["n_sistemas_vmrs_distintos_ano"].transform(
    lambda s: s.shift(1).rolling(5, min_periods=1).mean())

# ----------------------------------------------------------------- features ---
# cenario PREDITIVO do notebook 05 (curadoria D7): nada contemporaneo ao ano
NUM = ["idade_carreta", "eixos", "n_os_ano_anterior", "n_os_acum_ate_ano_anterior",
       "custo_ano_anterior", "custo_acum_ate_ano_anterior", "anos_ativo_ate_ano_anterior",
       "km_acumulado_inicio_ano", "vmrs_dist_media_5a", "tempo_contrato_meses_inicio_ano"]
CAT = ["flag_refrigerado", "unit_subtype", "descricao_carreta", "tipo_manutencao_ano"]

# as cinco retiradas na curadoria por serem fracas em Y1, mas relevantes em Y2
EXTRA_NUM = ["ano_modelo"]
EXTRA_CAT = ["cod_montadora", "suspension_type", "tire_size", "new_used_indicator"]

# ------------------------------------------------------- populacao e split ---
d = df[df[Y1].notna()].copy()
train = d[d["ano"] < 2025].copy()
test = d[d["ano"] == 2025].copy()
for alvo in (Y1, Y2, Y3):
    cap = train[alvo].quantile(0.995)
    train[alvo] = train[alvo].clip(upper=cap)
print(f"treino {len(train)} (2020-2024) | teste {len(test)} (2025)")

grupos = train["id_carreta"].to_numpy()
cv = GroupKFold(n_splits=5)


def pipe(est, num, cat, log=True):
    pre = ColumnTransformer([
        ("num", Pipeline([("imp", SimpleImputer(strategy="median")),
                          ("sc", StandardScaler())]), num),
        ("cat", Pipeline([("imp", SimpleImputer(strategy="constant", fill_value="NA")),
                          ("oh", OneHotEncoder(handle_unknown="infrequent_if_exist",
                                               min_frequency=50))]), cat),
    ])
    mdl = TransformedTargetRegressor(regressor=est, func=np.log1p,
                                     inverse_func=np.expm1) if log else est
    return Pipeline([("pre", pre), ("mdl", mdl)])


def familias():
    return {
        "random_forest": RandomForestRegressor(n_estimators=200, min_samples_leaf=20,
                                               n_jobs=-1, random_state=RANDOM_STATE),
        "gradient_boosting": GradientBoostingRegressor(n_estimators=300, max_depth=3,
                                                       learning_rate=0.05,
                                                       random_state=RANDOM_STATE),
        "ridge": Ridge(alpha=10.0),
        "regressao_linear_multipla": LinearRegression(),
    }


def metricas(y, p):
    return {"r2": round(r2_score(y, p), 4),
            "rmse": round(mean_squared_error(y, p) ** 0.5, 1),
            "mae": round(mean_absolute_error(y, p), 1)}


# =========================================================== ETAPA 1: Y2 ======
print("\n=== ETAPA 1: modelo de Y2 (n_os_ano) ===")
CONJUNTOS = {
    "curado (D7)": (NUM, CAT),
    "curado + 5 reincorporadas": (NUM + EXTRA_NUM, CAT + EXTRA_CAT),
}

sel_rows = []
for nome_conj, (num, cat) in CONJUNTOS.items():
    num = [c for c in num if c in train.columns]
    cat = [c for c in cat if c in train.columns]
    X, y = train[num + cat], train[Y2]
    for nome_m, est in familias().items():
        oof = np.clip(cross_val_predict(pipe(est, num, cat), X, y, cv=cv,
                                        groups=grupos, n_jobs=1), 0, None)
        sel_rows.append({"conjunto": nome_conj, "modelo": nome_m,
                         "cv_r2_treino": round(r2_score(y, oof), 4),
                         "cv_rmse_treino": round(mean_squared_error(y, oof) ** 0.5, 3),
                         "n_features": len(num) + len(cat)})
        print(f"  {nome_conj:28s} {nome_m:26s} CV R2={sel_rows[-1]['cv_r2_treino']}")

sel_y2 = pd.DataFrame(sel_rows).sort_values("cv_rmse_treino").reset_index(drop=True)
sel_y2.to_csv(TABLES / "13_selecao_modelo_y2.csv", index=False)

melhor = sel_y2.iloc[0]
NUM_Y2, CAT_Y2 = CONJUNTOS[melhor["conjunto"]]
NUM_Y2 = [c for c in NUM_Y2 if c in train.columns]
CAT_Y2 = [c for c in CAT_Y2 if c in train.columns]
est_y2 = familias()[melhor["modelo"]]
print(f"\nY2 escolhido por CV no treino: {melhor['modelo']} | conjunto: {melhor['conjunto']}")

ganho_extra = (sel_y2[sel_y2.conjunto == "curado (D7)"].iloc[0]["cv_r2_treino"],
               sel_y2[sel_y2.conjunto == "curado + 5 reincorporadas"].iloc[0]["cv_r2_treino"])
print(f"melhor CV R2 por conjunto -> curado: {ganho_extra[0]} | com as 5: {ganho_extra[1]}")

# --------------------- Y2 previsto: out-of-fold no treino, full-fit no teste ---
X_tr_y2, X_te_y2 = train[NUM_Y2 + CAT_Y2], test[NUM_Y2 + CAT_Y2]
oof_y2 = np.clip(cross_val_predict(pipe(est_y2, NUM_Y2, CAT_Y2), X_tr_y2, train[Y2],
                                   cv=cv, groups=grupos, n_jobs=1), 0, None)
mdl_y2 = pipe(est_y2, NUM_Y2, CAT_Y2).fit(X_tr_y2, train[Y2])
pred_y2_te = np.clip(mdl_y2.predict(X_te_y2), 0, None)

m_y2_te = metricas(test[Y2], pred_y2_te)
print(f"Y2 no teste 2025: R2={m_y2_te['r2']} RMSE={m_y2_te['rmse']} MAE={m_y2_te['mae']}")

# --------------------------------- Y3 previsto (mesma disciplina) -------------
est_y3 = RandomForestRegressor(n_estimators=200, min_samples_leaf=20, n_jobs=-1,
                               random_state=RANDOM_STATE)
oof_y3 = np.clip(cross_val_predict(pipe(est_y3, NUM, CAT), train[NUM + CAT], train[Y3],
                                   cv=cv, groups=grupos, n_jobs=1), 0, None)
mdl_y3 = pipe(est_y3, NUM, CAT).fit(train[NUM + CAT], train[Y3])
pred_y3_te = np.clip(mdl_y3.predict(test[NUM + CAT]), 0, None)
m_y3_te = metricas(test[Y3], pred_y3_te)
print(f"Y3 no teste 2025: R2={m_y3_te['r2']} RMSE={m_y3_te['rmse']}")

pd.DataFrame([
    {"alvo": Y2, "papel": "1a etapa da cascata", **m_y2_te,
     "modelo": melhor["modelo"], "conjunto_features": melhor["conjunto"]},
    {"alvo": Y3, "papel": "usado no caminho multiplicativo e na cascata dupla", **m_y3_te,
     "modelo": "random_forest", "conjunto_features": "curado (D7)"},
]).to_csv(TABLES / "13_etapa1_alvos.csv", index=False)

# =========================================================== ETAPA 2: Y1 ======
print("\n=== ETAPA 2: Y1 pelos quatro caminhos ===")
train_c, test_c = train.copy(), test.copy()
train_c["pred_n_os"], test_c["pred_n_os"] = oof_y2, pred_y2_te
train_c["pred_custo_medio_os"], test_c["pred_custo_medio_os"] = oof_y3, pred_y3_te

CAMINHOS = {
    "A_direto":          (NUM, CAT),
    "C_cascata_y2":      (NUM + ["pred_n_os"], CAT),
    "D_cascata_y2_y3":   (NUM + ["pred_n_os", "pred_custo_medio_os"], CAT),
}

rows, fits = [], {}
for nome, (num, cat) in CAMINHOS.items():
    for nome_m, est in familias().items():
        p = pipe(est, num, cat).fit(train_c[num + cat], train_c[Y1])
        pred = np.clip(p.predict(test_c[num + cat]), 0, None)
        rows.append({"caminho": nome, "modelo": nome_m, **metricas(test_c[Y1], pred)})
        fits[(nome, nome_m)] = (p, num, cat)

# caminho B: multiplicativo (nao tem modelo de Y1; e o produto das duas previsoes)
rows.append({"caminho": "B_multiplicativo", "modelo": "Y2xY3",
             **metricas(test_c[Y1], pred_y2_te * pred_y3_te)})

res = pd.DataFrame(rows).sort_values("rmse").reset_index(drop=True)
base_r2 = res[(res.caminho == "A_direto")].sort_values("rmse").iloc[0]["r2"]
res["delta_r2_vs_A"] = (res["r2"] - base_r2).round(4)
res.to_csv(TABLES / "13_cascata_comparacao.csv", index=False)
print(res.to_string(index=False))

melhor_por_caminho = res.sort_values("rmse").groupby("caminho").first().reset_index()
melhor_por_caminho = melhor_por_caminho.sort_values("rmse")
melhor_por_caminho.to_csv(TABLES / "13_cascata_melhor_por_caminho.csv", index=False)
print("\n=== melhor modelo de cada caminho ===")
print(melhor_por_caminho.to_string(index=False))

# ---------------------- quanto pesa pred_n_os no melhor caminho de cascata ----
melhor_casc = res[res.caminho.str.startswith(("C_", "D_"))].sort_values("rmse").iloc[0]
key = (melhor_casc["caminho"], melhor_casc["modelo"])
p, num, cat = fits[key]
perm = permutation_importance(p, test_c[num + cat], test_c[Y1], scoring="r2",
                              n_repeats=5, random_state=RANDOM_STATE, n_jobs=-1)
imp = (pd.DataFrame({"variavel": num + cat, "importancia": perm.importances_mean,
                     "desvio": perm.importances_std})
       .sort_values("importancia", ascending=False).reset_index(drop=True))
imp.insert(0, "caminho", melhor_casc["caminho"])
imp.insert(1, "modelo", melhor_casc["modelo"])
imp.to_csv(TABLES / "13_importancia_cascata.csv", index=False)
print(f"\n=== importancia por permutacao ({key[0]} / {key[1]}) ===")
print(imp.head(12).to_string(index=False))

pos = imp.index[imp.variavel == "pred_n_os"]
print("\npred_n_os ficou na posicao", (int(pos[0]) + 1) if len(pos) else "n/d",
      "de", len(imp), "variaveis")
