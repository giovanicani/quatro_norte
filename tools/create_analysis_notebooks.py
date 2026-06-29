from __future__ import annotations

from pathlib import Path

import nbformat as nbf
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = ROOT / "notebooks"
RAW = ROOT / "data" / "raw"


IPCA_2020_2025 = [
    ("2020-01", 0.21), ("2020-02", 0.25), ("2020-03", 0.07), ("2020-04", -0.31),
    ("2020-05", -0.38), ("2020-06", 0.26), ("2020-07", 0.36), ("2020-08", 0.24),
    ("2020-09", 0.64), ("2020-10", 0.86), ("2020-11", 0.89), ("2020-12", 1.35),
    ("2021-01", 0.25), ("2021-02", 0.86), ("2021-03", 0.93), ("2021-04", 0.31),
    ("2021-05", 0.83), ("2021-06", 0.53), ("2021-07", 0.96), ("2021-08", 0.87),
    ("2021-09", 1.16), ("2021-10", 1.25), ("2021-11", 0.95), ("2021-12", 0.73),
    ("2022-01", 0.54), ("2022-02", 1.01), ("2022-03", 1.62), ("2022-04", 1.06),
    ("2022-05", 0.47), ("2022-06", 0.67), ("2022-07", -0.68), ("2022-08", -0.36),
    ("2022-09", -0.29), ("2022-10", 0.59), ("2022-11", 0.41), ("2022-12", 0.62),
    ("2023-01", 0.53), ("2023-02", 0.84), ("2023-03", 0.71), ("2023-04", 0.61),
    ("2023-05", 0.23), ("2023-06", -0.08), ("2023-07", 0.12), ("2023-08", 0.23),
    ("2023-09", 0.26), ("2023-10", 0.24), ("2023-11", 0.28), ("2023-12", 0.56),
    ("2024-01", 0.42), ("2024-02", 0.83), ("2024-03", 0.16), ("2024-04", 0.38),
    ("2024-05", 0.46), ("2024-06", 0.21), ("2024-07", 0.38), ("2024-08", -0.02),
    ("2024-09", 0.44), ("2024-10", 0.56), ("2024-11", 0.39), ("2024-12", 0.52),
    ("2025-01", 0.16), ("2025-02", 1.31), ("2025-03", 0.56), ("2025-04", 0.43),
    ("2025-05", 0.26), ("2025-06", 0.24), ("2025-07", 0.26), ("2025-08", -0.11),
    ("2025-09", 0.48), ("2025-10", 0.09), ("2025-11", 0.18), ("2025-12", 0.33),
]


COMMON_SETUP = r"""
from pathlib import Path
import os
import warnings

import numpy as np
import pandas as pd

PROJECT_ROOT = Path.cwd()
if PROJECT_ROOT.name == "notebooks":
    PROJECT_ROOT = PROJECT_ROOT.parent

os.environ.setdefault("MPLCONFIGDIR", str(PROJECT_ROOT / ".cache" / "matplotlib"))
(PROJECT_ROOT / ".cache" / "matplotlib").mkdir(parents=True, exist_ok=True)

DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_INTERIM = PROJECT_ROOT / "data" / "interim"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
REPORTS = PROJECT_ROOT / "reports"
FIGURES = REPORTS / "figures"
TABLES = REPORTS / "tables"
ANALYSIS_START = pd.Timestamp("2020-01-01")
ANALYSIS_END_EXCLUSIVE = pd.Timestamp("2026-01-01")
ANALYSIS_END = pd.Timestamp("2025-12-31")
KM_MIN_MES_ALVO = 500.0
PREVENTIVE_VMRS_CODES = {"PM"}

for path in [DATA_INTERIM, DATA_PROCESSED, FIGURES, TABLES]:
    path.mkdir(parents=True, exist_ok=True)

warnings.filterwarnings("ignore", category=FutureWarning)
pd.set_option("display.max_columns", 80)
pd.set_option("display.width", 140)

FILES = {
    "dim_carretas": DATA_RAW / "dim_carretas_2020-01-01_to_2025-12-31.csv",
    "fato_contratos": DATA_RAW / "fato_contratos_2020-01-01_to_2025-12-31.csv",
    "fato_gps": DATA_RAW / "fato_gps_2020-01-01_to_2025-12-31.csv",
    "fato_readings": DATA_RAW / "fato_readings_2020-01-01_to_2025-12-31.csv",
    "fato_wo": DATA_RAW / "fato_wo_2020-01-01_to_2025-12-31.csv",
    "fato_wo_labour": DATA_RAW / "fato_wo_labour_2020-01-01_to_2025-12-31.csv",
    "fato_wo_parts": DATA_RAW / "fato_wo_parts_2020-01-01_to_2025-12-31.csv",
}

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.strip().lower() for c in df.columns]
    return df

def read_csv(name: str, **kwargs) -> pd.DataFrame:
    return normalize_columns(pd.read_csv(FILES[name], low_memory=False, **kwargs))

def month_start(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce").dt.to_period("M").dt.to_timestamp()

def as_number(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")

def mode_or_unknown(series: pd.Series, unknown: str = "SEM_INFORMACAO") -> str:
    values = series.dropna().astype(str)
    if values.empty:
        return unknown
    return values.mode().iloc[0]
"""


def md(text: str):
    return nbf.v4.new_markdown_cell(text.strip())


def code(text: str):
    return nbf.v4.new_code_cell(text.strip())


