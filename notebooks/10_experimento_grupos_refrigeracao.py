"""10 - Experimento complementar: modelos por grupo de refrigeracao.

Motivacao: `flag_refrigerado` e a variavel mais importante do modelo (importancia por
permutacao 0,169) e separa custos de forma marcante (media CAD 3.419/ano para
refrigeradas contra 1.067 para secas). A pergunta e se um modelo por grupo captura
dinamicas proprias que o modelo unico dilui -- a mesma logica do Mixed Effects Random
Forest de Katreddi et al. (2023), citado no referencial.

Desenho:
  A) modelo UNICO treinado em toda a populacao MAINT;
  B) modelos SEPARADOS para refrigeradas (Y) e secas (N), com previsoes reunidas.

Ambos avaliados exatamente nas MESMAS linhas de teste (2025), com o mesmo cap de
outliers e o mesmo alvo transformado, de modo que a unica diferenca seja a
estratificacao. Nos modelos separados `flag_refrigerado` sai das features (constante
dentro do grupo).

Saidas: reports/tables/10_*.csv e reports/figures/10_experimento_grupos.png
"""
import numpy as np
import pandas as pd
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "processed"
TABLES = ROOT / "reports" / "tables"
FIG = ROOT / "reports" / "figures"
RANDOM_STATE = 42
TARGET = "custo_ano_real"
GRUPO = "flag_refrigerado"

df = pd.read_csv(DATA / "base_anual_carreta_deflacionada.csv")

# derivacao feita pelo notebook 05 (nao persistida na base): exposicao no inicio do ano
df = df.sort_values(["id_carreta", "ano"]).reset_index(drop=True)
df["km_acumulado_inicio_ano"] = df.groupby("id_carreta")["km_acumulado_fim_ano"].shift(1)

# ---- populacao de modelagem (D6) e particao temporal, iguais as do notebook 05 ----
base = df[(df[TARGET].notna()) & (df["populacao_maint_flag"] == 1)].copy()
base = base[base[GRUPO].isin(["Y", "N"])].copy()
train = base[base["ano"] < 2025].copy()
test = base[base["ano"] == 2025].copy()

# cap GLOBAL de outliers: aplicado igualmente nas duas abordagens, para que a unica
# diferenca entre A e B seja a estratificacao (e nao o tratamento da cauda)
CAP = train[TARGET].quantile(0.995)
train[TARGET] = train[TARGET].clip(upper=CAP)

NUM_BASE = ["idade_carreta", "eixos", "comprimento", "ano_modelo",
            "n_os_ano_anterior", "n_os_acum_ate_ano_anterior",
            "custo_ano_anterior", "custo_acum_ate_ano_anterior",
            "anos_ativo_ate_ano_anterior"]
CAT_BASE = ["cod_montadora", "flag_refrigerado", "unit_subtype", "tire_size",
            "suspension_type", "new_used_indicator", "regiao_operacao", "provincia_estado"]
CONTRATO_EXPL = ["tempo_contrato_meses_fim_ano", "share_maint_ano", "n_clientes_ano", "trocou_contrato_ano"]
CONTRATO_PRED = ["tempo_contrato_meses_inicio_ano"]

CEN = {
    "explicativo": {
        "num": NUM_BASE + ["km_acumulado_fim_ano", "km_rodado_ano",
                           "n_sistemas_vmrs_distintos_ano", "share_pm_ano"] + CONTRATO_EXPL,
        "cat": CAT_BASE + ["vmrs_predominante_ano"]},
    "preditivo": {
        "num": NUM_BASE + ["km_acumulado_inicio_ano"] + CONTRATO_PRED,
        "cat": CAT_BASE},
}
for v in CEN.values():
    v["num"] = [c for c in v["num"] if c in base.columns]
    v["cat"] = [c for c in v["cat"] if c in base.columns]


