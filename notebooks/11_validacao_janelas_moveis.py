"""11 - Validacao com janelas moveis: o ganho dos modelos por grupo se sustenta?

O experimento 10 mostrou ganho do modelo estratificado por refrigeracao no cenario
preditivo, com IC 95% excluindo zero. Mas o bootstrap mede apenas o ruido amostral
DENTRO do unico ano de teste (2025) -- nao diz nada sobre variacao entre anos.

Aqui o mesmo confronto (modelo unico x modelos por grupo) e repetido com tres anos de
teste: 2023, 2024 e 2025, cada um treinado apenas com os anos anteriores. Se o ganho
aparecer nos tres, ele sustenta a escolha do modelo final; se oscilar de sinal, o
resultado de 2025 era especifico daquele ano.

Saidas: reports/tables/11_*.csv e reports/figures/11_janelas_moveis.png
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
ANOS_TESTE = [2023, 2024, 2025]

df = pd.read_csv(DATA / "base_anual_carreta_deflacionada.csv")
df = df.sort_values(["id_carreta", "ano"]).reset_index(drop=True)
df["km_acumulado_inicio_ano"] = df.groupby("id_carreta")["km_acumulado_fim_ano"].shift(1)

base = df[(df[TARGET].notna()) & (df["populacao_maint_flag"] == 1)].copy()
base = base[base[GRUPO].isin(["Y", "N"])].copy()

NUM = ["idade_carreta", "eixos", "comprimento", "ano_modelo",
       "n_os_ano_anterior", "n_os_acum_ate_ano_anterior",
       "custo_ano_anterior", "custo_acum_ate_ano_anterior",
       "anos_ativo_ate_ano_anterior", "km_acumulado_inicio_ano",
       "tempo_contrato_meses_inicio_ano"]
CAT = ["cod_montadora", "flag_refrigerado", "unit_subtype", "tire_size",
       "suspension_type", "new_used_indicator", "regiao_operacao", "provincia_estado"]
NUM = [c for c in NUM if c in base.columns]
CAT = [c for c in CAT if c in base.columns]
CAT_G = [c for c in CAT if c != GRUPO]


def make_model(nome, num, cat):
    pre = ColumnTransformer([
        ("num", Pipeline([("imp", SimpleImputer(strategy="median")), ("sc", StandardScaler())]), num),
        ("cat", Pipeline([("imp", SimpleImputer(strategy="constant", fill_value="NA")),
                          ("oh", OneHotEncoder(handle_unknown="infrequent_if_exist", min_frequency=50))]), cat),
    ])
    est = (GradientBoostingRegressor(n_estimators=300, max_depth=3, learning_rate=0.05,
                                     random_state=RANDOM_STATE)
           if nome == "gradient_boosting" else
           RandomForestRegressor(n_estimators=200, min_samples_leaf=20, n_jobs=-1,
                                 random_state=RANDOM_STATE))
    return Pipeline([("pre", pre),
                     ("mdl", TransformedTargetRegressor(regressor=est, func=np.log1p, inverse_func=np.expm1))])


linhas = []
for ano_teste in ANOS_TESTE:
    tr = base[base["ano"] < ano_teste].copy()
    te = base[base["ano"] == ano_teste].copy()
    if len(tr) < 500 or len(te) < 200:
        print(f"pulado {ano_teste}: dados insuficientes")
        continue
    cap = tr[TARGET].quantile(0.995)
    tr[TARGET] = tr[TARGET].clip(upper=cap)
    y = te[TARGET]

    for nome in ["gradient_boosting", "random_forest"]:
        mA = make_model(nome, NUM, CAT)
        mA.fit(tr[NUM + CAT], tr[TARGET])
        pA = np.clip(mA.predict(te[NUM + CAT]), 0, None)

        pB = pd.Series(index=te.index, dtype=float)
        for g in ["Y", "N"]:
            tr_g, te_g = tr[tr[GRUPO] == g], te[te[GRUPO] == g]
            mg = make_model(nome, NUM, CAT_G)
            mg.fit(tr_g[NUM + CAT_G], tr_g[TARGET])
            pB.loc[te_g.index] = np.clip(mg.predict(te_g[NUM + CAT_G]), 0, None)

        r2A, r2B = r2_score(y, pA), r2_score(y, pB)
        maeA, maeB = mean_absolute_error(y, pA), mean_absolute_error(y, pB)
        linhas.append({
            "ano_teste": ano_teste, "modelo": nome,
            "n_treino": len(tr), "n_teste": len(te),
            "anos_treino": f"{int(tr['ano'].min())}-{int(tr['ano'].max())}",
            "r2_unico": round(r2A, 4), "r2_por_grupo": round(r2B, 4),
            "delta_r2": round(r2B - r2A, 4),
            "mae_unico": round(maeA, 1), "mae_por_grupo": round(maeB, 1),
            "delta_mae": round(maeB - maeA, 1),
            "rmse_unico": round(mean_squared_error(y, pA) ** 0.5, 1),
            "rmse_por_grupo": round(mean_squared_error(y, pB) ** 0.5, 1),
        })
        print(f"ok: teste {ano_teste} / {nome} -> unico {r2A:.4f} | grupo {r2B:.4f} | delta {r2B - r2A:+.4f}")

res = pd.DataFrame(linhas)
res.to_csv(TABLES / "11_validacao_janelas_moveis.csv", index=False)

print()
print("=== VALIDACAO COM JANELAS MOVEIS ===")
print(res.to_string(index=False))

resumo = (res.groupby("modelo")
            .agg(anos=("ano_teste", "count"),
                 delta_r2_medio=("delta_r2", "mean"),
                 delta_r2_min=("delta_r2", "min"),
                 delta_r2_max=("delta_r2", "max"),
                 anos_com_ganho=("delta_r2", lambda s: int((s > 0).sum())),
                 delta_mae_medio=("delta_mae", "mean"))
            .round(4).reset_index())
resumo.to_csv(TABLES / "11_validacao_resumo.csv", index=False)
print()
print("=== RESUMO ===")
print(resumo.to_string(index=False))

fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
for ax, nome in zip(axes, ["gradient_boosting", "random_forest"]):
    sub = res[res["modelo"] == nome]
    x = np.arange(len(sub))
    ax.bar(x - 0.2, sub["r2_unico"], 0.4, label="modelo único", color="#3b6ea5")
    ax.bar(x + 0.2, sub["r2_por_grupo"], 0.4, label="modelos por grupo", color="#E8713A")
    ax.set_xticks(x); ax.set_xticklabels(sub["ano_teste"])
    ax.set_xlabel("ano de teste"); ax.set_ylabel("R²")
    ax.set_title(nome)
    ax.legend(fontsize=8)
    for xi, (a, b) in enumerate(zip(sub["r2_unico"], sub["r2_por_grupo"])):
        ax.text(xi - 0.2, a + 0.004, f"{a:.3f}", ha="center", fontsize=7)
        ax.text(xi + 0.2, b + 0.004, f"{b:.3f}", ha="center", fontsize=7)
fig.suptitle("Modelo único x modelos por grupo de refrigeração — cenário preditivo", fontsize=11)
fig.tight_layout()
fig.savefig(FIG / "11_janelas_moveis.png", dpi=140)
plt.close(fig)
print("\nfigura: reports/figures/11_janelas_moveis.png")

consistente = resumo[resumo["anos_com_ganho"] == resumo["anos"]]["modelo"].tolist()
print()
if consistente:
    print(f"ganho consistente nos {int(resumo['anos'].iloc[0])} anos para: {', '.join(consistente)}")
else:
    print("ganho NAO se sustenta em todos os anos testados")