def write_notebook(path: Path, cells: list):
    nb = nbf.v4.new_notebook()
    nb["cells"] = cells
    nb["metadata"] = {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {"name": "python", "pygments_lexer": "ipython3"},
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    nbf.write(nb, path)


def notebook_00():
    return [
        md("""# 00 - Contexto e inventario dos dados

## tl;dr
Este notebook inventaria os arquivos brutos do projeto Quatro Norte, confirma o modelo estrela e registra os principais riscos iniciais antes da preparacao analitica."""),
        md("""## Context & Methods

O objetivo do projeto e analisar historico de manutencao de carretas e prever custo interno de manutencao por km. A fonte local e a extracao `data/extract_custo_interno_km.sql`, materializada em sete CSVs em `data/raw`.

### Key Assumptions
- Os arquivos em `data/raw` sao a camada bruta e nao devem ser alterados manualmente.
- O identificador comum entre as bases e `ID_CARRETA`.
- A variavel-alvo sera derivada em etapa posterior, pois ainda nao existe pronta nos CSVs."""),
        code(COMMON_SETUP),
        md("## Data\n\n### 1. Listar arquivos disponiveis"),
        code("""
file_inventory = []
for name, path in FILES.items():
    header = pd.read_csv(path, nrows=0)
    file_inventory.append({
        "base": name,
        "arquivo": path.name,
        "tamanho_mb": path.stat().st_size / 1024**2,
        "n_colunas": len(header.columns),
        "colunas": ", ".join(header.columns),
    })

file_inventory = pd.DataFrame(file_inventory)
file_inventory
"""),
        md("### 2. Medir volumes, chaves e cobertura temporal"),
        code("""
date_columns = {
    "dim_carretas": ["DATA_ENTRADA_SERVICO"],
    "fato_contratos": ["DATA_INICIO", "DATA_FIM"],
    "fato_gps": ["DATA_HORA_GPS"],
    "fato_readings": ["DATA_LEITURA"],
    "fato_wo": ["DATA_OS"],
    "fato_wo_labour": ["DATA_OS"],
    "fato_wo_parts": ["DATA_OS"],
}

primary_keys = {
    "dim_carretas": "ID_CARRETA",
    "fato_contratos": "ID_CONTRATO_CARRETA",
    "fato_gps": None,
    "fato_readings": "ID_LEITURA",
    "fato_wo": "ID_OS",
    "fato_wo_labour": "ID_LINHA_MAO_OBRA",
    "fato_wo_parts": "ID_LINHA_PECA",
}

rows = []
for name, path in FILES.items():
    df = pd.read_csv(path, low_memory=False)
    row = {
        "base": name,
        "linhas": len(df),
        "colunas": len(df.columns),
        "grao": {
            "dim_carretas": "uma carreta",
            "fato_readings": "uma leitura de odometro",
            "fato_wo": "uma ordem de servico",
            "fato_wo_labour": "uma linha de mao de obra",
            "fato_wo_parts": "uma linha de peca",
            "fato_contratos": "uma carreta-contrato",
            "fato_gps": "um ponto GPS por carreta/dia",
        }[name],
    }
    if "ID_CARRETA" in df.columns:
        row["carretas_distintas"] = df["ID_CARRETA"].nunique(dropna=True)
    pk = primary_keys[name]
    if pk:
        row["chave_primaria"] = pk
        row["pk_distintas"] = df[pk].nunique(dropna=True)
        row["pk_duplicadas"] = len(df) - df[pk].nunique(dropna=True)
    for col in date_columns[name]:
        if col in df.columns:
            parsed = pd.to_datetime(df[col], errors="coerce")
            row[f"{col.lower()}_min"] = parsed.min()
            row[f"{col.lower()}_max"] = parsed.max()
            row[f"{col.lower()}_nulos"] = parsed.isna().sum()
    rows.append(row)

inventory = pd.DataFrame(rows)
inventory.to_csv(TABLES / "00_inventario_bases.csv", index=False)
inventory
"""),
        md("## Results\n\n### 3. Confirmar relacionamento estrela"),
        code("""
dim_ids = set(pd.read_csv(FILES["dim_carretas"], usecols=["ID_CARRETA"])["ID_CARRETA"])

integrity_rows = []
for name in [n for n in FILES if n != "dim_carretas"]:
    df = pd.read_csv(FILES[name], usecols=["ID_CARRETA"])
    ids = set(df["ID_CARRETA"].dropna())
    integrity_rows.append({
        "base": name,
        "carretas_distintas": len(ids),
        "ids_fora_dim_carretas": len(ids - dim_ids),
        "cobertura_sobre_dim": len(ids) / len(dim_ids),
    })

star_check = pd.DataFrame(integrity_rows)
star_check.to_csv(TABLES / "00_validacao_modelo_estrela.csv", index=False)
star_check
"""),
        md("### 4. Registrar riscos iniciais dos dados"),
        code("""
wo = read_csv("fato_wo", usecols=["ID_OS", "DATA_OS", "TOTAL_INTERNO_MAO_OBRA", "TOTAL_INTERNO_PECAS"])
labour = read_csv("fato_wo_labour", usecols=["ID_OS", "COD_SISTEMA_VMRS", "SISTEMA_VMRS"])
gps = read_csv("fato_gps", usecols=["ID_CARRETA", "DATA_HORA_GPS"])
readings = read_csv("fato_readings", usecols=["ID_CARRETA", "KM_ACUMULADO", "KM_RESET_EM", "KM_RESET_PARA"])

wo["data_os"] = pd.to_datetime(wo["data_os"], errors="coerce")
for col in ["total_interno_mao_obra", "total_interno_pecas"]:
    wo[col] = as_number(wo[col])

gps["data_hora_gps"] = pd.to_datetime(gps["data_hora_gps"], errors="coerce")
labour["flag_linha_preventiva"] = (
    labour["cod_sistema_vmrs"].astype(str).str.upper().isin(PREVENTIVE_VMRS_CODES)
    | labour["sistema_vmrs"].astype(str).str.upper().str.contains("PREVENTIVE", na=False)
)

risks = pd.DataFrame([
    {
        "risco": "GPS com cobertura parcial",
        "evidencia": f"{gps['data_hora_gps'].min()} a {gps['data_hora_gps'].max()}, {gps['id_carreta'].nunique()} carretas",
        "tratamento_planejado": "usar como analise complementar, nao como feature central para todo o historico",
    },
    {
        "risco": "OS fora da janela declarada",
        "evidencia": f"{(wo['data_os'] >= pd.Timestamp('2026-01-01')).sum()} registros com DATA_OS >= 2026-01-01",
        "tratamento_planejado": "filtrar na base analitica mensal",
    },
    {
        "risco": "Custos negativos e zerados",
        "evidencia": f"{((wo['total_interno_mao_obra'] < 0) | (wo['total_interno_pecas'] < 0)).sum()} OS com algum custo negativo",
        "tratamento_planejado": "analisar como ajustes/estornos e filtrar apenas na modelagem se necessario",
    },
    {
        "risco": "Resets de odometro",
        "evidencia": f"{readings[['km_reset_em', 'km_reset_para']].notna().any(axis=1).sum()} leituras com campos de reset",
        "tratamento_planejado": "tratar deltas negativos ou anormais antes de calcular km do periodo",
    },
    {
        "risco": "Variavel-alvo ausente",
        "evidencia": "nao ha coluna pronta de custo por km nos CSVs brutos",
        "tratamento_planejado": "derivar custo por km no grao carreta x mes",
    },
    {
        "risco": "Alvo preventivo diferente de custo interno total",
        "evidencia": f"{labour['flag_linha_preventiva'].sum()} linhas de mao de obra classificadas como preventivas por VMRS PM/PREVENTIVE",
        "tratamento_planejado": "criar alvo primario custo_manutencao_preventiva_por_km e manter custo interno total como sensibilidade",
    },
    {
        "risco": "Tipo de manutencao contratual como confundidor",
        "evidencia": "MAINT/NET/MIX alteram a responsabilidade economica sobre manutencao",
        "tratamento_planejado": "usar MAINT como populacao principal de modelagem e reportar NET/MIX como segmentos/caveats",
    },
    {
        "risco": "Meses com baixa quilometragem distorcem razoes custo/km",
        "evidencia": f"piso metodologico definido: {KM_MIN_MES_ALVO:.0f} km/mes",
        "tratamento_planejado": "calcular alvos por km apenas para meses com km_rodado_mes >= piso",
    },
])

risks.to_csv(TABLES / "00_riscos_iniciais.csv", index=False)
risks
"""),
        md("""## Takeaways

- As bases permitem montar uma visao mensal por carreta, integrando manutencao, odometro, contratos e atributos do ativo.
- `ID_CARRETA` e a chave estrutural do projeto; `ID_OS` detalha os custos de mao de obra e pecas.
- A preparacao precisa tratar qualidade de datas, resets de odometro, custos negativos/zerados, baixa quilometragem mensal e a cobertura parcial de GPS."""),
    ]


def notebook_01():
    return [
        md("""# 01 - Qualidade e integridade dos dados

## tl;dr
Este notebook valida chaves, duplicidades, valores ausentes, custos, odometro e datas antes da construcao da base mensal."""),
        md("""## Context & Methods

A qualidade dos dados e avaliada antes de qualquer modelagem para evitar conclusoes fortes com base em registros inconsistentes.

### Key Assumptions
- Dados brutos permanecem imutaveis.
- OS em `2026-01-01` serao excluidas da base analitica por estarem fora da janela 2020-2025.
- Custos negativos sao preservados no diagnostico e tratados com cautela na modelagem."""),
        code(COMMON_SETUP),
        md("## Data\n\n### 1. Carregar chaves principais"),
        code("""
dim = read_csv("dim_carretas")
wo_keys = read_csv("fato_wo", usecols=["ID_OS", "ID_CARRETA", "DATA_OS"])
labour_keys = read_csv("fato_wo_labour", usecols=["ID_LINHA_MAO_OBRA", "ID_OS", "ID_CARRETA", "DATA_OS"])
parts_keys = read_csv("fato_wo_parts", usecols=["ID_LINHA_PECA", "ID_OS", "ID_CARRETA", "DATA_OS"])
readings_keys = read_csv("fato_readings", usecols=["ID_LEITURA", "ID_CARRETA", "DATA_LEITURA", "ID_OS"])
contracts_keys = read_csv("fato_contratos", usecols=["ID_CONTRATO_CARRETA", "ID_CARRETA", "DATA_INICIO", "DATA_FIM"])
gps_keys = read_csv("fato_gps", usecols=["ID_CARRETA", "DATA_HORA_GPS"])
labour_class = read_csv("fato_wo_labour", usecols=["ID_OS", "ID_CARRETA", "DATA_OS", "COD_TIPO_SERVICO", "COD_SISTEMA_VMRS", "SISTEMA_VMRS", "CUSTO_INTERNO_MAO_OBRA"])
parts_quality = read_csv("fato_wo_parts", usecols=["ID_OS", "ID_CARRETA", "DATA_OS", "FLAG_GARANTIA", "CUSTO_INTERNO_PECA"])

datasets = {
    "dim_carretas": dim,
    "fato_wo": wo_keys,
    "fato_wo_labour": labour_keys,
    "fato_wo_parts": parts_keys,
    "fato_readings": readings_keys,
    "fato_contratos": contracts_keys,
    "fato_gps": gps_keys,
}
"""),
        md("### 2. Validar chaves, duplicidades e integridade referencial"),
        code("""
dim_ids = set(dim["id_carreta"].dropna())
wo_ids = set(wo_keys["id_os"].dropna())

primary_keys = {
    "dim_carretas": "id_carreta",
    "fato_wo": "id_os",
    "fato_wo_labour": "id_linha_mao_obra",
    "fato_wo_parts": "id_linha_peca",
    "fato_readings": "id_leitura",
    "fato_contratos": "id_contrato_carreta",
}

integrity = []
for name, df in datasets.items():
    row = {"base": name, "linhas": len(df)}
    if "id_carreta" in df.columns:
        row["ids_carreta_fora_dim"] = len(set(df["id_carreta"].dropna()) - dim_ids)
    pk = primary_keys.get(name)
    if pk:
        row["pk"] = pk
        row["pk_nulos"] = int(df[pk].isna().sum())
        row["pk_duplicadas"] = int(df[pk].duplicated(keep=False).sum())
    if name in ["fato_wo_labour", "fato_wo_parts"]:
        row["id_os_fora_fato_wo"] = len(set(df["id_os"].dropna()) - wo_ids)
    integrity.append(row)

integrity = pd.DataFrame(integrity)
integrity.to_csv(TABLES / "01_integridade_chaves.csv", index=False)
integrity
"""),
        md("### 3. Medir valores ausentes por coluna"),
        code("""
missing_rows = []
for name, path in FILES.items():
    df = pd.read_csv(path, low_memory=False)
    for col, missing in df.isna().sum().items():
        missing_rows.append({
            "base": name,
            "coluna": col,
            "nulos": int(missing),
            "pct_nulos": float(missing / len(df)) if len(df) else np.nan,
        })

missing = pd.DataFrame(missing_rows).sort_values(["pct_nulos", "nulos"], ascending=False)
missing.to_csv(TABLES / "01_valores_ausentes.csv", index=False)
missing.head(30)
"""),
        md("## Results\n\n### 4. Diagnosticar custos negativos, zerados e extremos"),
        code("""
wo_cost = read_csv("fato_wo", usecols=["ID_OS", "ID_CARRETA", "DATA_OS", "TOTAL_INTERNO_MAO_OBRA", "TOTAL_INTERNO_PECAS"])
wo_cost["data_os"] = pd.to_datetime(wo_cost["data_os"], errors="coerce")
for col in ["total_interno_mao_obra", "total_interno_pecas"]:
    wo_cost[col] = as_number(wo_cost[col])
wo_cost["custo_total"] = wo_cost["total_interno_mao_obra"].fillna(0) + wo_cost["total_interno_pecas"].fillna(0)

cost_summary = []
for col in ["total_interno_mao_obra", "total_interno_pecas", "custo_total"]:
    s = wo_cost[col]
    cost_summary.append({
        "campo": col,
        "soma": s.sum(),
        "media": s.mean(),
        "mediana": s.median(),
        "p95": s.quantile(0.95),
        "p99": s.quantile(0.99),
        "max": s.max(),
        "negativos": int((s < 0).sum()),
        "zeros": int((s == 0).sum()),
    })

cost_summary = pd.DataFrame(cost_summary)
cost_summary.to_csv(TABLES / "01_diagnostico_custos.csv", index=False)
cost_summary
"""),
        md("### 5. Avaliar odometro e deltas de quilometragem"),
        code("""
readings = read_csv("fato_readings")
readings["data_leitura"] = pd.to_datetime(readings["data_leitura"], errors="coerce")
for col in ["km_acumulado", "km_reset_em", "km_reset_para"]:
    readings[col] = as_number(readings[col])

readings = readings.sort_values(["id_carreta", "data_leitura", "id_leitura"])
readings["km_anterior"] = readings.groupby("id_carreta")["km_acumulado"].shift(1)
readings["delta_km_bruto"] = readings["km_acumulado"] - readings["km_anterior"]
positive_delta = readings.loc[readings["delta_km_bruto"] >= 0, "delta_km_bruto"]
limite_delta_km = min(max(float(positive_delta.quantile(0.999)), 50000.0), 250000.0)
readings["delta_km_tratado"] = readings["delta_km_bruto"].where(
    (readings["delta_km_bruto"] >= 0) & (readings["delta_km_bruto"] <= limite_delta_km)
)

odo_summary = pd.DataFrame([
    {"metrica": "leituras", "valor": len(readings)},
    {"metrica": "carretas", "valor": readings["id_carreta"].nunique()},
    {"metrica": "km_acumulado_nulo", "valor": readings["km_acumulado"].isna().sum()},
    {"metrica": "km_acumulado_negativo", "valor": (readings["km_acumulado"] < 0).sum()},
    {"metrica": "leituras_com_reset", "valor": readings[["km_reset_em", "km_reset_para"]].notna().any(axis=1).sum()},
    {"metrica": "delta_km_negativo", "valor": (readings["delta_km_bruto"] < 0).sum()},
    {"metrica": "delta_km_acima_limite", "valor": (readings["delta_km_bruto"] > limite_delta_km).sum()},
    {"metrica": "limite_delta_km_usado", "valor": limite_delta_km},
])

odo_summary.to_csv(TABLES / "01_diagnostico_odometro.csv", index=False)
odo_summary
"""),
        md("### 6. Verificar consistencia temporal"),
        code("""
date_checks = []
for name, df in {
    "fato_wo": wo_keys,
    "fato_wo_labour": labour_keys,
    "fato_wo_parts": parts_keys,
    "fato_readings": readings_keys,
    "fato_contratos": contracts_keys,
    "fato_gps": gps_keys,
}.items():
    for col in [c for c in df.columns if c.startswith("data_")]:
        parsed = pd.to_datetime(df[col], errors="coerce")
        date_checks.append({
            "base": name,
            "campo": col,
            "min": parsed.min(),
            "max": parsed.max(),
            "nulos": int(parsed.isna().sum()),
            "antes_2020": int((parsed < pd.Timestamp("2020-01-01")).sum()),
            "apos_2025": int((parsed >= pd.Timestamp("2026-01-01")).sum()),
        })

date_checks = pd.DataFrame(date_checks)
date_checks.to_csv(TABLES / "01_consistencia_temporal.csv", index=False)
date_checks
"""),
        md("### 7. Verificar classificacao de manutencao preventiva, garantia e contrato"),
        code("""
labour_class["data_os"] = pd.to_datetime(labour_class["data_os"], errors="coerce")
labour_class["custo_interno_mao_obra"] = as_number(labour_class["custo_interno_mao_obra"]).fillna(0)
labour_class["flag_linha_preventiva"] = (
    labour_class["cod_sistema_vmrs"].astype(str).str.upper().isin(PREVENTIVE_VMRS_CODES)
    | labour_class["sistema_vmrs"].astype(str).str.upper().str.contains("PREVENTIVE", na=False)
)
preventive_os_ids = set(labour_class.loc[labour_class["flag_linha_preventiva"], "id_os"].dropna())

parts_quality["data_os"] = pd.to_datetime(parts_quality["data_os"], errors="coerce")
parts_quality["custo_interno_peca"] = as_number(parts_quality["custo_interno_peca"]).fillna(0)
parts_quality["flag_garantia_bool"] = parts_quality["flag_garantia"].astype(str).str.upper().eq("Y")

contracts_profile = read_csv("fato_contratos", usecols=["ID_CARRETA", "TIPO_MANUTENCAO", "DATA_INICIO", "DATA_FIM"])
contracts_profile["data_inicio"] = pd.to_datetime(contracts_profile["data_inicio"], errors="coerce")
contracts_profile["data_fim"] = pd.to_datetime(contracts_profile["data_fim"], errors="coerce")
contracts_profile["duracao_contrato_meses_observada"] = (
    contracts_profile["data_fim"].fillna(ANALYSIS_END) - contracts_profile["data_inicio"]
).dt.days / 30.4375

preventive_profile = pd.DataFrame([
    {"metrica": "linhas_mao_obra", "valor": len(labour_class)},
    {"metrica": "linhas_mao_obra_preventiva", "valor": int(labour_class["flag_linha_preventiva"].sum())},
    {"metrica": "os_com_linha_preventiva", "valor": len(preventive_os_ids)},
    {"metrica": "share_linhas_preventivas", "valor": float(labour_class["flag_linha_preventiva"].mean())},
    {"metrica": "linhas_peca_garantia", "valor": int(parts_quality["flag_garantia_bool"].sum())},
    {"metrica": "share_linhas_peca_garantia", "valor": float(parts_quality["flag_garantia_bool"].mean())},
    {"metrica": "duracao_contrato_meses_mediana", "valor": float(contracts_profile["duracao_contrato_meses_observada"].median())},
])
preventive_profile.to_csv(TABLES / "01_perfil_preventiva_garantia_contrato.csv", index=False)
preventive_profile
"""),
        md("### 8. Consolidar regras para a base analitica"),
        code("""
treatment_rules = pd.DataFrame([
    {"tema": "janela temporal", "regra": "manter eventos de OS com DATA_OS < 2026-01-01"},
    {"tema": "odometro", "regra": "usar delta entre leituras consecutivas, remover deltas invalidos e prorratear KM entre meses-calendario"},
    {"tema": "piso de quilometragem", "regra": f"calcular alvos por km apenas para meses com km_rodado_mes >= {KM_MIN_MES_ALVO:.0f}"},
    {"tema": "alvo preventivo", "regra": "classificar OS preventiva por linha de mao de obra VMRS PM/PREVENTIVE; pecas entram como preventivas quando a OS tem linha preventiva"},
    {"tema": "zero manutencao", "regra": "manter meses com km valido e custo preventivo zero, pois representam custo esperado mensal para orcamento"},
    {"tema": "custos negativos", "regra": "preservar no diagnostico; excluir alvo negativo apenas na modelagem preditiva"},
    {"tema": "tipo_manutencao", "regra": "usar MAINT como populacao principal da modelagem e tratar NET/MIX como segmentos/caveats"},
    {"tema": "contratos", "regra": "ligar por ID_CARRETA e mes vigente dentro de DATA_INICIO e DATA_FIM"},
])
treatment_rules.to_csv(TABLES / "01_regras_tratamento.csv", index=False)
treatment_rules
"""),
        md("""## Takeaways

- A integridade por `ID_CARRETA` deve ser validada antes de qualquer juncao.
- Deltas de odometro negativos ou anormais serao removidos e a quilometragem sera prorrateada entre meses-calendario.
- A classificacao preventiva sera construida por VMRS PM/PREVENTIVE e documentada como aproximacao operacional.
- A base mensal deve registrar filtros aplicados, preservando os dados brutos para auditoria."""),
    ]


def notebook_02():
    return [
        md("""# 02 - Base analitica mensal

## tl;dr
Este notebook constroi a base principal no grao `id_carreta x ano_mes`, com custos, km, contrato vigente, atributos do ativo e historico sem vazamento temporal."""),
        md("""## Context & Methods

A modelagem sera feita em nivel mensal para equilibrar disponibilidade de custos, leituras de odometro e contratos.

### Key Assumptions
- Meses sem OS recebem custo zero quando ha quilometragem observada.
- Meses com `km_rodado_mes < KM_MIN_MES_ALVO` ficam sem alvo por km para reduzir explosao da razao.
- O alvo primario e preventivo: mao de obra VMRS PM/PREVENTIVE + pecas de OS com linha preventiva.
- O alvo-espelho de mao de obra preventiva por km sera mantido como medida mais limpa, pois a mao de obra e atribuivel por linha VMRS.
- Features acumuladas sao defasadas quando representam historico anterior ao mes analisado."""),
        code(COMMON_SETUP),
        md("## Data\n\n### 1. Carregar bases essenciais"),
        code("""
dim = read_csv("dim_carretas")
wo = read_csv("fato_wo")
labour = read_csv("fato_wo_labour")
parts = read_csv("fato_wo_parts")
readings = read_csv("fato_readings")
contracts = read_csv("fato_contratos")

wo["data_os"] = pd.to_datetime(wo["data_os"], errors="coerce")
labour["data_os"] = pd.to_datetime(labour["data_os"], errors="coerce")
parts["data_os"] = pd.to_datetime(parts["data_os"], errors="coerce")
readings["data_leitura"] = pd.to_datetime(readings["data_leitura"], errors="coerce")
contracts["data_inicio"] = pd.to_datetime(contracts["data_inicio"], errors="coerce")
contracts["data_fim"] = pd.to_datetime(contracts["data_fim"], errors="coerce")
dim["data_entrada_servico"] = pd.to_datetime(dim["data_entrada_servico"], errors="coerce")

for col in ["total_interno_mao_obra", "total_interno_pecas"]:
    wo[col] = as_number(wo[col]).fillna(0)
labour["custo_interno_mao_obra"] = as_number(labour["custo_interno_mao_obra"]).fillna(0)
parts["custo_interno_peca"] = as_number(parts["custo_interno_peca"]).fillna(0)
parts["qtd_real"] = as_number(parts["qtd_real"]).fillna(0)
for col in ["km_acumulado", "km_reset_em", "km_reset_para"]:
    readings[col] = as_number(readings[col])
contracts["franquia_km_mensal"] = as_number(contracts["franquia_km_mensal"])
"""),
        md("### 2. Agregar custos totais, preventivos, garantia e regiao por mes"),
        code("""
wo = wo[(wo["data_os"] >= ANALYSIS_START) & (wo["data_os"] < ANALYSIS_END_EXCLUSIVE)].copy()
labour = labour[(labour["data_os"] >= ANALYSIS_START) & (labour["data_os"] < ANALYSIS_END_EXCLUSIVE)].copy()
parts = parts[(parts["data_os"] >= ANALYSIS_START) & (parts["data_os"] < ANALYSIS_END_EXCLUSIVE)].copy()

wo["ano_mes"] = month_start(wo["data_os"])
wo["custo_total"] = wo["total_interno_mao_obra"] + wo["total_interno_pecas"]
wo["regiao_operacao_evento"] = (
    wo["provincia_estado"].where(wo["provincia_estado"].notna(), wo["cod_local_os"])
    .fillna("SEM_INFORMACAO")
)

custos_mes = (
    wo.groupby(["id_carreta", "ano_mes"], as_index=False)
    .agg(
        custo_mao_obra_mes=("total_interno_mao_obra", "sum"),
        custo_pecas_mes=("total_interno_pecas", "sum"),
        custo_total_mes=("custo_total", "sum"),
        n_os_mes=("id_os", "nunique"),
    )
)

labour["ano_mes"] = month_start(labour["data_os"])
labour["flag_linha_preventiva"] = (
    labour["cod_sistema_vmrs"].astype(str).str.upper().isin(PREVENTIVE_VMRS_CODES)
    | labour["sistema_vmrs"].astype(str).str.upper().str.contains("PREVENTIVE", na=False)
)
preventive_os_ids = set(labour.loc[labour["flag_linha_preventiva"], "id_os"].dropna())

mao_obra_preventiva_mes = (
    labour.loc[labour["flag_linha_preventiva"]]
    .groupby(["id_carreta", "ano_mes"], as_index=False)
    .agg(custo_preventivo_mao_obra_mes=("custo_interno_mao_obra", "sum"))
)

parts["ano_mes"] = month_start(parts["data_os"])
parts["flag_peca_garantia"] = parts["flag_garantia"].astype(str).str.upper().eq("Y")
parts["flag_os_preventiva"] = parts["id_os"].isin(preventive_os_ids)
parts["custo_peca_garantia_linha"] = np.where(parts["flag_peca_garantia"], parts["custo_interno_peca"], 0.0)

pecas_preventivas_mes = (
    parts.loc[parts["flag_os_preventiva"]]
    .groupby(["id_carreta", "ano_mes"], as_index=False)
    .agg(custo_preventivo_pecas_mes=("custo_interno_peca", "sum"))
)

garantia_mes = (
    parts.groupby(["id_carreta", "ano_mes"], as_index=False)
    .agg(
        qtd_linhas_peca_mes=("id_linha_peca", "count"),
        qtd_linhas_peca_garantia_mes=("flag_peca_garantia", "sum"),
        custo_pecas_garantia_mes=("custo_peca_garantia_linha", "sum"),
    )
)
garantia_mes["prop_pecas_garantia"] = np.where(
    garantia_mes["qtd_linhas_peca_mes"] > 0,
    garantia_mes["qtd_linhas_peca_garantia_mes"] / garantia_mes["qtd_linhas_peca_mes"],
    np.nan,
)

os_preventivas_mes = (
    wo.loc[wo["id_os"].isin(preventive_os_ids)]
    .groupby(["id_carreta", "ano_mes"], as_index=False)
    .agg(n_os_preventivas_mes=("id_os", "nunique"))
)

labour_os_mix = (
    labour.groupby("id_os", as_index=False)
    .agg(
        tem_linha_preventiva=("flag_linha_preventiva", "any"),
        tem_linha_nao_preventiva=("flag_linha_preventiva", lambda s: bool((~s).any())),
        linhas_mao_obra=("flag_linha_preventiva", "size"),
    )
)
labour_os_mix["os_preventiva_mista"] = labour_os_mix["tem_linha_preventiva"] & labour_os_mix["tem_linha_nao_preventiva"]
os_preventivas_total = int(labour_os_mix["tem_linha_preventiva"].sum())
os_preventivas_mistas = int(labour_os_mix["os_preventiva_mista"].sum())
labour_os_mix.to_csv(TABLES / "02_os_preventivas_mistas.csv", index=False)

regiao_mes = (
    wo.groupby(["id_carreta", "ano_mes"], as_index=False)
    .agg(regiao_operacao=("regiao_operacao_evento", mode_or_unknown))
)

classificacao_preventiva = pd.DataFrame([
    {"metrica": "os_totais", "valor": wo["id_os"].nunique()},
    {"metrica": "os_com_linha_preventiva", "valor": len(preventive_os_ids)},
    {"metrica": "os_preventivas_mistas", "valor": os_preventivas_mistas},
    {"metrica": "share_os_preventivas_mistas", "valor": os_preventivas_mistas / os_preventivas_total if os_preventivas_total else np.nan},
    {"metrica": "linhas_mao_obra_preventiva", "valor": int(labour["flag_linha_preventiva"].sum())},
    {"metrica": "linhas_pecas_em_os_preventiva", "valor": int(parts["flag_os_preventiva"].sum())},
])
classificacao_preventiva.to_csv(TABLES / "02_classificacao_preventiva.csv", index=False)

custos_mes.head()
"""),
        md("### 3. Calcular quilometragem mensal prorrateada"),
        code("""
readings = readings.sort_values(["id_carreta", "data_leitura", "id_leitura"]).copy()
readings["km_anterior"] = readings.groupby("id_carreta")["km_acumulado"].shift(1)
readings["data_leitura_anterior"] = readings.groupby("id_carreta")["data_leitura"].shift(1)
readings["delta_km_bruto"] = readings["km_acumulado"] - readings["km_anterior"]

positive_delta = readings.loc[readings["delta_km_bruto"] >= 0, "delta_km_bruto"]
limite_delta_km = min(max(float(positive_delta.quantile(0.999)), 50000.0), 250000.0)
readings["delta_km_tratado"] = readings["delta_km_bruto"].where(
    (readings["delta_km_bruto"] >= 0) & (readings["delta_km_bruto"] <= limite_delta_km)
)

intervalos_validos = readings.dropna(subset=["data_leitura_anterior", "data_leitura", "delta_km_tratado"]).copy()
intervalos_validos = intervalos_validos[intervalos_validos["data_leitura"] > intervalos_validos["data_leitura_anterior"]]

allocations = []
for row in intervalos_validos[["id_carreta", "data_leitura_anterior", "data_leitura", "delta_km_tratado"]].itertuples(index=False):
    start = row.data_leitura_anterior
    end = row.data_leitura
    total_seconds = (end - start).total_seconds()
    if total_seconds <= 0:
        continue
    first_month = start.to_period("M").to_timestamp()
    last_month = end.to_period("M").to_timestamp()
    for mes in pd.date_range(first_month, last_month, freq="MS"):
        month_start_ts = mes
        month_end_ts = mes + pd.offsets.MonthBegin(1)
        overlap_start = max(start, month_start_ts)
        overlap_end = min(end, month_end_ts)
        overlap_seconds = max((overlap_end - overlap_start).total_seconds(), 0)
        if overlap_seconds > 0:
            allocations.append({
                "id_carreta": row.id_carreta,
                "ano_mes": mes,
                "km_rodado_mes": row.delta_km_tratado * overlap_seconds / total_seconds,
            })

km_alloc = pd.DataFrame(allocations)
km_mes = (
    km_alloc.groupby(["id_carreta", "ano_mes"], as_index=False)
    .agg(km_rodado_mes=("km_rodado_mes", "sum"))
    if len(km_alloc)
    else pd.DataFrame(columns=["id_carreta", "ano_mes", "km_rodado_mes"])
)

readings["ano_mes"] = month_start(readings["data_leitura"])
leituras_mes = (
    readings.groupby(["id_carreta", "ano_mes"], as_index=False)
    .agg(
        leituras_mes=("id_leitura", "count"),
        km_acumulado=("km_acumulado", "max"),
        leituras_com_reset=("km_reset_em", lambda s: int(s.notna().sum())),
    )
)
km_mes = km_mes.merge(leituras_mes, on=["id_carreta", "ano_mes"], how="outer")

diagnostico_km = pd.DataFrame([
    {"metrica": "limite_delta_km", "valor": limite_delta_km},
    {"metrica": "deltas_negativos_removidos", "valor": int((readings["delta_km_bruto"] < 0).sum())},
    {"metrica": "deltas_acima_limite_removidos", "valor": int((readings["delta_km_bruto"] > limite_delta_km).sum())},
    {"metrica": "intervalos_prorrateados", "valor": len(intervalos_validos)},
    {"metrica": "piso_km_para_alvo", "valor": KM_MIN_MES_ALVO},
])
diagnostico_km.to_csv(TABLES / "02_diagnostico_km.csv", index=False)
km_mes.head()
"""),
        md("## Results\n\n### 4. Montar grade mensal e enriquecer com ativos"),
        code("""
months = pd.date_range("2020-01-01", "2025-12-01", freq="MS")
grid = pd.MultiIndex.from_product(
    [dim["id_carreta"].sort_values().unique(), months],
    names=["id_carreta", "ano_mes"],
).to_frame(index=False)

base = (
    grid.merge(custos_mes, on=["id_carreta", "ano_mes"], how="left")
    .merge(mao_obra_preventiva_mes, on=["id_carreta", "ano_mes"], how="left")
    .merge(pecas_preventivas_mes, on=["id_carreta", "ano_mes"], how="left")
    .merge(os_preventivas_mes, on=["id_carreta", "ano_mes"], how="left")
    .merge(garantia_mes, on=["id_carreta", "ano_mes"], how="left")
    .merge(regiao_mes, on=["id_carreta", "ano_mes"], how="left")
    .merge(km_mes, on=["id_carreta", "ano_mes"], how="left")
)

for col in [
    "custo_mao_obra_mes", "custo_pecas_mes", "custo_total_mes", "n_os_mes",
    "custo_preventivo_mao_obra_mes", "custo_preventivo_pecas_mes", "n_os_preventivas_mes",
    "qtd_linhas_peca_mes", "qtd_linhas_peca_garantia_mes", "custo_pecas_garantia_mes",
]:
    base[col] = base[col].fillna(0)
base["custo_preventivo_total_mes"] = base["custo_preventivo_mao_obra_mes"] + base["custo_preventivo_pecas_mes"]
for col in ["km_rodado_mes", "leituras_mes", "leituras_com_reset"]:
    base[col] = base[col].fillna(0)
base["prop_pecas_garantia"] = np.where(
    base["qtd_linhas_peca_mes"] > 0,
    base["qtd_linhas_peca_garantia_mes"] / base["qtd_linhas_peca_mes"],
    np.nan,
)
base["regiao_operacao"] = base.groupby("id_carreta")["regiao_operacao"].ffill().fillna("SEM_INFORMACAO")

asset_cols = [
    "id_carreta", "cod_montadora", "cod_modelo", "ano_modelo", "data_entrada_servico",
    "eixos", "comprimento", "flag_refrigerado", "cod_classe", "classe",
    "cod_grupo_manutencao", "grupo_manutencao", "status_equipamento",
]
base = base.merge(dim[asset_cols], on="id_carreta", how="left")
base["idade_carreta"] = (base["ano_mes"] - base["data_entrada_servico"]).dt.days / 365.25
base["idade_carreta"] = base["idade_carreta"].clip(lower=0)

base.head()
"""),
        md("### 5. Enriquecer com contrato vigente"),
        code("""
contracts_clean = contracts.dropna(subset=["id_carreta", "data_inicio"]).copy()
contracts_clean = contracts_clean[
    (contracts_clean["data_inicio"] < ANALYSIS_END_EXCLUSIVE)
    & (contracts_clean["data_fim"].isna() | (contracts_clean["data_fim"] >= ANALYSIS_START))
].copy()
contracts_clean["inicio_mes"] = contracts_clean["data_inicio"].dt.to_period("M").dt.to_timestamp()
contracts_clean["fim_mes"] = contracts_clean["data_fim"].fillna(pd.Timestamp("2025-12-31")).dt.to_period("M").dt.to_timestamp()
contracts_clean["inicio_mes"] = contracts_clean["inicio_mes"].clip(lower=pd.Timestamp("2020-01-01"))
contracts_clean["fim_mes"] = contracts_clean["fim_mes"].clip(upper=pd.Timestamp("2025-12-01"))

expanded_contracts = []
for row in contracts_clean.itertuples(index=False):
    if pd.isna(row.inicio_mes) or pd.isna(row.fim_mes) or row.inicio_mes > row.fim_mes:
        continue
    fim_referencia = row.data_fim if pd.notna(row.data_fim) else ANALYSIS_END
    duracao_contrato_meses = max((fim_referencia - row.data_inicio).days / 30.4375, 0)
    for mes in pd.date_range(row.inicio_mes, row.fim_mes, freq="MS"):
        idade_contrato_meses_no_mes = max((mes - row.data_inicio).days / 30.4375, 0)
        expanded_contracts.append({
            "id_carreta": row.id_carreta,
            "ano_mes": mes,
            "tipo_contrato": row.tipo_contrato,
            "tipo_manutencao": row.tipo_manutencao,
            "id_cliente": row.id_cliente,
            "cod_cliente": row.cod_cliente,
            "franquia_km_mensal": row.franquia_km_mensal,
            "cod_local_contrato": row.cod_local_contrato,
            "data_inicio_contrato": row.data_inicio,
            "data_fim_contrato": row.data_fim,
            "duracao_contrato_meses": duracao_contrato_meses,
            "idade_contrato_meses_no_mes": idade_contrato_meses_no_mes,
        })

contracts_month = pd.DataFrame(expanded_contracts)
if len(contracts_month):
    contracts_month = (
        contracts_month.sort_values(["id_carreta", "ano_mes", "data_inicio_contrato"])
        .drop_duplicates(["id_carreta", "ano_mes"], keep="last")
    )
    base = base.merge(contracts_month, on=["id_carreta", "ano_mes"], how="left")
else:
    for col in [
        "tipo_contrato", "tipo_manutencao", "id_cliente", "cod_cliente", "franquia_km_mensal",
        "cod_local_contrato", "duracao_contrato_meses", "idade_contrato_meses_no_mes",
    ]:
        base[col] = np.nan

base[["id_carreta", "ano_mes", "tipo_contrato", "tipo_manutencao", "franquia_km_mensal"]].head()
"""),
        md("### 6. Criar alvo e features historicas sem vazamento temporal"),
        code("""
base = base.sort_values(["id_carreta", "ano_mes"]).copy()
base["km_valido_modelagem_flag"] = (base["km_rodado_mes"] >= KM_MIN_MES_ALVO).astype(int)
base["custo_manutencao_interno_por_km"] = np.where(
    base["km_valido_modelagem_flag"].eq(1),
    base["custo_total_mes"] / base["km_rodado_mes"],
    np.nan,
)
base["custo_manutencao_preventiva_por_km"] = np.where(
    base["km_valido_modelagem_flag"].eq(1),
    base["custo_preventivo_total_mes"] / base["km_rodado_mes"],
    np.nan,
)
base["custo_preventivo_mao_obra_por_km"] = np.where(
    base["km_valido_modelagem_flag"].eq(1),
    base["custo_preventivo_mao_obra_mes"] / base["km_rodado_mes"],
    np.nan,
)
base["teve_custo_interno_mes"] = (base["custo_total_mes"] != 0).astype(int)
base["teve_custo_preventivo_mes"] = (base["custo_preventivo_total_mes"] != 0).astype(int)
base["teve_custo_preventivo_mao_obra_mes"] = (base["custo_preventivo_mao_obra_mes"] != 0).astype(int)

grouped = base.groupby("id_carreta", group_keys=False)
base["custo_acum_manutencao"] = grouped["custo_total_mes"].cumsum() - base["custo_total_mes"]
base["custo_preventivo_acum"] = grouped["custo_preventivo_total_mes"].cumsum() - base["custo_preventivo_total_mes"]
base["n_os_acum"] = grouped["n_os_mes"].cumsum() - base["n_os_mes"]
base["n_os_preventivas_acum"] = grouped["n_os_preventivas_mes"].cumsum() - base["n_os_preventivas_mes"]
base["km_rodado_acum"] = grouped["km_rodado_mes"].cumsum() - base["km_rodado_mes"]
base["km_acumulado_fim_mes"] = grouped["km_acumulado"].ffill()
base["km_acumulado"] = base.groupby("id_carreta")["km_acumulado_fim_mes"].shift(1)

base["custo_medio_movel_3m"] = grouped["custo_total_mes"].transform(
    lambda s: s.shift(1).rolling(3, min_periods=1).mean()
)
base["custo_preventivo_medio_movel_3m"] = grouped["custo_preventivo_total_mes"].transform(
    lambda s: s.shift(1).rolling(3, min_periods=1).mean()
)

wo_sorted = wo.sort_values(["id_carreta", "data_os"]).copy()
wo_sorted["intervalo_dias_os"] = wo_sorted.groupby("id_carreta")["data_os"].diff().dt.days
intervalo_mes = (
    wo_sorted.groupby(["id_carreta", "ano_mes"], as_index=False)
    .agg(intervalo_medio_os_mes=("intervalo_dias_os", "mean"))
)
base = base.merge(intervalo_mes, on=["id_carreta", "ano_mes"], how="left")
base["intervalo_medio_os"] = base.groupby("id_carreta", group_keys=False)["intervalo_medio_os_mes"].transform(
    lambda s: s.expanding(min_periods=1).mean().shift(1)
)

def meses_desde_ultima_os(n_os: pd.Series) -> pd.Series:
    result = []
    last_idx = None
    for idx, value in enumerate(n_os.to_numpy()):
        result.append(np.nan if last_idx is None else idx - last_idx)
        if value > 0:
            last_idx = idx
    return pd.Series(result, index=n_os.index)

base["meses_desde_ultima_os"] = base.groupby("id_carreta", group_keys=False)["n_os_mes"].apply(meses_desde_ultima_os)
base["meses_desde_entrada_servico"] = ((base["ano_mes"] - base["data_entrada_servico"]).dt.days / 30.4375).clip(lower=0)
base["km_por_mes"] = base["km_rodado_acum"] / base["meses_desde_entrada_servico"].replace(0, np.nan)
base["contrato_vigente_flag"] = base["tipo_contrato"].notna().astype(int)
base["populacao_modelagem_principal_flag"] = (
    base["tipo_manutencao"].eq("MAINT")
    & base["km_valido_modelagem_flag"].eq(1)
    & base["custo_manutencao_preventiva_por_km"].notna()
).astype(int)

base.head()
"""),
        md("### 7. Validar e salvar base mensal"),
        code("""
validation = pd.DataFrame([
    {"checagem": "linhas_base", "valor": len(base)},
    {"checagem": "carretas", "valor": base["id_carreta"].nunique()},
    {"checagem": "meses", "valor": base["ano_mes"].nunique()},
    {"checagem": "km_rodado_mes_negativo", "valor": int((base["km_rodado_mes"] < 0).sum())},
    {"checagem": "alvo_interno_calculado_abaixo_piso_km", "valor": int(base.loc[base["km_rodado_mes"] < KM_MIN_MES_ALVO, "custo_manutencao_interno_por_km"].notna().sum())},
    {"checagem": "alvo_preventivo_calculado_abaixo_piso_km", "valor": int(base.loc[base["km_rodado_mes"] < KM_MIN_MES_ALVO, "custo_manutencao_preventiva_por_km"].notna().sum())},
    {"checagem": "alvo_mao_obra_preventiva_calculado_abaixo_piso_km", "valor": int(base.loc[base["km_rodado_mes"] < KM_MIN_MES_ALVO, "custo_preventivo_mao_obra_por_km"].notna().sum())},
    {"checagem": "observacoes_com_alvo_preventivo", "valor": int(base["custo_manutencao_preventiva_por_km"].notna().sum())},
    {"checagem": "observacoes_com_alvo_mao_obra_preventiva", "valor": int(base["custo_preventivo_mao_obra_por_km"].notna().sum())},
    {"checagem": "share_zero_preventivo_com_km_valido", "valor": float((base.loc[base["km_valido_modelagem_flag"].eq(1), "custo_preventivo_total_mes"] == 0).mean())},
    {"checagem": "meses_desde_ultima_os_zero", "valor": int(base["meses_desde_ultima_os"].eq(0).sum())},
    {"checagem": "km_acumulado_defasado_valores_validos", "valor": int(base["km_acumulado"].notna().sum())},
    {"checagem": "soma_custo_base", "valor": float(base["custo_total_mes"].sum())},
    {"checagem": "soma_custo_fato_wo_filtrado", "valor": float(wo["custo_total"].sum())},
    {"checagem": "soma_custo_preventivo", "valor": float(base["custo_preventivo_total_mes"].sum())},
])
validation.to_csv(TABLES / "02_validacao_base_mensal.csv", index=False)

base.to_csv(DATA_PROCESSED / "base_mensal_carreta.csv", index=False)

dicionario = pd.DataFrame([
    {"campo": "id_carreta", "descricao": "Identificador da carreta"},
    {"campo": "ano_mes", "descricao": "Mes de referencia da observacao"},
    {"campo": "custo_total_mes", "descricao": "Custo interno total de manutencao no mes"},
    {"campo": "custo_preventivo_total_mes", "descricao": "Custo preventivo aproximado: mao de obra VMRS PM/PREVENTIVE + pecas de OS preventiva"},
    {"campo": "custo_preventivo_mao_obra_mes", "descricao": "Custo de mao de obra preventiva atribuivel diretamente por linha VMRS PM/PREVENTIVE"},
    {"campo": "km_rodado_mes", "descricao": "Quilometragem mensal prorrateada a partir de intervalos entre leituras tratadas"},
    {"campo": "km_acumulado", "descricao": "Odometro acumulado defasado ate o mes anterior, para evitar uso de leitura do mes corrente"},
    {"campo": "km_acumulado_fim_mes", "descricao": "Odometro maximo observado no mes corrente; mantido para auditoria, nao usado como feature preditiva"},
    {"campo": "km_valido_modelagem_flag", "descricao": f"1 quando km_rodado_mes >= {KM_MIN_MES_ALVO:.0f}, piso usado para alvos por km"},
    {"campo": "custo_manutencao_preventiva_por_km", "descricao": "Variavel-alvo primaria nominal: custo_preventivo_total_mes / km_rodado_mes, com piso de km"},
    {"campo": "custo_preventivo_mao_obra_por_km", "descricao": "Alvo-espelho nominal mais limpo: mao de obra preventiva / km_rodado_mes, com piso de km"},
    {"campo": "custo_manutencao_interno_por_km", "descricao": "Alvo secundario nominal: custo_total_mes / km_rodado_mes, com piso de km"},
    {"campo": "custo_acum_manutencao", "descricao": "Custo historico acumulado ate o mes anterior"},
    {"campo": "custo_preventivo_acum", "descricao": "Custo preventivo historico acumulado ate o mes anterior"},
    {"campo": "n_os_acum", "descricao": "Quantidade historica de OS ate o mes anterior"},
    {"campo": "n_os_preventivas_acum", "descricao": "Quantidade historica de OS preventivas ate o mes anterior"},
    {"campo": "intervalo_medio_os", "descricao": "Intervalo medio historico entre OS, defasado"},
    {"campo": "duracao_contrato_meses", "descricao": "Duracao observada/esperada do contrato vigente em meses"},
    {"campo": "prop_pecas_garantia", "descricao": "Proporcao de linhas de pecas em garantia no mes"},
    {"campo": "regiao_operacao", "descricao": "Regiao aproximada por provincia/estado ou local da OS, carregada para frente por carreta"},
])
dicionario.to_csv(TABLES / "02_dicionario_base_mensal.csv", index=False)
validation
"""),
        md("""## Takeaways

- A base mensal foi salva em `data/processed/base_mensal_carreta.csv`.
- O alvo preventivo nominal e calculado apenas quando a quilometragem mensal atinge o piso metodologico.
- O alvo-espelho de mao de obra preventiva por km foi criado para avaliar separadamente a parte mais limpa do custo preventivo.
- A quilometragem mensal foi prorrateada entre meses-calendario, reduzindo vies por leituras irregulares.
- Features historicas acumuladas, odometro acumulado e meses desde ultima OS foram defasados para reduzir risco de vazamento temporal."""),
    ]


def notebook_03():
    return [
        md("""# 03 - Analise exploratoria e hipoteses

## tl;dr
Este notebook explora a distribuicao do custo por km, compara segmentos e avalia as hipoteses de negocio com correlacoes e evidencias descritivas."""),
        md("""## Context & Methods

A EDA deve orientar a modelagem e evitar conclusoes fortes sem evidencias. O foco e identificar padroes consistentes e variaveis candidatas.

### Key Assumptions
- A base mensal nominal ja foi gerada pelo notebook 02.
- O alvo primario da EDA e `custo_manutencao_preventiva_por_km`.
- Meses abaixo do piso de quilometragem nao entram na analise de custo por km.
- A EDA principal usa a populacao `MAINT`, alinhada ao notebook de modelagem.
- Hipoteses sobre custo por km sao lidas em duas partes: ocorrencia de custo e magnitude condicional nos meses positivos.
- Resultados exploratorios indicam associacoes, nao causalidade."""),
        code(COMMON_SETUP),
        md("## Data\n\n### 1. Carregar base mensal"),
        code("""
base_path = DATA_PROCESSED / "base_mensal_carreta.csv"
base = pd.read_csv(base_path, parse_dates=["ano_mes", "data_entrada_servico"], low_memory=False)

analise_todos = base.replace([np.inf, -np.inf], np.nan).copy()
target = "custo_manutencao_preventiva_por_km"
target_label = "Custo preventivo por km"
analise_todos = analise_todos[analise_todos[target].notna()].copy()
analise_todos = analise_todos[analise_todos["km_valido_modelagem_flag"].eq(1)].copy()
analise = analise_todos[analise_todos["tipo_manutencao"].eq("MAINT")].copy()
analise["ocorrencia_custo_preventivo"] = (analise["custo_preventivo_total_mes"] > 0).astype(int)
analise_positiva = analise[analise["ocorrencia_custo_preventivo"].eq(1)].copy()

pd.DataFrame([
    {"recorte": "todos_com_km_valido", "linhas": len(analise_todos), "share_zero": float((analise_todos["custo_preventivo_total_mes"] == 0).mean())},
    {"recorte": "MAINT_modelagem", "linhas": len(analise), "share_zero": float((analise["custo_preventivo_total_mes"] == 0).mean())},
    {"recorte": "MAINT_custo_positivo", "linhas": len(analise_positiva), "share_zero": 0.0},
])
"""),
        md("### 2. Preparar bibliotecas graficas"),
        code("""
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")
plt.rcParams["figure.figsize"] = (10, 5)
"""),
        md("## Results\n\n### 3. Distribuicao do custo por km"),
        code("""
distribution = analise[target].describe(percentiles=[0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]).to_frame("valor")
distribution.loc["assimetria"] = analise[target].skew()
distribution.loc["share_zero_preventivo"] = (analise["custo_preventivo_total_mes"] == 0).mean()
distribution.loc["km_minimo_alvo"] = KM_MIN_MES_ALVO
distribution.to_csv(TABLES / "03_distribuicao_custo_por_km.csv")
distribution
"""),
        code("""
p99 = analise[target].quantile(0.99)
fig, ax = plt.subplots()
sns.histplot(analise.loc[analise[target].between(0, p99), target], bins=60, ax=ax)
ax.set_title("Distribuicao do custo preventivo por km (ate p99)")
ax.set_xlabel(target_label)
ax.set_ylabel("Observacoes mensais")
fig.tight_layout()
fig.savefig(FIGURES / "03_distribuicao_custo_por_km.png", dpi=160)
plt.show()
"""),
        md("### 4. Evolucao temporal"),
        code("""
temporal = (
    analise.groupby("ano_mes", as_index=False)
    .agg(
        custo_por_km_medio=(target, "mean"),
        custo_por_km_mediano=(target, "median"),
        custo_por_km_mediano_positivo=(target, lambda s: s[s > 0].median()),
        taxa_ocorrencia=("ocorrencia_custo_preventivo", "mean"),
        km_total=("km_rodado_mes", "sum"),
        custo_preventivo_total=("custo_preventivo_total_mes", "sum"),
        custo_total=("custo_total_mes", "sum"),
        observacoes=("id_carreta", "count"),
    )
)
temporal.to_csv(TABLES / "03_evolucao_temporal.csv", index=False)

fig, ax = plt.subplots()
ax.plot(temporal["ano_mes"], temporal["custo_por_km_medio"], label="Media", alpha=0.7)
ax.plot(temporal["ano_mes"], temporal["custo_por_km_mediano_positivo"], label="Mediana condicional positiva", alpha=0.7)
ax.set_title("Evolucao mensal do custo preventivo por km - MAINT")
ax.set_xlabel("Mes")
ax.set_ylabel("Custo por km")
ax.legend()
fig.tight_layout()
fig.savefig(FIGURES / "03_evolucao_custo_por_km.png", dpi=160)
plt.show()
"""),
        md("### 5. Comparacoes por segmentos"),
        code("""
def segment_summary(col: str, min_obs: int = 100) -> pd.DataFrame:
    out = (
        analise.groupby(col, dropna=False)
        .agg(
            observacoes=(target, "count"),
            custo_por_km_mediano=(target, "median"),
            custo_por_km_mediano_positivo=(target, lambda s: s[s > 0].median()),
            custo_por_km_medio=(target, "mean"),
            taxa_ocorrencia=("ocorrencia_custo_preventivo", "mean"),
            km_mediano=("km_rodado_mes", "median"),
            custo_preventivo_total=("custo_preventivo_total_mes", "sum"),
            custo_total=("custo_total_mes", "sum"),
        )
        .reset_index()
    )
    return out[out["observacoes"] >= min_obs].sort_values("custo_por_km_medio", ascending=False)

segmentos = {}
for col in ["cod_montadora", "ano_modelo", "flag_refrigerado", "tipo_contrato", "cod_grupo_manutencao", "regiao_operacao"]:
    if col in analise.columns:
        segmentos[col] = segment_summary(col)
        segmentos[col].to_csv(TABLES / f"03_segmento_{col}.csv", index=False)

segmento_tipo_manutencao_todos = (
    analise_todos.groupby("tipo_manutencao", dropna=False)
    .agg(
        observacoes=(target, "count"),
        custo_por_km_medio=(target, "mean"),
        custo_por_km_mediano_positivo=(target, lambda s: s[s > 0].median()),
        taxa_ocorrencia=("custo_preventivo_total_mes", lambda s: float((s > 0).mean())),
        custo_preventivo_total=("custo_preventivo_total_mes", "sum"),
    )
    .reset_index()
)
segmento_tipo_manutencao_todos.to_csv(TABLES / "03_segmento_tipo_manutencao_todos.csv", index=False)

segmentos["cod_montadora"].head(10)
"""),
        code("""
top_makes = analise["cod_montadora"].value_counts().head(8).index
plot_data = analise[analise["cod_montadora"].isin(top_makes) & (analise[target] <= p99)].copy()

fig, ax = plt.subplots(figsize=(11, 5))
sns.boxplot(data=plot_data, x="cod_montadora", y=target, ax=ax, showfliers=False)
ax.set_title("Custo por km por montadora (top 8 em volume)")
ax.set_xlabel("Montadora")
ax.set_ylabel("Custo por km")
fig.tight_layout()
fig.savefig(FIGURES / "03_boxplot_montadora.png", dpi=160)
plt.show()
"""),
        md("### 6. Correlacoes Pearson e Spearman"),
        code("""
numeric_candidates = [
    "custo_manutencao_preventiva_por_km", "custo_manutencao_interno_por_km",
    "custo_preventivo_total_mes", "custo_total_mes", "km_rodado_mes",
    "idade_carreta", "km_rodado_acum", "custo_acum_manutencao", "custo_preventivo_acum",
    "n_os_acum", "n_os_preventivas_acum", "custo_medio_movel_3m", "custo_preventivo_medio_movel_3m",
    "intervalo_medio_os", "meses_desde_ultima_os", "franquia_km_mensal",
    "duracao_contrato_meses", "idade_contrato_meses_no_mes", "prop_pecas_garantia",
]
numeric_candidates = [c for c in numeric_candidates if c in analise.columns]
corr_pearson = analise[numeric_candidates].corr(method="pearson")
corr_spearman = analise[numeric_candidates].corr(method="spearman")
corr_spearman_positivos = analise_positiva[numeric_candidates].corr(method="spearman")
corr_ocorrencia = analise[numeric_candidates + ["ocorrencia_custo_preventivo"]].corr(method="spearman")["ocorrencia_custo_preventivo"].drop("ocorrencia_custo_preventivo")
corr_pearson.to_csv(TABLES / "03_correlacao_pearson.csv")
corr_spearman.to_csv(TABLES / "03_correlacao_spearman.csv")
corr_spearman_positivos.to_csv(TABLES / "03_correlacao_spearman_positivos.csv")
corr_ocorrencia.to_frame("spearman_ocorrencia").to_csv(TABLES / "03_correlacao_ocorrencia.csv")

fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(corr_spearman_positivos, cmap="coolwarm", center=0, annot=False, ax=ax)
ax.set_title("Correlacao de Spearman - meses MAINT com custo positivo")
fig.tight_layout()
fig.savefig(FIGURES / "03_correlacao_spearman.png", dpi=160)
plt.show()

pd.DataFrame({
    "spearman_base_maint": corr_spearman[target],
    "spearman_magnitude_positivos": corr_spearman_positivos[target],
    "spearman_ocorrencia": corr_ocorrencia,
}).sort_values("spearman_magnitude_positivos", key=lambda s: s.abs(), ascending=False)
"""),
        md("### 7. Componentes/sistemas VMRS"),
        code("""
labour = read_csv("fato_wo_labour", usecols=["ID_CARRETA", "DATA_OS", "COD_SISTEMA_VMRS", "SISTEMA_VMRS", "CUSTO_INTERNO_MAO_OBRA"])
labour["data_os"] = pd.to_datetime(labour["data_os"], errors="coerce")
labour = labour[labour["data_os"] < pd.Timestamp("2026-01-01")].copy()
labour["custo_interno_mao_obra"] = as_number(labour["custo_interno_mao_obra"]).fillna(0)

vmrs = (
    labour.groupby(["cod_sistema_vmrs", "sistema_vmrs"], dropna=False, as_index=False)
    .agg(custo_mao_obra=("custo_interno_mao_obra", "sum"), linhas=("custo_interno_mao_obra", "count"))
    .sort_values("custo_mao_obra", ascending=False)
)
vmrs["share_custo"] = vmrs["custo_mao_obra"] / vmrs["custo_mao_obra"].sum()
vmrs.to_csv(TABLES / "03_custo_por_sistema_vmrs.csv", index=False)
vmrs.head(15)
"""),
        md("### 8. Sintese das hipoteses"),
        code("""
def status_corr(value: float) -> str:
    if pd.isna(value):
        return "inconclusiva"
    if abs(value) >= 0.30:
        return "suportada"
    if abs(value) >= 0.10:
        return "parcialmente suportada"
    return "nao suportada nesta EDA"

def safe_ratio(series: pd.Series) -> float:
    values = pd.to_numeric(series, errors="coerce").replace(0, np.nan).dropna()
    if len(values) < 2:
        return np.nan
    min_value = values.min()
    return np.nan if min_value == 0 else values.max() / min_value

def occurrence_by_quantile(col: str, q: int = 5) -> pd.DataFrame:
    tmp = analise[[col, "ocorrencia_custo_preventivo"]].dropna().copy()
    if tmp[col].nunique() < 2:
        return pd.DataFrame(columns=["variavel", "faixa", "observacoes", "taxa_ocorrencia"])
    tmp["faixa"] = pd.qcut(tmp[col], q=q, duplicates="drop")
    out = (
        tmp.groupby("faixa", observed=True)
        .agg(
            observacoes=("ocorrencia_custo_preventivo", "count"),
            taxa_ocorrencia=("ocorrencia_custo_preventivo", "mean"),
        )
        .reset_index()
    )
    out.insert(0, "variavel", col)
    out["faixa"] = out["faixa"].astype(str)
    return out

def occurrence_spread(col: str) -> float:
    out = occurrence_by_quantile(col)
    if out.empty:
        return np.nan
    return float(out["taxa_ocorrencia"].max() - out["taxa_ocorrencia"].min())

ocorrencia_faixas = pd.concat(
    [occurrence_by_quantile(col) for col in ["idade_carreta", "km_rodado_mes", "duracao_contrato_meses", "custo_preventivo_acum"]],
    ignore_index=True,
)
ocorrencia_faixas.to_csv(TABLES / "03_ocorrencia_por_faixa.csv", index=False)

spearman_target = corr_spearman[target]
spearman_target_pos = corr_spearman_positivos[target]
spearman_preventive_cost = corr_spearman["custo_preventivo_total_mes"] if "custo_preventivo_total_mes" in corr_spearman.columns else pd.Series(dtype=float)
contrato_seg = segmentos.get("tipo_contrato", pd.DataFrame())
contrato_ratio = np.nan
if len(contrato_seg) >= 2:
    contrato_ratio = safe_ratio(contrato_seg["custo_por_km_medio"])
contrato_ratio_positivo = safe_ratio(contrato_seg["custo_por_km_mediano_positivo"]) if len(contrato_seg) >= 2 else np.nan
tipo_manutencao_seg = segmento_tipo_manutencao_todos
tipo_manutencao_ratio = np.nan
if len(tipo_manutencao_seg) >= 2:
    tipo_manutencao_ratio = safe_ratio(tipo_manutencao_seg["custo_por_km_medio"])

historico_features = [
    "custo_preventivo_acum",
    "n_os_preventivas_acum",
    "n_os_acum",
    "custo_preventivo_medio_movel_3m",
    "intervalo_medio_os",
    "meses_desde_ultima_os",
    "custo_acum_manutencao",
    "custo_medio_movel_3m",
]
historico_rows = []
for col in historico_features:
    historico_rows.append({
        "feature": col,
        "spearman_ocorrencia": corr_ocorrencia.get(col, np.nan),
        "spearman_magnitude_positiva": spearman_target_pos.get(col, np.nan),
    })
historico_proxies = pd.DataFrame(historico_rows)
historico_proxies["max_abs_spearman"] = historico_proxies[
    ["spearman_ocorrencia", "spearman_magnitude_positiva"]
].abs().max(axis=1)
historico_proxies = historico_proxies.sort_values("max_abs_spearman", ascending=False)
historico_proxies.to_csv(TABLES / "03_historico_manutencao_proxies.csv", index=False)
historico_max_abs = historico_proxies["max_abs_spearman"].max() if len(historico_proxies) else np.nan
historico_top_evidencia = "; ".join(
    [
        f"{row.feature}: ocorrencia={row.spearman_ocorrencia:.3f}, magnitude={row.spearman_magnitude_positiva:.3f}"
        for row in historico_proxies.head(4).itertuples()
    ]
)
historico_status = "parcialmente suportada" if pd.notna(historico_max_abs) and historico_max_abs >= 0.10 else "nao suportada nesta EDA"

vmrs_top5_share = vmrs.head(5)["share_custo"].sum() if len(vmrs) else np.nan

hipoteses = pd.DataFrame([
    {
        "hipotese": "Contratos de maior duracao tendem a maior custo por km",
        "evidencia": (
            f"Ocorrencia: Spearman = {corr_ocorrencia.get('duracao_contrato_meses', np.nan):.3f}; "
            f"magnitude positiva: Spearman duracao vs custo/km = {spearman_target_pos.get('duracao_contrato_meses', np.nan):.3f}"
        ),
        "status": status_corr(spearman_target_pos.get("duracao_contrato_meses", np.nan)),
    },
    {
        "hipotese": "Carretas mais antigas tendem a ter maior custo por km",
        "evidencia": (
            f"Ocorrencia: Spearman = {corr_ocorrencia.get('idade_carreta', np.nan):.3f}; "
            f"spread de taxa por quintil = {occurrence_spread('idade_carreta'):.3f}; "
            f"magnitude positiva: Spearman idade vs custo/km = {spearman_target_pos.get('idade_carreta', np.nan):.3f}"
        ),
        "status": status_corr(spearman_target_pos.get("idade_carreta", np.nan)),
    },
    {
        "hipotese": "Maior quilometragem mensal esta associada ao custo absoluto",
        "evidencia": (
            f"Spearman km_rodado_mes vs custo_preventivo_total_mes = {spearman_preventive_cost.get('km_rodado_mes', np.nan):.3f}; "
            f"ocorrencia = {corr_ocorrencia.get('km_rodado_mes', np.nan):.3f}; "
            f"custo/km positivo = {spearman_target_pos.get('km_rodado_mes', np.nan):.3f} (relacao mecanica com denominador)"
        ),
        "status": status_corr(spearman_preventive_cost.get("km_rodado_mes", np.nan)),
    },
    {
        "hipotese": "Historico de manutencoes ajuda a prever custo futuro",
        "evidencia": (
            f"Maior |Spearman| entre proxies historicos = {historico_max_abs:.3f}; "
            f"principais proxies: {historico_top_evidencia}"
        ),
        "status": historico_status,
    },
    {
        "hipotese": "Caracteristicas contratuais influenciam o custo",
        "evidencia": (
            f"Razao media por tipo_contrato em MAINT = {contrato_ratio:.2f}; "
            f"mediana positiva = {contrato_ratio_positivo:.2f}; "
            f"tipo_manutencao na base completa e caveat estrutural NET/MIX, nao tamanho de efeito ({tipo_manutencao_ratio:.2f})"
        ),
        "status": "parcialmente suportada" if any(pd.notna(v) and v >= 1.10 for v in [contrato_ratio, contrato_ratio_positivo]) else "inconclusiva",
    },
    {
        "hipotese": "Componentes/sistemas concentram parte relevante do custo",
        "evidencia": f"Top 5 sistemas VMRS representam {vmrs_top5_share:.1%} do custo de mao de obra",
        "status": "suportada" if pd.notna(vmrs_top5_share) and vmrs_top5_share >= 0.50 else "parcialmente suportada",
    },
])

hipoteses.to_csv(TABLES / "03_sintese_hipoteses.csv", index=False)
features_candidatas = pd.DataFrame({"feature": [
    "idade_carreta", "km_rodado_mes", "km_rodado_acum", "custo_acum_manutencao",
    "custo_preventivo_acum", "n_os_acum", "n_os_preventivas_acum",
    "custo_medio_movel_3m", "custo_preventivo_medio_movel_3m", "intervalo_medio_os",
    "cod_montadora", "cod_modelo", "flag_refrigerado", "tipo_contrato",
    "tipo_manutencao", "franquia_km_mensal", "duracao_contrato_meses",
    "regiao_operacao", "cod_grupo_manutencao",
]})
features_candidatas.to_csv(TABLES / "03_features_candidatas.csv", index=False)
hipoteses
"""),
        md("""## Takeaways

- A distribuicao do custo por km e zero-inflada e assimetrica, exigindo leitura separada de ocorrencia e magnitude.
- A EDA principal esta alinhada a populacao `MAINT`, usada na modelagem.
- As hipoteses devem ser interpretadas como evidencias associativas, nao causais.
- As variaveis mais promissoras seguem para a modelagem no notebook 05."""),
    ]


def notebook_04():
    return [
        md("""# 04 - Deflacao dos custos por IPCA

## tl;dr
Este notebook converte custos historicos nominais para valores de dezembro de 2025 usando IPCA mensal do SGS/BCB, serie 433."""),
        md("""## Context & Methods

A deflacao evita que inflacao historica seja confundida com aumento real de custo de manutencao.

### Key Assumptions
- Mes-base: `2025-12`.
- Fonte: Banco Central do Brasil, SGS serie 433, IPCA mensal em percentual.
- O fator aplicado e `indice_mes_base / indice_mes`."""),
        code(COMMON_SETUP),
        md("## Data\n\n### 1. Carregar base mensal e IPCA"),
        code("""
base = pd.read_csv(DATA_PROCESSED / "base_mensal_carreta.csv", parse_dates=["ano_mes"], low_memory=False)
ipca_path = DATA_RAW / "ipca_mensal_bcb_2020_2025.csv"
ipca = pd.read_csv(ipca_path, parse_dates=["ano_mes"])
ipca["ipca_pct"] = as_number(ipca["ipca_pct"])
ipca.head()
"""),
        md("### 2. Calcular indice acumulado e fator de correcao"),
        code("""
MES_BASE = pd.Timestamp("2025-12-01")
ipca = ipca.sort_values("ano_mes").copy()
ipca["indice_ipca"] = (1 + ipca["ipca_pct"] / 100).cumprod()
indice_base = float(ipca.loc[ipca["ano_mes"] == MES_BASE, "indice_ipca"].iloc[0])
ipca["fator_ipca_para_2025_12"] = indice_base / ipca["indice_ipca"]
ipca.to_csv(TABLES / "04_ipca_fatores.csv", index=False)
ipca.tail()
"""),
        md("## Results\n\n### 3. Aplicar deflacao aos custos"),
        code("""
base_defl = base.merge(ipca[["ano_mes", "ipca_pct", "indice_ipca", "fator_ipca_para_2025_12"]], on="ano_mes", how="left")

cost_cols = [
    "custo_total_mes", "custo_mao_obra_mes", "custo_pecas_mes",
    "custo_preventivo_total_mes", "custo_preventivo_mao_obra_mes", "custo_preventivo_pecas_mes",
]
for col in cost_cols:
    base_defl[f"{col}_deflacionado"] = base_defl[col] * base_defl["fator_ipca_para_2025_12"]

base_defl["custo_manutencao_interno_por_km_deflacionado"] = np.where(
    base_defl["km_valido_modelagem_flag"].eq(1),
    base_defl["custo_total_mes_deflacionado"] / base_defl["km_rodado_mes"],
    np.nan,
)
base_defl["custo_manutencao_preventiva_por_km_deflacionado"] = np.where(
    base_defl["km_valido_modelagem_flag"].eq(1),
    base_defl["custo_preventivo_total_mes_deflacionado"] / base_defl["km_rodado_mes"],
    np.nan,
)
base_defl["custo_preventivo_mao_obra_por_km_deflacionado"] = np.where(
    base_defl["km_valido_modelagem_flag"].eq(1),
    base_defl["custo_preventivo_mao_obra_mes_deflacionado"] / base_defl["km_rodado_mes"],
    np.nan,
)

base_defl.to_csv(DATA_PROCESSED / "base_mensal_carreta_deflacionada.csv", index=False)

validation = pd.DataFrame([
    {"checagem": "linhas", "valor": len(base_defl)},
    {"checagem": "meses_sem_ipca", "valor": int(base_defl["fator_ipca_para_2025_12"].isna().sum())},
    {"checagem": "alvo_preventivo_deflacionado_valido", "valor": int(base_defl["custo_manutencao_preventiva_por_km_deflacionado"].notna().sum())},
    {"checagem": "alvo_mao_obra_preventiva_deflacionado_valido", "valor": int(base_defl["custo_preventivo_mao_obra_por_km_deflacionado"].notna().sum())},
    {"checagem": "mes_base", "valor": MES_BASE.strftime("%Y-%m")},
    {"checagem": "fonte", "valor": "BCB SGS 433 - IPCA mensal"},
])
validation.to_csv(TABLES / "04_validacao_deflacao.csv", index=False)
validation
"""),
        md("### 4. Comparar custo por km nominal e deflacionado"),
        code("""
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")
compare = base_defl[
    ["ano_mes", "custo_manutencao_preventiva_por_km", "custo_manutencao_preventiva_por_km_deflacionado"]
].dropna()

summary = compare.describe(percentiles=[0.5, 0.95, 0.99]).T
summary.to_csv(TABLES / "04_comparacao_nominal_deflacionado.csv")
summary
"""),
        code("""
temporal = (
    compare.groupby("ano_mes", as_index=False)
    .agg(
        nominal=("custo_manutencao_preventiva_por_km", "median"),
        deflacionado=("custo_manutencao_preventiva_por_km_deflacionado", "median"),
    )
)

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(temporal["ano_mes"], temporal["nominal"], label="Nominal")
ax.plot(temporal["ano_mes"], temporal["deflacionado"], label="Deflacionado para 2025-12")
ax.set_title("Mediana mensal do custo preventivo por km: nominal vs deflacionado")
ax.set_xlabel("Mes")
ax.set_ylabel("Custo por km")
ax.legend()
fig.tight_layout()
fig.savefig(FIGURES / "04_nominal_vs_deflacionado.png", dpi=160)
plt.show()
"""),
        md("""## Takeaways

- A base deflacionada foi salva em `data/processed/base_mensal_carreta_deflacionada.csv`.
- A modelagem preditiva deve usar o alvo deflacionado como referencia principal.
- A deflacao permite interpretar variacoes de custo com menor contaminacao inflacionaria."""),
    ]


def notebook_05():
    return [
        md("""# 05 - Modelagem preditiva

## tl;dr
Este notebook treina modelos supervisionados para prever o custo preventivo de manutencao por km deflacionado, com populacao principal `MAINT` e separacao temporal entre treino e teste."""),
        md("""## Context & Methods

A modelagem busca comparar tecnicas estatisticas e de machine learning alinhadas ao projeto, preservando ordem temporal para reduzir vazamento.

### Key Assumptions
- Alvo principal: `custo_manutencao_preventiva_por_km_deflacionado`.
- Populacao principal: contratos `MAINT`, para reduzir confundimento de `NET/MIX`.
- Meses com custo preventivo zero sao mantidos, pois representam custo esperado mensal para orcamento.
- A distribuicao e zero-inflada; por isso, alem dos modelos diretos, sera avaliado um modelo em duas partes (hurdle).
- Sera reportado um alvo-espelho de mao de obra preventiva por km, mais limpo do ponto de vista de atribuicao VMRS.
- `km_rodado_mes` e mantido como feature operacional, mas interpretado com cautela porque tambem entra no denominador do alvo por km.
- `prop_pecas_garantia` fica fora da modelagem principal porque a base praticamente nao registra garantia.
- Teste temporal: ultimos 12 meses disponiveis.
- Observacoes com alvo negativo ou extremamente acima do p99,5 sao excluidas apenas do treino/teste de modelo."""),
        code(COMMON_SETUP),
        md("## Data\n\n### 1. Carregar base deflacionada"),
        code("""
base = pd.read_csv(DATA_PROCESSED / "base_mensal_carreta_deflacionada.csv", parse_dates=["ano_mes"], low_memory=False)
target = "custo_manutencao_preventiva_por_km_deflacionado"

model_data = base.replace([np.inf, -np.inf], np.nan).copy()
population_summary = (
    model_data.groupby("tipo_manutencao", dropna=False)
    .agg(
        observacoes=("id_carreta", "count"),
        obs_km_valido=("km_valido_modelagem_flag", "sum"),
        share_zero_preventivo=("custo_preventivo_total_mes", lambda s: float((s == 0).mean())),
    )
    .reset_index()
)
population_summary.to_csv(TABLES / "05_resumo_populacao_modelagem.csv", index=False)

model_data = model_data[
    model_data["tipo_manutencao"].eq("MAINT")
    & model_data["km_valido_modelagem_flag"].eq(1)
    & model_data[target].notna()
].copy()
model_data = model_data[model_data[target] >= 0].copy()
target_cap = model_data[target].quantile(0.995)
model_data = model_data[model_data[target] <= target_cap].copy()
model_data["teve_custo_preventivo"] = (model_data[target] > 0).astype(int)

model_data.shape, model_data["ano_mes"].min(), model_data["ano_mes"].max(), target_cap
"""),
        md("### 2. Definir features e separacao temporal"),
        code("""
numeric_features = [
    "idade_carreta", "km_rodado_mes", "km_rodado_acum", "km_acumulado",
    "custo_acum_manutencao", "custo_preventivo_acum", "n_os_acum", "n_os_preventivas_acum",
    "custo_medio_movel_3m", "custo_preventivo_medio_movel_3m", "intervalo_medio_os",
    "meses_desde_ultima_os", "km_por_mes", "franquia_km_mensal",
    "duracao_contrato_meses", "idade_contrato_meses_no_mes",
]
categorical_features = [
    "cod_montadora", "cod_modelo", "flag_refrigerado", "tipo_contrato",
    "cod_grupo_manutencao", "regiao_operacao",
]
numeric_features = [c for c in numeric_features if c in model_data.columns]
categorical_features = [c for c in categorical_features if c in model_data.columns]

features_removidas = pd.DataFrame([
    {
        "feature": "prop_pecas_garantia",
        "motivo": "quase sem variacao util: a base registra pouquissimas pecas em garantia; mantida apenas como diagnostico",
        "share_meses_modelagem_com_garantia": float(model_data.get("prop_pecas_garantia", pd.Series(dtype=float)).fillna(0).gt(0).mean()),
    }
])
features_removidas.to_csv(TABLES / "05_features_removidas_modelagem.csv", index=False)

test_start = model_data["ano_mes"].max() - pd.DateOffset(months=11)
train = model_data[model_data["ano_mes"] < test_start].copy()
test = model_data[model_data["ano_mes"] >= test_start].copy()

X_train = train[numeric_features + categorical_features]
y_train = train[target]
X_test = test[numeric_features + categorical_features]
y_test = test[target]

split_summary = pd.DataFrame([
    {"particao": "treino", "linhas": len(train), "inicio": train["ano_mes"].min(), "fim": train["ano_mes"].max(), "share_zero_preventivo": float((train[target] == 0).mean())},
    {"particao": "teste", "linhas": len(test), "inicio": test["ano_mes"].min(), "fim": test["ano_mes"].max(), "share_zero_preventivo": float((test[target] == 0).mean())},
])
split_summary.to_csv(TABLES / "05_particao_temporal.csv", index=False)
split_summary
"""),
        md("## Results\n\n### 3. Treinar e comparar modelos"),
        code("""
from sklearn.compose import ColumnTransformer
from sklearn.base import clone
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
)
from sklearn.neighbors import KNeighborsRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, PolynomialFeatures, StandardScaler
from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import LinearRegression, Ridge, SGDClassifier
from sklearn.compose import TransformedTargetRegressor
from sklearn.inspection import permutation_importance

numeric_scaled = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler()),
])
numeric_plain = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
])
categorical_pipe = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("onehot", OneHotEncoder(handle_unknown="infrequent_if_exist", min_frequency=100, sparse_output=True)),
])

preprocess_scaled = ColumnTransformer([
    ("num", numeric_scaled, numeric_features),
    ("cat", categorical_pipe, categorical_features),
])
preprocess_plain = ColumnTransformer([
    ("num", numeric_plain, numeric_features),
    ("cat", categorical_pipe, categorical_features),
])

simple_feature = ["km_rodado_mes"] if "km_rodado_mes" in numeric_features else numeric_features[:1]
preprocess_simple = ColumnTransformer([
    ("num", numeric_scaled, simple_feature),
])

models = {
    "regressao_linear_simples": Pipeline([("prep", preprocess_simple), ("model", LinearRegression())]),
    "regressao_linear_multipla": Pipeline([("prep", preprocess_scaled), ("model", LinearRegression())]),
    "ridge_multipla": Pipeline([("prep", preprocess_scaled), ("model", Ridge(alpha=10.0))]),
    "ridge_log1p": TransformedTargetRegressor(
        regressor=Pipeline([("prep", preprocess_scaled), ("model", Ridge(alpha=10.0))]),
        func=np.log1p,
        inverse_func=np.expm1,
    ),
    "regressao_polinomial_grau_2": Pipeline([
        ("prep", ColumnTransformer([("num", Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("poly", PolynomialFeatures(degree=2, include_bias=False)),
            ("scaler", StandardScaler()),
        ]), numeric_features[:6])])),
        ("model", LinearRegression()),
    ]),
    "arvore_decisao": Pipeline([("prep", preprocess_plain), ("model", DecisionTreeRegressor(max_depth=8, min_samples_leaf=50, random_state=42))]),
    "random_forest": Pipeline([("prep", preprocess_plain), ("model", RandomForestRegressor(n_estimators=30, min_samples_leaf=40, random_state=42, n_jobs=-1))]),
    "gradient_boosting": Pipeline([("prep", preprocess_plain), ("model", GradientBoostingRegressor(random_state=42, max_depth=3, n_estimators=70))]),
    "knn": Pipeline([("prep", preprocess_scaled), ("model", KNeighborsRegressor(n_neighbors=25, weights="distance"))]),
}

MAX_TREE_TRAIN_ROWS = 80000
MAX_KNN_TRAIN_ROWS = 30000
MAX_KNN_TEST_ROWS = 10000
SAMPLED_TRAINING_MODELS = {"arvore_decisao", "random_forest", "gradient_boosting"}
metrics = []
predictions = {}
for name, pipeline in models.items():
    if name == "knn":
        train_eval = train.sample(n=min(MAX_KNN_TRAIN_ROWS, len(train)), random_state=42)
        test_eval_sample = test.sample(n=min(MAX_KNN_TEST_ROWS, len(test)), random_state=42)
        x_train_fit = train_eval[numeric_features + categorical_features]
        y_train_fit = train_eval[target]
        x_test_eval = test_eval_sample[numeric_features + categorical_features]
        y_test_eval = test_eval_sample[target]
        avaliacao = "amostra_teste_temporal"
    elif name in SAMPLED_TRAINING_MODELS:
        train_eval = train.sample(n=min(MAX_TREE_TRAIN_ROWS, len(train)), random_state=42)
        x_train_fit = train_eval[numeric_features + categorical_features]
        y_train_fit = train_eval[target]
        x_test_eval = X_test
        y_test_eval = y_test
        avaliacao = "teste_temporal_completo"
    else:
        x_train_fit = X_train
        y_train_fit = y_train
        x_test_eval = X_test
        y_test_eval = y_test
        avaliacao = "teste_temporal_completo"
    pipeline.fit(x_train_fit, y_train_fit)
    pred = pipeline.predict(x_test_eval)
    if avaliacao == "teste_temporal_completo":
        predictions[name] = pred
    rmse = mean_squared_error(y_test_eval, pred) ** 0.5
    metrics.append({
        "modelo": name,
        "avaliacao": avaliacao,
        "elegivel_recomendacao": avaliacao == "teste_temporal_completo",
        "r2": r2_score(y_test_eval, pred),
        "rmse": rmse,
        "mae": mean_absolute_error(y_test_eval, pred),
    })

metrics = pd.DataFrame(metrics).sort_values("rmse")
metrics.to_csv(TABLES / "05_metricas_modelos.csv", index=False)
best_model_name = metrics.loc[metrics["elegivel_recomendacao"]].sort_values("rmse").iloc[0]["modelo"]
best_model = models[best_model_name] if best_model_name in models else None
best_model_is_direct_pipeline = best_model is not None
metrics
"""),
        md("### 4. Modelo em duas partes para distribuicao zero-inflada"),
        code("""
binary_target = "teve_custo_preventivo"
MAX_HURDLE_CLASSIFIER_ROWS = 120000
MAX_HURDLE_POSITIVE_ROWS = 60000

hurdle_classifier = Pipeline([
    ("prep", preprocess_scaled),
    ("model", SGDClassifier(
        loss="log_loss",
        class_weight="balanced",
        random_state=42,
        max_iter=1000,
        tol=1e-3,
    )),
])

classifier_train = train.sample(n=min(MAX_HURDLE_CLASSIFIER_ROWS, len(train)), random_state=42)
hurdle_classifier.fit(classifier_train[numeric_features + categorical_features], classifier_train[binary_target])
prob_positive = hurdle_classifier.predict_proba(X_test)[:, 1]
class_pred = (prob_positive >= 0.5).astype(int)
y_test_binary = test[binary_target].to_numpy()

classification_metrics = pd.DataFrame([{
    "modelo": "hurdle_sgd_classifier",
    "roc_auc": roc_auc_score(y_test_binary, prob_positive) if len(np.unique(y_test_binary)) > 1 else np.nan,
    "average_precision": average_precision_score(y_test_binary, prob_positive) if len(np.unique(y_test_binary)) > 1 else np.nan,
    "brier_score": brier_score_loss(y_test_binary, prob_positive),
    "precision_threshold_0_5": precision_score(y_test_binary, class_pred, zero_division=0),
    "recall_threshold_0_5": recall_score(y_test_binary, class_pred, zero_division=0),
    "f1_threshold_0_5": f1_score(y_test_binary, class_pred, zero_division=0),
    "share_positivo_teste": float(y_test_binary.mean()),
    "share_positivo_predito_0_5": float(class_pred.mean()),
}])

positive_train = train[train[target] > 0].copy()
positive_train_fit = positive_train.sample(n=min(MAX_HURDLE_POSITIVE_ROWS, len(positive_train)), random_state=42)
hurdle_positive_regressor = TransformedTargetRegressor(
    regressor=Pipeline([
        ("prep", preprocess_plain),
        ("model", GradientBoostingRegressor(random_state=42, max_depth=3, n_estimators=70)),
    ]),
    func=np.log1p,
    inverse_func=np.expm1,
)
hurdle_positive_regressor.fit(positive_train_fit[numeric_features + categorical_features], positive_train_fit[target])
positive_magnitude_pred = np.maximum(hurdle_positive_regressor.predict(X_test), 0)
hurdle_pred = prob_positive * positive_magnitude_pred

hurdle_row = {
    "modelo": "hurdle_sgd_gb",
    "avaliacao": "teste_temporal_completo",
    "elegivel_recomendacao": True,
    "r2": r2_score(y_test, hurdle_pred),
    "rmse": mean_squared_error(y_test, hurdle_pred) ** 0.5,
    "mae": mean_absolute_error(y_test, hurdle_pred),
}

predictions["hurdle_sgd_gb"] = hurdle_pred
metrics = (
    pd.concat([metrics, pd.DataFrame([hurdle_row])], ignore_index=True)
    .drop_duplicates(subset=["modelo"], keep="last")
    .sort_values("rmse")
)
metrics.to_csv(TABLES / "05_metricas_modelos.csv", index=False)
classification_metrics.to_csv(TABLES / "05_hurdle_classificacao.csv", index=False)
pd.DataFrame([hurdle_row]).to_csv(TABLES / "05_hurdle_metricas.csv", index=False)

best_model_name = metrics.loc[metrics["elegivel_recomendacao"]].sort_values("rmse").iloc[0]["modelo"]
best_model = models[best_model_name] if best_model_name in models else None
best_model_is_direct_pipeline = best_model is not None

pd.concat([
    classification_metrics,
    pd.DataFrame([{
        "modelo": "hurdle_sgd_gb",
        "roc_auc": np.nan,
        "average_precision": np.nan,
        "brier_score": np.nan,
        "precision_threshold_0_5": np.nan,
        "recall_threshold_0_5": np.nan,
        "f1_threshold_0_5": np.nan,
        "share_positivo_teste": float(y_test_binary.mean()),
        "share_positivo_predito_0_5": float(class_pred.mean()),
        "rmse_esperado": hurdle_row["rmse"],
        "mae_esperado": hurdle_row["mae"],
        "r2_esperado": hurdle_row["r2"],
    }])
], ignore_index=True)
"""),
        md("### 5. Alvo-espelho limpo: mao de obra preventiva por km"),
        code("""
mirror_target = "custo_preventivo_mao_obra_por_km_deflacionado"
mirror_rows = []

if mirror_target in model_data.columns:
    mirror_data = model_data[
        model_data[mirror_target].notna()
        & (model_data[mirror_target] >= 0)
    ].copy()
    mirror_cap = mirror_data[mirror_target].quantile(0.995)
    mirror_data = mirror_data[mirror_data[mirror_target] <= mirror_cap].copy()
    mirror_train = mirror_data[mirror_data["ano_mes"] < test_start].copy()
    mirror_test = mirror_data[mirror_data["ano_mes"] >= test_start].copy()

    mirror_train_fit = mirror_train.sample(n=min(MAX_TREE_TRAIN_ROWS, len(mirror_train)), random_state=42)
    mirror_model = clone(models["random_forest"])
    mirror_model.fit(
        mirror_train_fit[numeric_features + categorical_features],
        mirror_train_fit[mirror_target],
    )
    mirror_pred = mirror_model.predict(mirror_test[numeric_features + categorical_features])

    total_rf = metrics.loc[metrics["modelo"].eq("random_forest")].iloc[0]
    mirror_rows = [
        {
            "alvo": target,
            "descricao": "custo preventivo total por km: mao de obra preventiva + pecas de OS com linha preventiva",
            "modelo": "random_forest",
            "observacoes_teste": len(test),
            "share_zero_teste": float((test[target] == 0).mean()),
            "r2": total_rf["r2"],
            "rmse": total_rf["rmse"],
            "mae": total_rf["mae"],
        },
        {
            "alvo": mirror_target,
            "descricao": "alvo-espelho mais limpo: apenas mao de obra preventiva atribuivel por linha VMRS",
            "modelo": "random_forest",
            "observacoes_teste": len(mirror_test),
            "share_zero_teste": float((mirror_test[mirror_target] == 0).mean()),
            "r2": r2_score(mirror_test[mirror_target], mirror_pred),
            "rmse": mean_squared_error(mirror_test[mirror_target], mirror_pred) ** 0.5,
            "mae": mean_absolute_error(mirror_test[mirror_target], mirror_pred),
        },
    ]

alvo_espelho = pd.DataFrame(mirror_rows)
if len(alvo_espelho):
    alvo_espelho["delta_r2_vs_total"] = alvo_espelho["r2"] - alvo_espelho.loc[0, "r2"]
    alvo_espelho["delta_rmse_vs_total"] = alvo_espelho["rmse"] - alvo_espelho.loc[0, "rmse"]
alvo_espelho.to_csv(TABLES / "05_alvo_espelho_mao_obra.csv", index=False)
alvo_espelho
"""),
        md("### 6. Validacao temporal expansiva"),
        code("""
def temporal_folds(data: pd.DataFrame, min_train_months: int = 24, validation_months: int = 6, n_folds: int = 3):
    months = sorted(data["ano_mes"].dropna().unique())
    folds = []
    latest_validation_end = len(months) - 12
    candidate_ends = np.linspace(min_train_months, max(min_train_months + 1, latest_validation_end - validation_months), n_folds, dtype=int)
    for train_end in sorted(set(candidate_ends)):
        val_start = train_end
        val_end = min(train_end + validation_months, len(months))
        if val_end <= val_start or val_end > latest_validation_end:
            continue
        folds.append((months[:train_end], months[val_start:val_end]))
    return folds

cv_models = {name: models[name] for name in ["ridge_log1p", "arvore_decisao", "gradient_boosting"] if name in models}
cv_rows = []
for fold_idx, (train_months, val_months) in enumerate(temporal_folds(model_data), start=1):
    fold_train = model_data[model_data["ano_mes"].isin(train_months)]
    fold_val = model_data[model_data["ano_mes"].isin(val_months)]
    if len(fold_train) == 0 or len(fold_val) == 0:
        continue
    for name, pipeline in cv_models.items():
        fold_train_fit = fold_train.sample(n=min(50000, len(fold_train)), random_state=42) if name in SAMPLED_TRAINING_MODELS else fold_train
        fold_pipeline = clone(pipeline)
        fold_pipeline.fit(fold_train_fit[numeric_features + categorical_features], fold_train_fit[target])
        pred = fold_pipeline.predict(fold_val[numeric_features + categorical_features])
        cv_rows.append({
            "fold": fold_idx,
            "modelo": name,
            "treino_inicio": min(train_months),
            "treino_fim": max(train_months),
            "validacao_inicio": min(val_months),
            "validacao_fim": max(val_months),
            "r2": r2_score(fold_val[target], pred),
            "rmse": mean_squared_error(fold_val[target], pred) ** 0.5,
            "mae": mean_absolute_error(fold_val[target], pred),
        })

cv_metrics = pd.DataFrame(cv_rows)
cv_metrics.to_csv(TABLES / "05_validacao_temporal_expansiva.csv", index=False)
cv_metrics.groupby("modelo", as_index=False).agg(rmse_medio=("rmse", "mean"), mae_medio=("mae", "mean"), r2_medio=("r2", "mean")).sort_values("rmse_medio")
"""),
        md("### 7. Diagnosticar multicolinearidade numerica"),
        code("""
from sklearn.linear_model import LinearRegression as SkLinearRegression

vif_data = model_data[numeric_features].copy()
vif_sample = vif_data.sample(n=min(50000, len(vif_data)), random_state=42) if len(vif_data) else vif_data
vif_sample = pd.DataFrame(
    SimpleImputer(strategy="median").fit_transform(vif_sample),
    columns=numeric_features,
)

vif_rows = []
for feature in numeric_features:
    other_features = [c for c in numeric_features if c != feature]
    if not other_features:
        continue
    y_feature = vif_sample[feature]
    x_other = vif_sample[other_features]
    r2_feature = SkLinearRegression().fit(x_other, y_feature).score(x_other, y_feature)
    vif_rows.append({
        "feature": feature,
        "r2_explicado_pelas_demais": r2_feature,
        "vif_aproximado": np.inf if r2_feature >= 0.999999 else 1 / (1 - r2_feature),
    })

vif = pd.DataFrame(vif_rows).sort_values("vif_aproximado", ascending=False)
vif.to_csv(TABLES / "05_vif_features_numericas.csv", index=False)
vif.head(15)
"""),
        md("### 8. Interpretar importancia de variaveis"),
        code("""
rf = models["random_forest"]
rf_model = rf.named_steps["model"]
prep = rf.named_steps["prep"]

try:
    feature_names = prep.get_feature_names_out()
except Exception:
    feature_names = [f"feature_{i}" for i in range(len(rf_model.feature_importances_))]

importance = (
    pd.DataFrame({"feature": feature_names, "importancia": rf_model.feature_importances_})
    .sort_values("importancia", ascending=False)
)
importance.to_csv(TABLES / "05_importancia_variaveis_random_forest.csv", index=False)
perm_sample = test.sample(n=min(12000, len(test)), random_state=42)
perm = permutation_importance(
    rf,
    perm_sample[numeric_features + categorical_features],
    perm_sample[target],
    n_repeats=5,
    random_state=42,
    scoring="neg_mean_absolute_error",
    n_jobs=-1,
)
permutation_df = (
    pd.DataFrame({
        "feature": numeric_features + categorical_features,
        "importancia_permutacao_mae": perm.importances_mean,
        "importancia_permutacao_std": perm.importances_std,
    })
    .sort_values("importancia_permutacao_mae", ascending=False)
)
permutation_df.to_csv(TABLES / "05_importancia_permutacao_random_forest.csv", index=False)
importance.head(20)
"""),
        md("### 9. Diagnosticar erros por segmentos"),
        code("""
test_eval = test[["id_carreta", "ano_mes", "cod_montadora", "tipo_contrato", "regiao_operacao", "idade_carreta", target]].copy()
test_eval["predito"] = predictions[best_model_name]
test_eval["erro"] = test_eval["predito"] - test_eval[target]
test_eval["erro_abs"] = test_eval["erro"].abs()
test_eval["faixa_idade"] = pd.cut(test_eval["idade_carreta"], bins=[0, 3, 6, 10, 20, np.inf], include_lowest=True)

error_by_segment = []
for col in ["cod_montadora", "tipo_contrato", "regiao_operacao", "faixa_idade"]:
    if col in test_eval.columns:
        seg = (
            test_eval.groupby(col, dropna=False)
            .agg(observacoes=("erro_abs", "count"), mae=("erro_abs", "mean"), vies=("erro", "mean"))
            .reset_index()
        )
        seg["segmento"] = col
        seg = seg.rename(columns={col: "valor_segmento"})
        error_by_segment.append(seg)

error_by_segment = pd.concat(error_by_segment, ignore_index=True)
error_by_segment.to_csv(TABLES / "05_erro_por_segmento.csv", index=False)

best_row = metrics.loc[metrics["modelo"].eq(best_model_name)].iloc[0]
recommendation = pd.DataFrame([{
    "modelo_recomendado": best_model_name,
    "criterio": "menor RMSE no conjunto de teste temporal da populacao MAINT",
    "alvo": target,
    "populacao": "tipo_manutencao = MAINT; km_rodado_mes >= piso metodologico",
    "pipeline_direto_disponivel": best_model_is_direct_pipeline,
    "rmse": best_row["rmse"],
    "mae": best_row["mae"],
    "r2": best_row["r2"],
}])
recommendation.to_csv(TABLES / "05_modelo_recomendado.csv", index=False)

recommendation
"""),
        md("""## Takeaways

- A comparacao de modelos esta salva em `reports/tables/05_metricas_modelos.csv`.
- O modelo recomendado e definido por menor RMSE no teste temporal da populacao `MAINT`.
- O modelo hurdle explicita a natureza zero-inflada: primeiro estima ocorrencia de custo, depois magnitude condicional. O classificador de ocorrencia deve ser interpretado como achado operacional, mesmo quando a previsao esperada nao vence em RMSE.
- O alvo-espelho de mao de obra preventiva por km testa se a parte mais limpa do custo e mais previsivel do que o alvo total com pecas alocadas no nivel da OS.
- A validacao temporal expansiva, o VIF e a permutation importance ficam salvos para auditoria metodologica.
- `prop_pecas_garantia` foi removida da modelagem principal por baixa variacao observada.
- Mixed-Effects Random Forest/MERF fica como extensao futura para tratar explicitamente efeito-carreta."""),
    ]


def notebook_06():
    return [
        md("""# 06 - Resultados e recomendacoes

## tl;dr
Este notebook consolida os achados finais para uso no TCC/apresentacao: resposta ao problema, fatores relevantes, desempenho preditivo, limitacoes e recomendacoes de negocio."""),
        md("""## Context & Methods

Este e um notebook de sintese. Ele consome as tabelas geradas pelos notebooks anteriores e produz uma narrativa executiva.

### Key Assumptions
- Os notebooks 02 a 05 ja foram executados.
- As recomendacoes sao condicionadas a qualidade dos dados e ao desempenho observado no teste temporal."""),
        code(COMMON_SETUP),
        md("## Data\n\n### 1. Carregar insumos consolidados"),
        code("""
base = pd.read_csv(DATA_PROCESSED / "base_mensal_carreta_deflacionada.csv", parse_dates=["ano_mes"], low_memory=False)
metricas = pd.read_csv(TABLES / "05_metricas_modelos.csv")
modelo_recomendado = pd.read_csv(TABLES / "05_modelo_recomendado.csv")
importancia = pd.read_csv(TABLES / "05_importancia_variaveis_random_forest.csv")
importancia_permutacao = pd.read_csv(TABLES / "05_importancia_permutacao_random_forest.csv") if (TABLES / "05_importancia_permutacao_random_forest.csv").exists() else pd.DataFrame()
hipoteses = pd.read_csv(TABLES / "03_sintese_hipoteses.csv")
distribuicao = pd.read_csv(TABLES / "03_distribuicao_custo_por_km.csv", index_col=0)
hurdle_classificacao = pd.read_csv(TABLES / "05_hurdle_classificacao.csv") if (TABLES / "05_hurdle_classificacao.csv").exists() else pd.DataFrame()
alvo_espelho = pd.read_csv(TABLES / "05_alvo_espelho_mao_obra.csv") if (TABLES / "05_alvo_espelho_mao_obra.csv").exists() else pd.DataFrame()
classificacao_preventiva = pd.read_csv(TABLES / "02_classificacao_preventiva.csv")
"""),
        md("## Results\n\n### 2. Resposta sintetica ao problema"),
        code("""
alvo = "custo_manutencao_preventiva_por_km_deflacionado"
base_modelo = base[
    base["tipo_manutencao"].eq("MAINT")
    & base["km_valido_modelagem_flag"].eq(1)
    & base[alvo].notna()
].copy()

hurdle_auc = float(hurdle_classificacao.iloc[0]["roc_auc"]) if len(hurdle_classificacao) else np.nan
hurdle_avg_precision = float(hurdle_classificacao.iloc[0]["average_precision"]) if len(hurdle_classificacao) else np.nan
alvo_espelho_r2 = np.nan
if len(alvo_espelho) and "custo_preventivo_mao_obra_por_km_deflacionado" in set(alvo_espelho["alvo"]):
    alvo_espelho_r2 = float(alvo_espelho.loc[
        alvo_espelho["alvo"].eq("custo_preventivo_mao_obra_por_km_deflacionado"),
        "r2",
    ].iloc[0])

resumo_numerico = pd.DataFrame([
    {"indicador": "carretas na base", "valor": base["id_carreta"].nunique()},
    {"indicador": "observacoes mensais", "valor": len(base)},
    {"indicador": "observacoes MAINT com alvo preventivo valido", "valor": len(base_modelo)},
    {"indicador": "share zero preventivo na populacao modelada", "valor": float((base_modelo["custo_preventivo_total_mes"] == 0).mean())},
    {"indicador": "custo preventivo/km deflacionado mediano", "valor": base_modelo[alvo].median()},
    {"indicador": "custo preventivo/km deflacionado medio", "valor": base_modelo[alvo].mean()},
    {"indicador": "modelo recomendado", "valor": modelo_recomendado.loc[0, "modelo_recomendado"]},
    {"indicador": "RMSE teste", "valor": modelo_recomendado.loc[0, "rmse"]},
    {"indicador": "MAE teste", "valor": modelo_recomendado.loc[0, "mae"]},
    {"indicador": "AUC hurdle ocorrencia", "valor": hurdle_auc},
    {"indicador": "average precision hurdle ocorrencia", "valor": hurdle_avg_precision},
    {"indicador": "R2 alvo espelho mao obra", "valor": alvo_espelho_r2},
])
resumo_numerico.to_csv(TABLES / "06_resumo_numerico_final.csv", index=False)
resumo_numerico
"""),
        md("### 3. Fatores mais relevantes"),
        code("""
if len(importancia_permutacao):
    top_features = (
        importancia_permutacao.head(15)
        .rename(columns={"importancia_permutacao_mae": "importancia"})
        [["feature", "importancia", "importancia_permutacao_std"]]
        .copy()
    )
    top_features["metodo"] = "permutation_importance_mae"
else:
    top_features = importancia.head(15).copy()
    top_features["metodo"] = "importancia_impureza_random_forest"
top_features.to_csv(TABLES / "06_top_fatores_modelo.csv", index=False)
top_features
"""),
        md("### 4. Hipoteses: evidencias e status"),
        code("""
hipoteses.to_csv(TABLES / "06_hipoteses_final.csv", index=False)
hipoteses
"""),
        md("### 5. Recomendacoes de negocio"),
        code("""
recomendacoes = pd.DataFrame([
    {
        "tema": "orcamento de manutencao",
        "recomendacao": "usar previsao mensal por carreta como apoio ao planejamento financeiro, comunicando desempenho preditivo modesto e alta proporcao de meses sem custo",
    },
    {
        "tema": "zero-inflacao",
        "recomendacao": "usar a probabilidade de ocorrencia do hurdle como sinal complementar de priorizacao, comunicando que o desempenho e moderado apos remover vazamento temporal",
    },
    {
        "tema": "gestao de frota",
        "recomendacao": "monitorar perfis com maior probabilidade prevista de custo preventivo e maior erro historico, usando os fatores recalculados do modelo como priorizacao",
    },
    {
        "tema": "contratos",
        "recomendacao": "comparar custo preventivo previsto por km com franquia, duracao e tipo de contrato; tratar NET/MIX separadamente de MAINT",
    },
    {
        "tema": "manutencao preventiva",
        "recomendacao": "priorizar investigacao dos sistemas VMRS com maior concentracao de custo de mao de obra",
    },
    {
        "tema": "dados",
        "recomendacao": "preservar no extrato o vinculo peca-linha de mao de obra para reduzir ruido nas pecas preventivas; ampliar cobertura historica de GPS",
    },
    {
        "tema": "modelagem futura",
        "recomendacao": "avaliar Mixed-Effects Random Forest/MERF, modelos hierarquicos e alternativas zero-infladas para representar efeito-carreta e ocorrencia de custo",
    },
])
recomendacoes.to_csv(TABLES / "06_recomendacoes_negocio.csv", index=False)
recomendacoes
"""),
        md("### 6. Gerar sumario executivo em Markdown"),
        code(r'''
best = modelo_recomendado.iloc[0]
feature_lines = "\n".join([f"- {row.feature}: {row.importancia:.4f}" for row in top_features.head(8).itertuples()])
hypothesis_lines = "\n".join([f"- {row.hipotese}: {row.status} ({row.evidencia})" for row in hipoteses.itertuples()])
recommendation_lines = "\n".join([f"- {row.tema}: {row.recomendacao}" for row in recomendacoes.itertuples()])
resumo_final = dict(zip(resumo_numerico["indicador"], resumo_numerico["valor"]))
zero_share = float(resumo_final.get("share zero preventivo na populacao modelada", np.nan))
mixed_lookup = dict(zip(classificacao_preventiva["metrica"], classificacao_preventiva["valor"]))
share_os_mistas = float(mixed_lookup.get("share_os_preventivas_mistas", np.nan))
hurdle_lines = ""
if len(hurdle_classificacao):
    hurdle = hurdle_classificacao.iloc[0]
    hurdle_expected = metricas.loc[metricas["modelo"].eq("hurdle_sgd_gb")]
    hurdle_expected_line = ""
    if len(hurdle_expected):
        hurdle_expected_line = f"- Hurdle RMSE da previsao esperada: {hurdle_expected.iloc[0]['rmse']:.4f}\n"
    hurdle_lines = f"""
- Hurdle ROC AUC para ocorrencia de custo: {hurdle.get('roc_auc', np.nan):.4f}
- Hurdle average precision: {hurdle.get('average_precision', np.nan):.4f}
- Hurdle Brier score: {hurdle.get('brier_score', np.nan):.4f}
{hurdle_expected_line}"""

mirror_lines = ""
mirror_interpretation = ""
if len(alvo_espelho):
    total_row = alvo_espelho.iloc[0]
    mirror_candidates = alvo_espelho[alvo_espelho["alvo"].eq("custo_preventivo_mao_obra_por_km_deflacionado")]
    if len(mirror_candidates):
        mirror_row = mirror_candidates.iloc[0]
        delta_r2_mirror = mirror_row["r2"] - total_row["r2"]
        if delta_r2_mirror >= 0.05:
            mirror_interpretation = "o ganho de R2 no alvo de mao de obra preventiva indica de forma mais robusta que parte da perda de qualidade no alvo total pode vir da alocacao ruidosa de pecas no nivel da OS. A queda de RMSE e ilustrativa, mas parcialmente mecanica pela diferenca de escala."
        elif delta_r2_mirror > 0:
            mirror_interpretation = f"o alvo de mao de obra preventiva e apenas marginalmente mais previsivel (delta R2 = {delta_r2_mirror:.3f}); isso e sugestivo, mas nao conclusivo, de ruido adicional nas pecas alocadas no nivel da OS. A queda de RMSE e ilustrativa, mas parcialmente mecanica pela diferenca de escala."
        else:
            mirror_interpretation = "o alvo de mao de obra preventiva nao superou o alvo preventivo total em R2; isso indica que a dificuldade de magnitude nao vem apenas da alocacao de pecas, embora essa continue sendo uma limitacao importante."
        mirror_lines = f"""
## Alvo-espelho: mao de obra preventiva

A mao de obra preventiva e a parcela mais limpa do alvo, porque e atribuida diretamente por linha VMRS. As pecas seguem alocadas no nivel da OS, o que gera ruido quando a OS mistura tarefas preventivas e nao preventivas.

A comparacao entre alvos deve ser sustentada principalmente pelo R2, que e adimensional. O RMSE e o MAE sao reportados como contexto, mas nao devem ser interpretados como ganho proporcional, pois o alvo de mao de obra tem escala menor que o alvo total com pecas.

- Alvo preventivo total por km - Random Forest: R2 = {total_row['r2']:.4f}; RMSE = {total_row['rmse']:.4f}; MAE = {total_row['mae']:.4f}
- Alvo apenas mao de obra preventiva por km - Random Forest: R2 = {mirror_row['r2']:.4f}; RMSE = {mirror_row['rmse']:.4f}; MAE = {mirror_row['mae']:.4f}
- Interpretacao: {mirror_interpretation}
"""

summary_md = f"""# Sumario executivo - Projeto Quatro Norte

## Resposta ao problema

Os custos preventivos de manutencao por km foram aproximados de forma reprodutivel no grao carreta x mes, usando linhas VMRS PM/PREVENTIVE e pecas de OS com linha preventiva. A identificacao de fatores e mais forte do que a capacidade preditiva pura: a base e zero-inflada, com {zero_share:.1%} dos meses modelados sem custo preventivo, e parte do alvo tem erro de medicao por OS mistas.

O principal achado metodologico e que o problema se divide em duas partes: ocorrencia de custo e magnitude condicional. Depois de remover vazamento temporal, a ocorrencia deixa de parecer quase deterministica e passa a mostrar sinal preditivo moderado; a magnitude do custo por km permanece mais ruidosa. Assim, o R2 baixo do modelo direto deve ser lido como evidencia da dificuldade de estimar valor, nao como ausencia completa de sinal operacional.

## Desempenho preditivo

- Modelo recomendado: {best['modelo_recomendado']}
- Criterio: {best['criterio']}
- Alvo: {best['alvo']}
- Populacao: {best['populacao']}
- RMSE no teste temporal: {best['rmse']:.4f}
- MAE no teste temporal: {best['mae']:.4f}
- R2 no teste temporal: {best['r2']:.4f}
{hurdle_lines}
O hurdle nao venceu a Random Forest no RMSE da previsao esperada. Ainda assim, ele ajuda a explicar a natureza do problema: existe algum sinal para estimar a ocorrencia de custo, mas a previsao da magnitude continua sendo o componente mais instavel.

{mirror_lines}

## Principais fatores do modelo

O ranking abaixo vem da Random Forest interpretativa, priorizando permutation importance no teste temporal quando disponivel. Ele deve ser lido **dentro da populacao MAINT**, nao como ranking global de toda a frota. O efeito de `tipo_manutencao` deve ser interpretado na EDA comparativa, pois a modelagem principal fixa essa populacao para reduzir confundimento.

{feature_lines}

## Hipoteses avaliadas

{hypothesis_lines}

## Recomendacoes

{recommendation_lines}

## Limitacoes

- GPS tem cobertura parcial, concentrada no fim de 2025.
- A manutencao preventiva e uma aproximacao por VMRS PM/PREVENTIVE; a mao de obra e atribuivel por linha, mas pecas foram alocadas no nivel da OS porque o CSV nao traz o vinculo da peca com a linha de mao de obra.
- Entre OS com linha preventiva, {share_os_mistas:.1%} tambem possuem linhas nao-preventivas, sinalizando ruido de medicao no alvo preventivo.
- A distribuicao e zero-inflada; o modelo direto tem desempenho preditivo modesto e o hurdle mostra sinal moderado para prever ocorrencia de custo.
- A base praticamente nao registra pecas em garantia; por isso `prop_pecas_garantia` foi mantida como diagnostico, mas retirada da modelagem principal.
- NET/MIX foram tratados como caveat/segmento; a modelagem principal usa MAINT.
- Meses com baixa quilometragem foram excluidos dos alvos por km pelo piso metodologico de {KM_MIN_MES_ALVO:.0f} km/mes.
- Custos negativos podem representar estornos ou ajustes contabeis.
- O modelo deve ser usado como apoio a decisao, nao como substituto de validacao operacional.
- MERF/modelos hierarquicos sao uma extensao recomendada para tratar explicitamente o efeito individual de cada carreta.
"""

(REPORTS / "sumario_executivo.md").write_text(summary_md, encoding="utf-8")
print(summary_md)
'''),
        md("""## Takeaways

- O projeto passa a ter uma trilha completa: inventario, qualidade, base mensal, EDA, deflacao, modelagem e recomendacoes.
- A resposta final combina evidencia estatistica, desempenho preditivo e interpretabilidade de negocio.
- O arquivo `reports/sumario_executivo.md` pode ser reaproveitado na entrega academica."""),
    ]


def main():
    NOTEBOOKS.mkdir(parents=True, exist_ok=True)
    (ROOT / "reports" / "figures").mkdir(parents=True, exist_ok=True)
    (ROOT / "reports" / "tables").mkdir(parents=True, exist_ok=True)
    (ROOT / ".cache" / "matplotlib").mkdir(parents=True, exist_ok=True)

    ipca = pd.DataFrame(IPCA_2020_2025, columns=["ano_mes", "ipca_pct"])
    ipca["fonte"] = "Banco Central do Brasil - SGS serie 433"
    ipca["consulta"] = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados"
    ipca.to_csv(RAW / "ipca_mensal_bcb_2020_2025.csv", index=False)

    notebooks = {
        "00_contexto_inventario_dados.ipynb": notebook_00(),
        "01_qualidade_integridade_dados.ipynb": notebook_01(),
        "02_base_analitica_mensal.ipynb": notebook_02(),
        "03_analise_exploratoria_hipoteses.ipynb": notebook_03(),
        "04_deflacao_custos_ipca.ipynb": notebook_04(),
        "05_modelagem_preditiva.ipynb": notebook_05(),
        "06_resultados_recomendacoes.ipynb": notebook_06(),
    }
    for filename, cells in notebooks.items():
        write_notebook(NOTEBOOKS / filename, cells)
        print(f"wrote {NOTEBOOKS / filename}")


if __name__ == "__main__":
    main()