def make_model(nome, num, cat):
    pre = ColumnTransformer([
        ("num", Pipeline([("imp", SimpleImputer(strategy="median")), ("sc", StandardScaler())]), num),
        ("cat", Pipeline([("imp", SimpleImputer(strategy="constant", fill_value="NA")),
                          ("oh", OneHotEncoder(handle_unknown="infrequent_if_exist", min_frequency=50))]), cat),
    ])
    if nome == "gradient_boosting":
        est = GradientBoostingRegressor(n_estimators=300, max_depth=3, learning_rate=0.05,
                                        random_state=RANDOM_STATE)
    else:
        est = RandomForestRegressor(n_estimators=200, min_samples_leaf=20, n_jobs=-1,
                                    random_state=RANDOM_STATE)
    return Pipeline([("pre", pre),
                     ("mdl", TransformedTargetRegressor(regressor=est, func=np.log1p, inverse_func=np.expm1))])


def metricas(y, pred):
    return {"r2": r2_score(y, pred),
            "rmse": mean_squared_error(y, pred) ** 0.5,
            "mae": mean_absolute_error(y, pred)}


linhas, por_grupo, previsoes = [], [], {}
rng = np.random.default_rng(RANDOM_STATE)

for cen, cols in CEN.items():
    num, cat = cols["num"], cols["cat"]
    # features dos modelos por grupo: sem a variavel de grupo (constante dentro dele)
    cat_g = [c for c in cat if c != GRUPO]

    for nome in ["gradient_boosting", "random_forest"]:
        # ---------- A) modelo unico ----------
        mA = make_model(nome, num, cat)
        mA.fit(train[num + cat], train[TARGET])
        predA = pd.Series(np.clip(mA.predict(test[num + cat]), 0, None), index=test.index)

        # ---------- B) modelos separados por grupo ----------
        predB = pd.Series(index=test.index, dtype=float)
        tamanhos = {}
        for g in ["Y", "N"]:
            tr_g = train[train[GRUPO] == g]
            te_g = test[test[GRUPO] == g]
            tamanhos[g] = (len(tr_g), len(te_g))
            mg = make_model(nome, num, cat_g)
            mg.fit(tr_g[num + cat_g], tr_g[TARGET])
            predB.loc[te_g.index] = np.clip(mg.predict(te_g[num + cat_g]), 0, None)

        y = test[TARGET]
        mA_m, mB_m = metricas(y, predA), metricas(y, predB)
        linhas.append({
            "cenario": cen, "modelo": nome,
            "r2_unico": round(mA_m["r2"], 4), "r2_por_grupo": round(mB_m["r2"], 4),
            "delta_r2": round(mB_m["r2"] - mA_m["r2"], 4),
            "rmse_unico": round(mA_m["rmse"], 1), "rmse_por_grupo": round(mB_m["rmse"], 1),
            "delta_rmse": round(mB_m["rmse"] - mA_m["rmse"], 1),
            "mae_unico": round(mA_m["mae"], 1), "mae_por_grupo": round(mB_m["mae"], 1),
            "delta_mae": round(mB_m["mae"] - mA_m["mae"], 1),
        })

        # metricas dentro de cada grupo (onde o ganho, se houver, se materializa)
        for g in ["Y", "N"]:
            idx = test.index[test[GRUPO] == g]
            a, b = metricas(y.loc[idx], predA.loc[idx]), metricas(y.loc[idx], predB.loc[idx])
            por_grupo.append({
                "cenario": cen, "modelo": nome,
                "grupo": "refrigeradas (Y)" if g == "Y" else "secas (N)",
                "n_treino": tamanhos[g][0], "n_teste": tamanhos[g][1],
                "y_medio_teste": round(float(y.loc[idx].mean()), 1),
                "r2_unico": round(a["r2"], 4), "r2_por_grupo": round(b["r2"], 4),
                "delta_r2": round(b["r2"] - a["r2"], 4),
                "mae_unico": round(a["mae"], 1), "mae_por_grupo": round(b["mae"], 1),
                "delta_mae": round(b["mae"] - a["mae"], 1),
            })

        previsoes[(cen, nome)] = {"y": y, "unico": predA, "por_grupo": predB}
        print(f"ok: {cen} / {nome}")

