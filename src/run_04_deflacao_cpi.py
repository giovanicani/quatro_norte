# 04 - Deflacao dos custos por CPI Canada (StatCan)
# Converte custos historicos nominais (CAD) para valores de dezembro de 2025
# usando o CPI all-items Canada (StatCan, vetor v41690973, base 2002=100).
# Substitui a versao anterior que usava IPCA/BCB (indice brasileiro), incorreto
# para uma operacao canadense com custos em CAD.
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path.cwd()
if PROJECT_ROOT.name in ("notebooks", "src"):
    PROJECT_ROOT = PROJECT_ROOT.parent

DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
TABLES = PROJECT_ROOT / "reports" / "tables"
FIGURES = PROJECT_ROOT / "reports" / "figures"

MES_BASE = pd.Timestamp("2025-12-01")

base = pd.read_csv(DATA_PROCESSED / "base_mensal_carreta.csv", parse_dates=["ano_mes"])

cpi = pd.read_csv(DATA_RAW / "cpi_canada_statcan_2020_2025.csv", parse_dates=["ano_mes"])
cpi["indice_cpi"] = pd.to_numeric(cpi["indice_cpi"], errors="coerce")
cpi = cpi.sort_values("ano_mes").copy()
indice_base = float(cpi.loc[cpi["ano_mes"] == MES_BASE, "indice_cpi"].iloc[0])
cpi["fator_cpi_para_2025_12"] = indice_base / cpi["indice_cpi"]
cpi.to_csv(TABLES / "04_cpi_fatores.csv", index=False)

base_defl = base.merge(
    cpi[["ano_mes", "indice_cpi", "fator_cpi_para_2025_12"]], on="ano_mes", how="left"
)

COST_COLS = [
    "custo_total_mes",
    "custo_mao_obra_mes",
    "custo_pecas_mes",
    "custo_preventivo_total_mes",
    "custo_preventivo_mao_obra_mes",
    "custo_preventivo_pecas_mes",
]
for col in COST_COLS:
    base_defl[f"{col}_deflacionado"] = base_defl[col] * base_defl["fator_cpi_para_2025_12"]

km_ok = base_defl["km_valido_modelagem_flag"] == 1
for alvo_nominal, alvo_defl, col_custo in [
    ("custo_manutencao_interno_por_km", "custo_manutencao_interno_por_km_deflacionado", "custo_total_mes_deflacionado"),
    ("custo_manutencao_preventiva_por_km", "custo_manutencao_preventiva_por_km_deflacionado", "custo_preventivo_total_mes_deflacionado"),
    ("custo_preventivo_mao_obra_por_km", "custo_preventivo_mao_obra_por_km_deflacionado", "custo_preventivo_mao_obra_mes_deflacionado"),
]:
    base_defl[alvo_defl] = pd.NA
    base_defl.loc[km_ok, alvo_defl] = (
        base_defl.loc[km_ok, col_custo] / base_defl.loc[km_ok, "km_rodado_mes"]
    )
    base_defl[alvo_defl] = pd.to_numeric(base_defl[alvo_defl], errors="coerce")

validacao = pd.DataFrame(
    [
        {"checagem": "linhas_base", "valor": len(base_defl)},
        {"checagem": "meses_sem_cpi", "valor": int(base_defl["fator_cpi_para_2025_12"].isna().sum())},
        {"checagem": "mes_base", "valor": str(MES_BASE.date())},
        {"checagem": "indice_base", "valor": indice_base},
        {"checagem": "fator_min", "valor": float(cpi["fator_cpi_para_2025_12"].min())},
        {"checagem": "fator_max", "valor": float(cpi["fator_cpi_para_2025_12"].max())},
        {"checagem": "fonte", "valor": "StatCan v41690973 - CPI all-items Canada (2002=100)"},
    ]
)
validacao.to_csv(TABLES / "04_validacao_deflacao.csv", index=False)

anual = (
    base_defl.assign(ano=base_defl["ano_mes"].dt.year)
    .groupby("ano")
    .agg(
        custo_total_nominal=("custo_total_mes", "sum"),
        custo_total_deflacionado=("custo_total_mes_deflacionado", "sum"),
    )
    .reset_index()
)
anual.to_csv(TABLES / "04_comparacao_nominal_deflacionado.csv", index=False)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(anual["ano"], anual["custo_total_nominal"] / 1e6, marker="o", label="Nominal (CAD)")
ax.plot(anual["ano"], anual["custo_total_deflacionado"] / 1e6, marker="s", label="Deflacionado (CAD de dez/2025, CPI Canada)")
ax.set_xlabel("Ano")
ax.set_ylabel("Custo interno total (milhoes CAD)")
ax.set_title("Custo interno anual: nominal vs deflacionado (CPI Canada, base dez/2025)")
ax.legend()
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(FIGURES / "04_nominal_vs_deflacionado.png", dpi=150)
plt.close(fig)

base_defl.to_csv(DATA_PROCESSED / "base_mensal_carreta_deflacionada.csv", index=False)
print("OK deflacao CPI Canada")
print(anual)
