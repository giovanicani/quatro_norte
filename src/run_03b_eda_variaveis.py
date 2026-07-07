# 03b - EDA variavel-a-variavel (protocolo academico)
# Y = custo_manutencao_interno_por_km_deflacionado (custo interno total por km, CAD de dez/2025)
# Para cada quantitativa: histograma + boxplot + estatisticas descritivas.
# Para cada qualitativa: boxplot de Y por categoria + tabela de frequencia + stats de Y por categoria.
# Complementos: correlacao Pearson/Spearman com Y, eta2 para categoricas, VIF.
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

PROJECT_ROOT = Path.cwd()
if PROJECT_ROOT.name in ("notebooks", "src"):
    PROJECT_ROOT = PROJECT_ROOT.parent

DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
TABLES = PROJECT_ROOT / "reports" / "tables"
FIG_EDA = PROJECT_ROOT / "reports" / "figures" / "eda"
FIG_EDA.mkdir(parents=True, exist_ok=True)

TARGET = "custo_manutencao_interno_por_km_deflacionado"

base = pd.read_csv(DATA_PROCESSED / "base_mensal_carreta_deflacionada.csv", parse_dates=["ano_mes"])
df = base[base["km_valido_modelagem_flag"] == 1].copy()
df = df[df[TARGET].notna()]
df = df[df[TARGET] >= 0]

QUANT = [c for c in [
    "ano_modelo", "eixos", "comprimento", "idade_carreta",
    "km_rodado_mes", "km_acumulado", "km_por_mes", "franquia_km_mensal",
    "duracao_contrato_meses", "idade_contrato_meses_no_mes",
    "custo_acum_manutencao", "custo_preventivo_acum",
    "n_os_acum", "n_os_preventivas_acum",
    "custo_medio_movel_3m", "custo_preventivo_medio_movel_3m",
    "intervalo_medio_os", "meses_desde_ultima_os",
] if c in df.columns]

QUALI = [c for c in [
    "cod_montadora", "flag_refrigerado", "tipo_contrato", "tipo_manutencao",
    "cod_grupo_manutencao", "regiao_operacao", "cod_classe",
] if c in df.columns]

print(f"Base EDA: {len(df):,} linhas | Y = {TARGET}")
print("Quantitativas:", QUANT)
print("Qualitativas:", QUALI)

y = pd.to_numeric(df[TARGET], errors="coerce")
y_p99 = y.quantile(0.99)

# ---------- estatisticas descritivas (Y + quantitativas) ----------
rows = []
for col in [TARGET] + QUANT:
    s = pd.to_numeric(df[col], errors="coerce").dropna()
    if s.empty:
        continue
    rows.append({
        "variavel": col, "tipo": "Y" if col == TARGET else "Quantitativa",
        "N": len(s), "media": s.mean(), "desvio_padrao": s.std(),
        "min": s.min(), "Q1": s.quantile(0.25), "mediana": s.median(),
        "Q3": s.quantile(0.75), "max": s.max(), "assimetria": s.skew(),
    })
desc = pd.DataFrame(rows)
desc.to_csv(TABLES / "03b_estatisticas_descritivas.csv", index=False)

# ---------- histograma + boxplot por quantitativa ----------
def hist_box(col, s, title_extra=""):
    s = s.dropna()
    if s.empty:
        return
    cap = s.quantile(0.99)
    s_plot = s[s <= cap] if s.nunique() > 20 else s
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    axes[0].hist(s_plot, bins=40, color="#3b6ea5", edgecolor="white")
    axes[0].set_title(f"Histograma — {col}{title_extra}")
    axes[0].set_ylabel("frequencia")
    axes[1].boxplot(s_plot, vert=True, showfliers=True,
                    medianprops={"color": "#c44"},
                    flierprops={"markersize": 2, "alpha": 0.3})
    axes[1].set_title(f"Boxplot — {col}{title_extra}")
    for ax in axes:
        ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIG_EDA / f"quant_{col}.png", dpi=130)
    plt.close(fig)

hist_box(TARGET, y, " (corte p99)")
for col in QUANT:
    hist_box(col, pd.to_numeric(df[col], errors="coerce"))

# ---------- qualitativas: freq + boxplot de Y por categoria + stats ----------
freq_rows, ystat_rows, eta_rows = [], [], []
grand_mean = y.mean()
sst = ((y - grand_mean) ** 2).sum()

for col in QUALI:
    cat = df[col].fillna("SEM_INFORMACAO").astype(str)
    vc = cat.value_counts()
    top = vc.head(10).index.tolist()
    cat_top = cat.where(cat.isin(top), "OUTRAS")

    for k, v in vc.items():
        freq_rows.append({"variavel": col, "categoria": k, "n": v, "pct": v / len(cat)})

    g = df.assign(_cat=cat).groupby("_cat")[TARGET]
    stats = g.agg(["count", "mean", "std", "min", "median", "max"]).reset_index()
    stats.insert(0, "variavel", col)
    ystat_rows.append(stats)

    # eta2 (variancia entre grupos / total)
    ssb = sum(len(grp) * (grp.mean() - grand_mean) ** 2 for _, grp in g)
    eta2 = ssb / sst if sst > 0 else np.nan
    eta_rows.append({"variavel": col, "eta2": eta2, "eta": np.sqrt(eta2), "n_categorias": cat.nunique()})

    # boxplot Y (cortado em p99) por categoria (top 10)
    order = (df.assign(_cat=cat_top).groupby("_cat")[TARGET].median()
             .sort_values(ascending=False).index.tolist())
    data = [df.loc[(cat_top == c) & (y <= y_p99), TARGET].dropna() for c in order]
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.boxplot(data, tick_labels=order, showfliers=False, medianprops={"color": "#c44"})
    ax.set_title(f"{TARGET} por {col} (corte p99, sem outliers no grafico)")
    ax.set_ylabel("CAD/km (dez/2025)")
    ax.tick_params(axis="x", rotation=30)
    ax.grid(alpha=0.25, axis="y")
    fig.tight_layout()
    fig.savefig(FIG_EDA / f"quali_{col}.png", dpi=130)
    plt.close(fig)

