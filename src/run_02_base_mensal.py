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

# %% -----

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

# %% -----

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

# %% -----

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

# %% -----

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

# %% -----

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

# %% -----

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

# %% -----

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