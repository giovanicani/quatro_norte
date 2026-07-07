# 03d - Diagnostico de outliers por variavel (regra IQR + percentis extremos)
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path.cwd()
if PROJECT_ROOT.name in ("notebooks", "src"):
    PROJECT_ROOT = PROJECT_ROOT.parent
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
TABLES = PROJECT_ROOT / "reports" / "tables"

TARGET = "custo_manutencao_interno_por_km_deflacionado"
base = pd.read_csv(DATA_PROCESSED / "base_mensal_carreta_deflacionada.csv",
                   parse_dates=["ano_mes"], low_memory=False)
df = base[(base["km_valido_modelagem_flag"] == 1) & base[TARGET].notna() & (base[TARGET] >= 0)]

VARS = [TARGET, "ano_modelo", "eixos", "comprimento", "idade_carreta", "km_rodado_mes",
        "km_acumulado", "km_por_mes", "franquia_km_mensal", "duracao_contrato_meses",
        "idade_contrato_meses_no_mes", "custo_acum_manutencao", "custo_preventivo_acum",
        "n_os_acum", "n_os_preventivas_acum", "custo_medio_movel_3m",
        "custo_preventivo_medio_movel_3m", "intervalo_medio_os", "meses_desde_ultima_os"]

rows = []
for col in VARS:
    s = pd.to_numeric(df[col], errors="coerce").dropna()
    if s.empty:
        continue
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    lim_sup = q3 + 1.5 * iqr
    p99, p999 = s.quantile(0.99), s.quantile(0.999)
    share_iqr = float((s > lim_sup).mean()) if iqr > 0 else 0.0
    ratio = float(s.max() / p99) if p99 > 0 else float("nan")
    rows.append({
        "variavel": col,
        "p99": p99, "p99_9": p999, "max": s.max(),
        "lim_sup_iqr": lim_sup,
        "share_acima_iqr": share_iqr,
        "razao_max_p99": ratio,
    })
out = pd.DataFrame(rows)

def decisao(r):
    if r["variavel"] == TARGET:
        return "cap p99,5 na modelagem; negativos excluidos"
    if r["razao_max_p99"] > 20:
        return "cauda extrema: winsorizar/monitorar; arvores robustas, mediana na imputacao"
    if r["share_acima_iqr"] > 0.10:
        return "cauda longa estrutural (nao e erro): manter; log/rank em modelos lineares"
    if r["share_acima_iqr"] > 0:
        return "outliers moderados: manter (robustez de arvore)"
    return "sem outliers relevantes"

out["decisao"] = out.apply(decisao, axis=1)
out.to_csv(TABLES / "03d_diagnostico_outliers.csv", index=False)
print(out.to_string(index=False))
