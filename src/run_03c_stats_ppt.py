# Estatisticas complementares para o PPT (Y = custo interno total por km deflacionado)
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
y = df[TARGET]

stats = {
    "linhas_base_total": len(base),
    "carretas": base["id_carreta"].nunique(),
    "obs_y_valido": len(df),
    "share_y_zero": float((y == 0).mean()),
    "y_media": float(y.mean()),
    "y_mediana": float(y.median()),
    "y_mediana_positivos": float(y[y > 0].median()),
    "y_media_positivos": float(y[y > 0].mean()),
    "y_p90": float(y.quantile(0.9)),
    "y_p99": float(y.quantile(0.99)),
    "custo_total_nominal": float(base["custo_total_mes"].sum()),
    "custo_total_deflacionado": float(base["custo_total_mes_deflacionado"].sum()),
    "share_maint": float((df["tipo_manutencao"] == "MAINT").mean()),
}
pd.DataFrame([stats]).T.rename(columns={0: "valor"}).to_csv(TABLES / "03c_stats_ppt.csv")
print(pd.DataFrame([stats]).T)

evo = (df.assign(ano=df["ano_mes"].dt.year).groupby("ano")
       .apply(lambda g: pd.Series({
           "media_y": g[TARGET].mean(),
           "media_y_positivos": g.loc[g[TARGET] > 0, TARGET].mean(),
           "share_zero": (g[TARGET] == 0).mean(),
           "n": len(g)}), include_groups=False))
print(evo)
evo.to_csv(TABLES / "03c_evolucao_y_detalhe.csv")
