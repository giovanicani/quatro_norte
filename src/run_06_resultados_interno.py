# 06 - Resultados e recomendacoes (trilha vigente: alvo interno total + CPI Canada)
# Regenera as tabelas 06_* a partir dos artefatos atuais de 03b/03c/05.
# O sumario executivo (reports/sumario_executivo.md) e mantido manualmente.
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path.cwd()
if PROJECT_ROOT.name in ("notebooks", "src"):
    PROJECT_ROOT = PROJECT_ROOT.parent
TABLES = PROJECT_ROOT / "reports" / "tables"

ALVO = "custo_manutencao_interno_por_km_deflacionado"

stats = pd.read_csv(TABLES / "03c_stats_ppt.csv", index_col=0)["valor"]
rec = pd.read_csv(TABLES / "05_modelo_recomendado.csv").iloc[0]
metricas = pd.read_csv(TABLES / "05_metricas_modelos.csv")
perm = pd.read_csv(TABLES / "05_importancia_permutacao_random_forest.csv")

resumo = pd.DataFrame([
    {"indicador": "alvo", "valor": ALVO},
    {"indicador": "deflator", "valor": "CPI all-items Canada (StatCan v41690973), base 2025-12"},
    {"indicador": "populacao", "valor": "tipo_manutencao = MAINT; km_rodado_mes >= 500"},
    {"indicador": "observacoes_alvo_valido", "valor": int(stats["obs_y_valido"])},
    {"indicador": "share_meses_custo_zero", "valor": round(float(stats["share_y_zero"]), 4)},
    {"indicador": "custo_interno_nominal_cad", "valor": round(float(stats["custo_total_nominal"]), 2)},
    {"indicador": "custo_interno_deflacionado_cad", "valor": round(float(stats["custo_total_deflacionado"]), 2)},
    {"indicador": "modelo_recomendado", "valor": rec["modelo_recomendado"]},
    {"indicador": "r2_teste_temporal", "valor": round(float(rec["r2"]), 4)},
    {"indicador": "rmse_teste_temporal", "valor": round(float(rec["rmse"]), 4)},
    {"indicador": "mae_teste_temporal", "valor": round(float(rec["mae"]), 4)},
])
resumo.to_csv(TABLES / "06_resumo_numerico_final.csv", index=False)

top = perm.nlargest(15, "importancia_permutacao_mae").rename(
    columns={"importancia_permutacao_mae": "importancia"})
top["fonte"] = "permutation importance (teste temporal, Random Forest)"
top.to_csv(TABLES / "06_top_fatores_modelo.csv", index=False)

hipoteses = pd.DataFrame([
    {"hipotese": "H1 duracao de contrato => custo", "status": "nao suportada",
     "evidencia": "Spearman duracao_contrato_meses vs Y = +0,02"},
    {"hipotese": "H2 idade => custo", "status": "parcialmente suportada",
     "evidencia": "efeito direto fraco (+0,04); idade opera via historico acumulado (km_acumulado, n_os_acum)"},
    {"hipotese": "H3 quilometragem => custo", "status": "parcialmente suportada",
     "evidencia": "km_acumulado +0,16; km mensal tem relacao mecanica com o denominador do alvo"},
    {"hipotese": "H4 historico preve custo futuro", "status": "suportada",
     "evidencia": "n_os_acum +0,22; custo_acum_manutencao +0,20; intervalo_medio_os -0,19"},
    {"hipotese": "H5 operacao/contrato influenciam", "status": "parcialmente suportada",
     "evidencia": "regiao eta 0,084; montadora 0,068; reefer 0,063; efeito contratual fraco"},
])
hipoteses.to_csv(TABLES / "06_hipoteses_final.csv", index=False)

recom = pd.DataFrame([
    {"area": "orcamento", "recomendacao": "usar previsao mensal por carreta como apoio, comunicando desempenho moderado e alta proporcao de meses sem custo"},
    {"area": "priorizacao de frota", "recomendacao": "monitorar carretas com maior historico de OS e menor intervalo entre manutencoes"},
    {"area": "contratos", "recomendacao": "precificar pelo perfil operacional (uso, reefer, regiao), nao pela duracao do contrato"},
    {"area": "dados", "recomendacao": "preservar vinculo peca-linha de mao de obra na extracao; investigar anomalias de cadastro (n_os_acum extremo); ampliar cobertura GPS"},
    {"area": "modelagem futura", "recomendacao": "Mixed-Effects Random Forest / modelos hierarquicos e zero-inflados"},
])
recom.to_csv(TABLES / "06_recomendacoes_negocio.csv", index=False)

print("OK 06 (alvo interno)")
print(resumo.to_string(index=False))