pd.DataFrame(freq_rows).to_csv(TABLES / "03b_frequencia_categorias.csv", index=False)
pd.concat(ystat_rows).to_csv(TABLES / "03b_y_por_categoria.csv", index=False)
eta_df = pd.DataFrame(eta_rows).sort_values("eta", ascending=False)
eta_df.to_csv(TABLES / "03b_eta_categoricas.csv", index=False)

# ---------- correlacao com Y ----------
corr_rows = []
for col in QUANT:
    s = pd.to_numeric(df[col], errors="coerce")
    mask = s.notna() & y.notna()
    if mask.sum() < 100:
        continue
    corr_rows.append({
        "variavel": col,
        "pearson": y[mask].corr(s[mask], method="pearson"),
        "spearman": y[mask].corr(s[mask], method="spearman"),
        "n": int(mask.sum()),
    })
corr = pd.DataFrame(corr_rows).sort_values("spearman", key=abs, ascending=False)
corr.to_csv(TABLES / "03b_correlacao_com_y.csv", index=False)

# grafico ranking de associacao (|spearman| numericas + eta categoricas)
rank = pd.concat([
    corr.assign(forca=corr["spearman"].abs(), tipo="numerica (|Spearman|)")[["variavel", "forca", "tipo"]],
    eta_df.assign(forca=eta_df["eta"], tipo="categorica (eta)")[["variavel", "forca", "tipo"]],
]).sort_values("forca")
fig, ax = plt.subplots(figsize=(9, max(5, 0.32 * len(rank))))
colors = rank["tipo"].map({"numerica (|Spearman|)": "#3b6ea5", "categorica (eta)": "#c47a3b"})
ax.barh(rank["variavel"], rank["forca"], color=colors)
ax.set_title("Forca de associacao com o custo interno por km (deflacionado)")
ax.set_xlabel("0 = sem relacao · 1 = deterministica")
ax.grid(alpha=0.25, axis="x")
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color="#3b6ea5", label="numerica (|Spearman|)"),
                   Patch(color="#c47a3b", label="categorica (eta)")], loc="lower right")
fig.tight_layout()
fig.savefig(FIG_EDA / "ranking_associacao_y.png", dpi=140)
plt.close(fig)

# ---------- matriz de correlacao Spearman entre numericas + VIF ----------
num_df = df[QUANT].apply(pd.to_numeric, errors="coerce")
spear = num_df.corr(method="spearman")
spear.to_csv(TABLES / "03b_spearman_numericas.csv")
fig, ax = plt.subplots(figsize=(10, 8))
im = ax.imshow(spear, cmap="RdBu_r", vmin=-1, vmax=1)
ax.set_xticks(range(len(QUANT)), QUANT, rotation=90)
ax.set_yticks(range(len(QUANT)), QUANT)
for i in range(len(QUANT)):
    for j in range(len(QUANT)):
        v = spear.iloc[i, j]
        if pd.notna(v):
            ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=6.5,
                    color="white" if abs(v) > 0.5 else "black")
fig.colorbar(im, shrink=0.8)
ax.set_title("Correlacao de Spearman entre variaveis numericas")
fig.tight_layout()
fig.savefig(FIG_EDA / "matriz_spearman.png", dpi=140)
plt.close(fig)

# VIF aproximado via R2 de regressao de cada X nas demais
from sklearn.linear_model import LinearRegression
from sklearn.impute import SimpleImputer

X = SimpleImputer(strategy="median").fit_transform(num_df)
vif_rows = []
for i, col in enumerate(QUANT):
    others = np.delete(X, i, axis=1)
    r2 = LinearRegression().fit(others, X[:, i]).score(others, X[:, i])
    vif_rows.append({"variavel": col, "vif": np.inf if r2 >= 0.999 else 1 / (1 - r2)})
pd.DataFrame(vif_rows).sort_values("vif", ascending=False).to_csv(TABLES / "03b_vif.csv", index=False)

# ---------- evolucao temporal do Y (real) ----------
evo = (df.assign(ano=df["ano_mes"].dt.year).groupby("ano")[TARGET]
       .agg(media="mean", mediana="median", p90=lambda s: s.quantile(0.9), n="count").reset_index())
evo.to_csv(TABLES / "03b_evolucao_y_anual.csv", index=False)
fig, ax = plt.subplots(figsize=(9, 4.5))
ax.plot(evo["ano"], evo["media"], marker="o", label="media")
ax.plot(evo["ano"], evo["mediana"], marker="s", label="mediana")
ax.set_title("Custo interno por km (deflacionado) — evolucao anual")
ax.set_ylabel("CAD/km (dez/2025)")
ax.legend(); ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(FIG_EDA / "evolucao_y_anual.png", dpi=140)
plt.close(fig)

print("OK EDA 03b")
print(desc[["variavel", "N", "media", "mediana", "max"]].to_string(index=False))
print(corr.to_string(index=False))
print(eta_df.to_string(index=False))