res = pd.DataFrame(linhas)
res.to_csv(TABLES / "10_experimento_grupos.csv", index=False)
grp = pd.DataFrame(por_grupo)
grp.to_csv(TABLES / "10_experimento_grupos_detalhe.csv", index=False)

print()
print("=== GLOBAL (mesmas linhas de teste) ===")
print(res.to_string(index=False))
print()
print("=== POR GRUPO ===")
print(grp.to_string(index=False))

# ---------------- incerteza: bootstrap sobre as linhas de teste ----------------
# Os ganhos sao pequenos; sem intervalo nao da para dizer se superam o ruido amostral.
B = 2000
boot_rows = []
for (cen, nome), d_ in previsoes.items():
    yv = d_["y"].to_numpy()
    pa = d_["unico"].to_numpy()
    pb = d_["por_grupo"].to_numpy()
    n = len(yv)
    dr2, dmae = np.empty(B), np.empty(B)
    for b in range(B):
        idx = rng.integers(0, n, n)
        yb, ab, bb = yv[idx], pa[idx], pb[idx]
        dr2[b] = r2_score(yb, bb) - r2_score(yb, ab)
        dmae[b] = mean_absolute_error(yb, bb) - mean_absolute_error(yb, ab)
    boot_rows.append({
        "cenario": cen, "modelo": nome,
        "delta_r2": round(r2_score(yv, pb) - r2_score(yv, pa), 4),
        "ic95_r2_inf": round(float(np.percentile(dr2, 2.5)), 4),
        "ic95_r2_sup": round(float(np.percentile(dr2, 97.5)), 4),
        "prob_ganho_r2": round(float((dr2 > 0).mean()), 3),
        "delta_mae": round(mean_absolute_error(yv, pb) - mean_absolute_error(yv, pa), 1),
        "ic95_mae_inf": round(float(np.percentile(dmae, 2.5)), 1),
        "ic95_mae_sup": round(float(np.percentile(dmae, 97.5)), 1),
        "prob_reducao_mae": round(float((dmae < 0).mean()), 3),
    })
boot = pd.DataFrame(boot_rows)
boot.to_csv(TABLES / "10_experimento_grupos_incerteza.csv", index=False)
print()
print(f"=== INCERTEZA (bootstrap de {B} reamostragens do teste) ===")
print(boot.to_string(index=False))

# ---------------- figura ----------------
fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
for ax, cen in zip(axes, ["preditivo", "explicativo"]):
    sub = res[res["cenario"] == cen]
    x = np.arange(len(sub))
    ax.bar(x - 0.2, sub["r2_unico"], 0.4, label="modelo único", color="#3b6ea5")
    ax.bar(x + 0.2, sub["r2_por_grupo"], 0.4, label="modelos por grupo", color="#E8713A")
    ax.set_xticks(x)
    ax.set_xticklabels(sub["modelo"], fontsize=8)
    ax.set_title(f"Cenário {cen} — R² no teste 2025")
    ax.set_ylabel("R²")
    ax.legend(fontsize=8)
    for xi, (a, b) in enumerate(zip(sub["r2_unico"], sub["r2_por_grupo"])):
        ax.text(xi - 0.2, a + 0.004, f"{a:.3f}", ha="center", fontsize=7)
        ax.text(xi + 0.2, b + 0.004, f"{b:.3f}", ha="center", fontsize=7)
fig.tight_layout()
fig.savefig(FIG / "10_experimento_grupos.png", dpi=140)
plt.close(fig)
print("\nfigura: reports/figures/10_experimento_grupos.png")

# resumo interpretativo
melhor = res.loc[res["delta_r2"].idxmax()]
print(f"\nmaior ganho: {melhor['cenario']} / {melhor['modelo']} -> delta R2 = {melhor['delta_r2']:+.4f}")
