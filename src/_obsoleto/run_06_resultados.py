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

# %% -----

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

# %% -----

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

# %% -----

hipoteses.to_csv(TABLES / "06_hipoteses_final.csv", index=False)
hipoteses

# %% -----

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

# %% -----

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