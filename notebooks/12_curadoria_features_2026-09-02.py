"""
Curadoria de features 2026-09-02 - Quatro Norte / MBA
=====================================================

Aplica a curadoria de variaveis decidida pelo Grupo, mede a associacao de cada
variavel com o custo anual por carreta e materializa as dummies autorizadas.

Decisoes de escopo desta rodada (ver docs/curadoria_features_2026-09-02.md):
  - D6 REVOGADA: a populacao passa a ser a base completa (sem filtro MAINT).
    `tipo_manutencao_ano` volta a ser feature; `populacao_maint_flag` sai.
  - Y decomposto: Y1 = custo_ano_real ; Y2 = n_os_ano ; Y3 = custo_medio_por_os_ano.
    Y1 = Y2 x Y3 (identidade), logo Y2 e Y3 NAO sao features de Y1.
  - `id_carreta` vira one-hot por decisao do Grupo, com ressalva metodologica.

Saidas:
  reports/tables/curadoria_features_2026-09-02.xlsx
  data/processed/base_anual_modelagem_2026-09-02.csv          (sem dummies de id_carreta)
  data/processed/base_anual_modelagem_id_dummy_2026-09-02.csv.gz (com dummies de id_carreta)
"""

from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
TABLES = PROJECT_ROOT / "reports" / "tables"
TABLES.mkdir(parents=True, exist_ok=True)

FORTE, MODERADA = 0.30, 0.15
COBERTURA_TOPN = 0.90        # top-N categorias que cobrem 90% das linhas; resto -> OUTROS
MAX_NIVEIS_INTEGRAIS = 10    # ate 10 niveis, nenhuma categoria e colapsada em OUTROS
CARD_ALTA = 30               # acima disso o eta e inflado pela cardinalidade

Y1, Y2, Y3 = "custo_ano_real", "n_os_ano", "custo_medio_por_os_ano"

base = pd.read_csv(DATA_PROCESSED / "base_anual_carreta_deflacionada.csv")
print("base:", base.shape)

# ---------------------------------------------------------------- curadoria ---
# acao: Y1 | Y2 | Y3 | MANTER | DUMMY | CHAVE | RETIRAR | PREMISSA | SERIE_TEMPORAL
CUR = [
    ("id_carreta", "DUMMY", "Identificacao da carreta.",
     "9.585 categorias. One-hot memoriza a carreta e nao generaliza para ativo novo; "
     "materializado por decisao explicita do Grupo, em arquivo separado."),
    ("ano", "CHAVE", "Ano em que ocorreram as OS.",
     "Usado como chave do split temporal (treino <=2024 / teste 2025). Nao vira dummy: "
     "um nivel 2026 nao existe no treino e quebraria a previsao."),
    ("custo_ano_nominal", "RETIRAR", "Numero sem a inflacao.",
     "Correto: e o Y1 antes da deflacao pelo CPI. Mante-lo seria vazamento direto."),
    ("n_os_ano", "Y2", "Prever a quantidade de OS para o ano de 2026.",
     "Componente aritmetico de Y1 (Y1 = Y2 x Y3). Vira alvo proprio, nunca feature de Y1."),
    ("n_sistemas_vmrs_distintos_ano", "PREMISSA",
     "Media da quantidade de VMRS usada pelas carretas nos ultimos 5 anos.",
     "Aba 03: a premissa do Grupo foi TESTADA e venceu. Media movel de 5 anos defasada "
     "Spearman 0,474 vs defasagem t-1 0,449 - a media suaviza o ruido de ano isolado. "
     "Usar a media, calculada SO com anos anteriores (sem vazamento). A versao "
     "contemporanea (0,702) e mais forte, mas nao existe para prever 2026."),
    ("share_pm_ano", "RETIRAR", "Nao testar: recorta classe especifica de manutencao.",
     "Aceito. Associacao com Y1 registrada na aba 02 para rastreio."),
    ("km_acumulado_fim_ano", "SERIE_TEMPORAL", "Estimar o KM em 2026.",
     "Contemporanea ao ano: no cenario preditivo usar o odometro de inicio de ano ou a "
     "projecao da serie por carreta."),
    ("vmrs_predominante_ano", "DUMMY",
     "Codigo mais frequente na carreta; empate resolvido pelo mais frequente da base.",
     "Contemporanea ao ano: valida no cenario explicativo; no preditivo exige a versao t-1."),
    ("regiao_operacao", "RETIRAR", "Retirar.",
     "Encerra a hipotese H5. Ha respaldo estatistico (eta baixo) - ver aba 02."),
    ("provincia_estado", "RETIRAR", "Retirar.",
     "Idem H5. Cobertura parcial (~54%) reforca a decisao."),
    ("tipo_manutencao_ano", "DUMMY",
     "Verificar se tipos de contrato especificos impactam o custo.",
     "So e possivel porque D6 foi revogada (base completa). Desbalanceada: MAINT ~88%; "
     "reportar custo medio por nivel, nao so eta."),
    ("share_maint_ano", "MANTER", "Acompanha o resultado de tipo_manutencao_ano.",
     "Redundante com a dummy de tipo_manutencao_ano; vigiar VIF em modelo linear."),
    ("n_tipos_manutencao_ano", "RETIRAR", "Redundante com tipo_manutencao_ano.",
     "Aceito - mede so quantos regimes conviveram no ano."),
    ("tempo_contrato_meses_fim_ano", "MANTER", "Avaliar impacto do tempo de contrato (H7).",
     "Contemporanea: no preditivo usar tempo_contrato_meses_inicio_ano. Colinear com "
     "idade_carreta - checar VIF."),
    ("n_clientes_ano", "MANTER", "Avaliar se mais clientes impactam o custo.",
     "Aceito."),
    ("cod_cliente_predominante_ano", "RETIRAR", "Retirar do modelo.",
     "Coerente com D4: 597 categorias, risco de memorizacao. Uso so descritivo."),
    ("descricao_carreta", "DUMMY", "Detalhamento da carreta.",
     "253 categorias -> top-N + OUTROS cobrindo 90% das linhas."),
    ("cod_montadora", "RETIRAR", "Retirar do modelo.",
     "Registrado: eta moderado (ver aba 02). Parte da informacao sobrevive em descricao_carreta."),
    ("flag_refrigerado", "DUMMY", "Veiculos refrigerados sao mais caros de manter.",
     "Binaria - one-hot com uma coluna basta."),
    ("tailgate_flag", "DUMMY", "Tambem precisa de manutencao e pode afetar o custo.",
     "IMPOSSIVEL: constante na base (variancia nula). Nao ha dummy a criar - ver aba 07."),
    ("unit_subtype", "DUMMY", "Classificacao especifica do negocio.",
     "26 categorias -> top-N + OUTROS."),
    ("tire_size", "DUMMY", "Tamanho do pneu impacta no custo.",
     "24 categorias, com ausentes -> nivel AUSENTE explicito."),
    ("suspension_type", "RETIRAR", "A maioria das carretas ja tem suspensao a ar.",
     "Aceito - baixa variabilidade util."),
    ("new_used_indicator", "RETIRAR", "Em contrato as carretas sao novas, quase todas leasing.",
     "Aceito."),
    ("ano_modelo", "RETIRAR", "Redundante com idade_carreta.",
     "Correto: idade_carreta = ano - ano de entrada (fallback ano_modelo)."),
    ("eixos", "MANTER", "Mais eixos, mais pneus e outros itens.",
     "Quase constante (95% com 2 eixos) - ver aba 02 antes de manter no modelo final."),
    ("comprimento", "RETIRAR", "Informacao ja presente em descricao_carreta.",
     "Aceito."),
    ("data_entrada_servico", "RETIRAR", "Foco em custo anual.",
     "A informacao permanece via idade_carreta."),
    ("idade_carreta", "MANTER", "Prever 2026 com base nos anos anteriores.",
     "Deterministica no tempo: idade_2026 = idade_2025 + 1."),
    ("km_rodado_ano", "MANTER", "Prever 2026 com base nos anos anteriores.",
     "Contemporanea - no preditivo exige projecao, como km_acumulado_fim_ano."),
    ("n_os_ano_anterior", "MANTER", "Utilizar no modelo.", "Defasada - sem vazamento."),
    ("n_os_acum_ate_ano_anterior", "MANTER", "Utilizar no modelo.", "Defasada - sem vazamento."),
    ("anos_ativo_ate_ano_anterior", "MANTER", "Utilizar no modelo.", "Defasada - sem vazamento."),
    ("tempo_contrato_meses_inicio_ano", "MANTER", "Utilizar no modelo.",
     "Versao defasada de tempo_contrato_meses_fim_ano - a admissivel no preditivo."),
    ("trocou_contrato_ano", "MANTER", "Utilizar no modelo.", "Binaria, contemporanea."),
    ("populacao_maint_flag", "RETIRAR", "Retirar.",
     "Implica REVOGAR a decisao D6 (populacao = MAINT). Confirmado pelo Grupo em "
     "2026-09-02: a modelagem passa a usar a base completa."),
    ("custo_ano_real", "Y1", "Variavel principal a prever para 2026.",
     "Alvo. CAD real de dez/2025 (CPI Canada)."),
    ("custo_medio_por_os_ano", "Y3", "Utilizar no modelo.",
     "Componente aritmetico de Y1 (Y1 = Y2 x Y3): como feature daria R2 artificial ~1. "
     "Vira o terceiro alvo, conforme decisao de 2026-09-02."),
    ("custo_ano_anterior", "MANTER", "Utilizar no modelo.", "Defasada - sem vazamento."),
    ("custo_acum_ate_ano_anterior", "MANTER", "Utilizar no modelo.", "Defasada - sem vazamento."),
]
cur = pd.DataFrame(CUR, columns=["variavel", "acao", "justificativa_grupo", "nota_tecnica"])
assert set(cur.variavel) == set(base.columns), set(cur.variavel) ^ set(base.columns)

# ------------------------------------------------------------- associacoes ---
def eta_ratio(y, g):
    """Razao de correlacao eta: sqrt(SQ_entre / SQ_total)."""
    d = pd.DataFrame({"y": y, "g": g}).dropna()
    if d.g.nunique() < 2 or len(d) < 10:
        return np.nan, np.nan, np.nan
    gm = d.y.mean()
    ss_tot = ((d.y - gm) ** 2).sum()
    if ss_tot == 0:
        return np.nan, np.nan, np.nan
    grp = d.groupby("g")["y"]
    ss_bet = (grp.count() * (grp.mean() - gm) ** 2).sum()
    amostras = [v.to_numpy() for _, v in grp if len(v) > 1]
    F, p = stats.f_oneway(*amostras) if len(amostras) > 1 else (np.nan, np.nan)
    return float(np.sqrt(ss_bet / ss_tot)), float(F), float(p)


def classifica(f):
    if pd.isna(f):
        return "nao calculavel"
    return "FORTE" if f >= FORTE else ("moderada" if f >= MODERADA else "fraca")


NUMERICAS = [c for c in base.columns
             if pd.api.types.is_numeric_dtype(base[c]) and c not in {"id_carreta", "ano"}]
CATEGORICAS = [c for c in base.columns if c not in NUMERICAS and c not in {"id_carreta", "ano"}]


def evidencia(alvo):
    linhas = []
    y = base[alvo]
    for c in NUMERICAS:
        if c == alvo:
            continue
        d = pd.concat([y, base[c]], axis=1).dropna()
        if len(d) < 10 or d[c].nunique() < 2:
            r = rho = pr = pp = np.nan
        else:
            r, pp = stats.pearsonr(d[alvo], d[c])
            rho, pr = stats.spearmanr(d[alvo], d[c])
        linhas.append({"variavel": c, "tipo": "quantitativa", "metrica": "Spearman",
                       "forca": abs(rho) if pd.notna(rho) else np.nan,
                       "spearman": rho, "pearson": r, "p_valor": pr,
                       "n_validos": len(d), "pct_ausente": 100 * base[c].isna().mean(),
                       "n_categorias": np.nan})
    for c in CATEGORICAS:
        g = base[c].fillna("AUSENTE").astype(str)
        e, F, p = eta_ratio(y, g)
        linhas.append({"variavel": c, "tipo": "categorica", "metrica": "eta (ANOVA)",
                       "forca": e, "spearman": np.nan, "pearson": np.nan, "p_valor": p,
                       "n_validos": int(y.notna().sum()),
                       "pct_ausente": 100 * base[c].isna().mean(),
                       "n_categorias": int(g.nunique())})
    ev = pd.DataFrame(linhas).sort_values("forca", ascending=False, na_position="last")
    ev["classificacao"] = ev["forca"].map(classifica)
    ev["forca"] = ev["forca"].round(4)
    for cc in ["spearman", "pearson"]:
        ev[cc] = ev[cc].round(4)
    ev["pct_ausente"] = ev["pct_ausente"].round(2)
    ev["alerta"] = np.where(
        ev["n_categorias"] > CARD_ALTA,
        f"eta inflado: mais de {CARD_ALTA} categorias explicam variancia por contagem de "
        "graus de liberdade, nao por efeito real. Nao comparar com variaveis de poucos niveis",
        "")
    return ev.reset_index(drop=True)


ev1 = evidencia(Y1)
ev2 = evidencia(Y2)
ev3 = evidencia(Y3)
print("evidencia calculada")

# eta de id_carreta (mecanicamente inflado - so para registro)
e_id, _, p_id = eta_ratio(base[Y1], base["id_carreta"].astype(str))

# ------------------------------- premissa: media 5 anos vs defasagem t-1 ------
b = base.sort_values(["id_carreta", "ano"]).copy()
g = b.groupby("id_carreta")["n_sistemas_vmrs_distintos_ano"]
b["vmrs_dist_t_1"] = g.shift(1)
b["vmrs_dist_media_hist"] = g.transform(lambda s: s.shift(1).expanding().mean())
b["vmrs_dist_media_5a"] = g.transform(lambda s: s.shift(1).rolling(5, min_periods=1).mean())

prem = []
for nome, col, desc in [
    ("Contemporanea (ano corrente)", "n_sistemas_vmrs_distintos_ano",
     "Valor do proprio ano. Maior associacao, mas indisponivel para prever 2026."),
    ("Defasada t-1", "vmrs_dist_t_1",
     "Valor do ano anterior. Conhecida no inicio do ano - sem vazamento."),
    ("Media movel 5 anos (defasada)", "vmrs_dist_media_5a",
     "Premissa proposta pelo Grupo, calculada so com anos anteriores."),
    ("Media historica (defasada)", "vmrs_dist_media_hist",
     "Media de todos os anos anteriores da carreta."),
]:
    d = b[[Y1, col]].dropna()
    rho, p = stats.spearmanr(d[Y1], d[col])
    prem.append({"versao": nome, "coluna": col, "spearman_com_Y1": round(float(rho), 4),
                 "p_valor": float(p), "n_validos": len(d),
                 "pct_disponivel": round(100 * b[col].notna().mean(), 1),
                 "observacao": desc})
premissa = pd.DataFrame(prem)
print(premissa[["versao", "spearman_com_Y1", "pct_disponivel"]].to_string(index=False))

# -------------------------------------------------- Y medio por categoria ----
por_cat = []
for c in CATEGORICAS:
    gg = base[c].fillna("AUSENTE").astype(str)
    t = base.groupby(gg)[Y1].agg(n="size", media="mean", mediana="median", desvio="std")
    t = t.sort_values("media", ascending=False).reset_index()
    t.columns = ["categoria", "n_carreta_ano", "custo_medio", "custo_mediano", "desvio"]
    t.insert(0, "variavel", c)
    t["ic95_semi_amplitude"] = 1.96 * t["desvio"] / np.sqrt(t["n_carreta_ano"])
    t["pct_linhas"] = 100 * t["n_carreta_ano"] / len(base)
    por_cat.append(t.head(30))
y_por_cat = pd.concat(por_cat, ignore_index=True).round(2)

# ------------------------------------------------------------------ dummies ---
forca1 = ev1.set_index("variavel")["forca"].to_dict()
pedidas = cur.loc[cur.acao == "DUMMY", "variavel"].tolist()

mapa, criadas, nao_criadas = [], {}, []
for c in pedidas:
    if c == "id_carreta":
        continue
    serie = base[c].fillna("AUSENTE").astype(str)
    f = forca1.get(c, np.nan)
    if serie.nunique() < 2:
        nao_criadas.append({"variavel": c, "motivo": "constante na base (variancia nula)",
                            "forca_Y1": f, "n_categorias": int(serie.nunique())})
        continue
    if pd.isna(f) or f < FORTE:
        # excecao de escopo: tipo_manutencao_ano sustenta H6b, razao da revogacao de D6
        if c != "tipo_manutencao_ano":
            nao_criadas.append({"variavel": c,
                                "motivo": f"associacao {classifica(f)} (<{FORTE}); a autorizacao "
                                          "do Grupo cobria apenas associacao FORTE",
                                "forca_Y1": f, "n_categorias": int(serie.nunique())})
            continue
    freq = serie.value_counts(normalize=True)
    if serie.nunique() <= MAX_NIVEIS_INTEGRAIS:
        manter = list(freq.index)          # poucos niveis: preserva todos
    else:
        acum = freq.cumsum()
        manter = list(freq.index[:max(1, int((acum < COBERTURA_TOPN).sum()) + 1)])
    reduzida = pd.Series(np.where(serie.isin(manter), serie, "OUTROS"), index=base.index)
    d = pd.get_dummies(reduzida, prefix=f"dm_{c}", drop_first=True, dtype="int8")
    base_ref = sorted(reduzida.unique())[0]
    criadas[c] = d
    obs = ("materializada (excecao de escopo: sustenta H6b, razao da revogacao de D6)"
           if c == "tipo_manutencao_ano" and f < FORTE else "materializada")
    for col in d.columns:
        mapa.append({"variavel_origem": c, "coluna_dummy": col,
                     "categoria": col.replace(f"dm_{c}_", ""),
                     "categoria_base_omitida": base_ref,
                     "pct_linhas": round(100 * float(d[col].mean()), 2),
                     "forca_Y1": f, "classificacao": classifica(f), "status": obs})
mapa_dummies = pd.DataFrame(mapa)
nao_materializadas = pd.DataFrame(nao_criadas)

# dummies de id_carreta (decisao explicita do Grupo)
d_id = pd.get_dummies(base["id_carreta"].astype(str), prefix="dm_id_carreta",
                      drop_first=True, dtype="int8")
mapa_id = pd.DataFrame({
    "coluna_dummy": d_id.columns,
    "id_carreta": [c.replace("dm_id_carreta_", "") for c in d_id.columns],
    "n_carreta_ano": [int(d_id[c].sum()) for c in d_id.columns],
})
mapa_id["categoria_base_omitida"] = sorted(base["id_carreta"].astype(str))[0]

# ------------------------------------------------------------ base final -----
manter_cols = cur.loc[cur.acao.isin(["MANTER", "PREMISSA", "SERIE_TEMPORAL"]), "variavel"].tolist()
cod = pd.concat(
    [base[["id_carreta", "ano", Y1, Y2, Y3]], base[manter_cols]]
    + [criadas[c] for c in criadas], axis=1)
# versoes defasadas da premissa VMRS (aba 03): a media movel de 5 anos venceu o teste
cod["vmrs_dist_media_5a"] = b["vmrs_dist_media_5a"].reindex(cod.index)
cod["vmrs_dist_t_1"] = b["vmrs_dist_t_1"].reindex(cod.index)
print("base codificada:", cod.shape)

cod.to_csv(DATA_PROCESSED / "base_anual_modelagem_2026-09-02.csv", index=False)
# 9.584 dummies -> ~926 MB em CSV puro; gravado comprimido (pd.read_csv le direto)
pd.concat([cod, d_id], axis=1).to_csv(
    DATA_PROCESSED / "base_anual_modelagem_id_dummy_2026-09-02.csv.gz",
    index=False, compression="gzip")

# ---------------------------------------------------------------- removidas ---
rem = cur[cur.acao == "RETIRAR"].merge(
    ev1[["variavel", "forca", "metrica", "classificacao"]], on="variavel", how="left")
rem = rem.rename(columns={"forca": "forca_associacao_Y1", "metrica": "metrica_usada",
                          "classificacao": "classificacao_Y1"})
rem["alerta"] = np.where(
    rem.classificacao_Y1 == "FORTE",
    "ATENCAO: associacao FORTE com Y1 - a remocao e decisao de negocio, nao consequencia "
    "estatistica. Perde-se poder explicativo.",
    np.where(rem.classificacao_Y1 == "moderada",
             "Associacao moderada - remocao aceitavel, custo explicativo baixo.", ""))
rem = rem[["variavel", "justificativa_grupo", "nota_tecnica", "forca_associacao_Y1",
           "metrica_usada", "classificacao_Y1", "alerta"]]

# tabela de decisao consolidada
dec = cur.merge(ev1[["variavel", "forca", "metrica", "classificacao", "pct_ausente",
                     "n_categorias"]], on="variavel", how="left")
ACAO_TXT = {
    "Y1": "ALVO PRINCIPAL (Y1)", "Y2": "ALVO SECUNDARIO (Y2)", "Y3": "ALVO SECUNDARIO (Y3)",
    "MANTER": "MANTER como feature", "DUMMY": "DUMMY (one-hot)", "CHAVE": "CHAVE (nao e feature)",
    "RETIRAR": "RETIRAR", "PREMISSA": "MANTER sob premissa", "SERIE_TEMPORAL": "MANTER via projecao",
}
dec.insert(1, "decisao", dec.acao.map(ACAO_TXT))
dec = dec.drop(columns="acao").rename(columns={
    "forca": "forca_associacao_Y1", "metrica": "metrica_usada", "classificacao": "classificacao_Y1"})
dec["entra_no_modelo"] = np.where(
    dec.decisao.str.startswith(("MANTER", "DUMMY")), "sim",
    np.where(dec.decisao.str.startswith("ALVO"), "e alvo", "nao"))
materializadas = set(mapa_dummies.variavel_origem) if len(mapa_dummies) else set()
dec["dummy_materializada"] = np.where(
    dec.decisao.eq("DUMMY (one-hot)"),
    np.where(dec.variavel.isin(materializadas | {"id_carreta"}), "sim", "NAO - ver aba 07"), "-")

leia_me = pd.DataFrame([
    ("Projeto", "Quatro Norte / MBA - custo anual de manutencao por carreta (CAD real dez/2025)"),
    ("Data", "2026-09-02"),
    ("Base", f"{len(base):,} carreta-anos x {base.shape[1]} colunas; "
             f"{base.id_carreta.nunique():,} carretas; anos "
             f"{int(base.ano.min())}-{int(base.ano.max())}"),
    ("Fonte", "data/processed/base_anual_carreta_deflacionada.csv (fonte unica fato_wo_ml, 29 col)"),
    ("Y1", "custo_ano_real - alvo principal, o que se quer prever para 2026"),
    ("Y2", "n_os_ano - quantidade de OS no ano (alvo secundario)"),
    ("Y3", "custo_medio_por_os_ano - custo medio por OS (alvo secundario)"),
    ("Identidade", "Y1 = Y2 x Y3. Por isso Y2 e Y3 nao podem ser features de Y1: "
                   "dariam R2 artificial proximo de 1. Previsao de 2026: Y1 = Y2 previsto x Y3 previsto"),
    ("Decisao de populacao", "D6 REVOGADA em 2026-09-02: a modelagem usa a base completa "
                             "(nao so o regime MAINT). Por isso tipo_manutencao_ano volta a ser "
                             "feature e populacao_maint_flag foi retirada"),
    ("Como ler a forca", f"quantitativas: |Spearman|; categoricas: eta (razao de correlacao). "
                         f"FORTE >= {FORTE} | moderada {MODERADA} a {FORTE} | fraca < {MODERADA}"),
    ("Por que Spearman", "o custo anual e muito assimetrico (cauda longa a direita); Spearman mede "
                         "associacao monotona sem exigir normalidade nem relacao linear"),
    ("Por que eta", "eta e a raiz de (variancia entre categorias / variancia total): quanto do "
                    "custo a categoria explica sozinha. Vem com o p-valor da ANOVA"),
    ("Cuidado com o p-valor", "com ~47,7 mil linhas quase tudo da p < 0,05. O que decide e a FORCA "
                              "da associacao, nao a significancia"),
    ("Regra das dummies", f"top-N categorias que cobrem {COBERTURA_TOPN:.0%} das linhas + OUTROS; "
                          "uma categoria e omitida como base (evita colinearidade perfeita)"),
    ("Ausentes", "nas categoricas a ausencia vira o nivel AUSENTE - e informacao, nao ruido"),
    ("id_carreta", f"one-hot com {d_id.shape[1]:,} colunas foi gerado por decisao do Grupo, em CSV "
                   f"separado (base_anual_modelagem_id_dummy_2026-09-02.csv.gz) - nao cabe nesta "
                   f"planilha. eta bruto com Y1 = {e_id:.3f}, mas o valor e inflado mecanicamente "
                   f"({base.id_carreta.nunique():,} grupos): nao e comparavel com as demais variaveis"),
    ("Abas", "01 decisoes | 02 evidencia Y1 | 03 premissa VMRS | 04 evidencia Y2 e Y3 | "
             "05 custo por categoria | 06 mapa das dummies | 07 dummies nao materializadas | "
             "08 removidas | 09 base codificada | 10 mapa das dummies de id_carreta | "
             "11 comparativo Y1 x Y2 | 12 recomendado para Y1 | 13 recomendado para Y2"),
    ("Disponibilidade", "coluna da aba 11. DISPONIVEL = existe no inicio do ano, serve para "
                        "prever 2026. CONTEMPORANEA = descreve o ano que ja aconteceu, so "
                        "vale no cenario explicativo. VAZAMENTO/ALVO/POPULACAO = nao e feature"),
    ("Muda de papel", "coluna da aba 11: marca as variaveis fracas em Y1 que sobem em Y2 - "
                      "sao as candidatas a entrar so no modelo de Y2"),
], columns=["item", "descricao"])


# ------------------------------------- comparativo Y1 x Y2 (fechamento da EDA) ---
# Classificacao de DISPONIBILIDADE: o que pode entrar num modelo que preve o ano
# seguinte (2026) sem vazamento. Uma variavel contemporanea ao ano descreve o ano que
# ja aconteceu - nao existe em janeiro quando o orcamento e feito.
DISPONIBILIDADE = {
    # alvos e componentes aritmeticos
    "custo_ano_real": ("ALVO Y1", "E a propria resposta"),
    "n_os_ano": ("ALVO Y2", "Componente de Y1; virou alvo (D8)"),
    "custo_medio_por_os_ano": ("ALVO Y3", "Componente de Y1; virou alvo (D8)"),
    "custo_ano_nominal": ("VAZAMENTO", "E Y1 antes da deflacao"),
    "populacao_maint_flag": ("POPULACAO", "Define a amostra, nao explica o custo"),
    # estaticas do ativo - disponiveis sempre
    "descricao_carreta": ("DISPONIVEL", "Atributo estatico do ativo"),
    "unit_subtype": ("DISPONIVEL", "Atributo estatico do ativo"),
    "flag_refrigerado": ("DISPONIVEL", "Atributo estatico do ativo"),
    "cod_montadora": ("DISPONIVEL", "Atributo estatico do ativo"),
    "tire_size": ("DISPONIVEL", "Atributo estatico do ativo"),
    "suspension_type": ("DISPONIVEL", "Atributo estatico do ativo"),
    "new_used_indicator": ("DISPONIVEL", "Atributo estatico do ativo"),
    "ano_modelo": ("DISPONIVEL", "Atributo estatico do ativo"),
    "comprimento": ("DISPONIVEL", "Atributo estatico do ativo"),
    "eixos": ("DISPONIVEL", "Atributo estatico do ativo"),
    "tailgate_flag": ("DISPONIVEL", "Atributo estatico - porem constante"),
    "data_entrada_servico": ("DISPONIVEL", "Data de entrada; usar via idade_carreta"),
    "idade_carreta": ("DISPONIVEL", "Deterministica: idade_2026 = idade_2025 + 1"),
    # historico defasado - disponivel no inicio do ano
    "n_os_ano_anterior": ("DISPONIVEL", "Historico de t-1"),
    "n_os_acum_ate_ano_anterior": ("DISPONIVEL", "Historico acumulado ate t-1"),
    "custo_ano_anterior": ("DISPONIVEL", "Historico de t-1"),
    "custo_acum_ate_ano_anterior": ("DISPONIVEL", "Historico acumulado ate t-1"),
    "anos_ativo_ate_ano_anterior": ("DISPONIVEL", "Historico ate t-1"),
    "tempo_contrato_meses_inicio_ano": ("DISPONIVEL", "Maturidade contratual em t-1"),
    # contemporaneas ao ano - so cenario explicativo
    "n_sistemas_vmrs_distintos_ano": ("CONTEMPORANEA", "Descreve o ano corrente; usar a media defasada de 5 anos no preditivo"),
    "share_pm_ano": ("CONTEMPORANEA", "Fracao de OS preventivas do ano corrente"),
    "km_rodado_ano": ("CONTEMPORANEA", "Km do ano corrente; exige projecao para 2026"),
    "km_acumulado_fim_ano": ("CONTEMPORANEA", "Odometro de fim de ano; usar o de inicio no preditivo"),
    "vmrs_predominante_ano": ("CONTEMPORANEA", "Sistema predominante do ano corrente"),
    "share_maint_ano": ("CONTEMPORANEA", "Composicao contratual do ano corrente"),
    "n_tipos_manutencao_ano": ("CONTEMPORANEA", "Regimes que conviveram no ano corrente"),
    "tempo_contrato_meses_fim_ano": ("CONTEMPORANEA", "Maturidade no fim do ano corrente"),
    "n_clientes_ano": ("CONTEMPORANEA", "Clientes do ano corrente"),
    "trocou_contrato_ano": ("CONTEMPORANEA", "Troca ocorrida no ano corrente"),
    "cod_cliente_predominante_ano": ("CONTEMPORANEA", "Cliente do ano corrente; 597 categorias (D4)"),
    "tipo_manutencao_ano": ("DISPONIVEL (contrato vigente)", "Regime do contrato em vigor - conhecido antes do reparo"),
    "regiao_operacao": ("CONTEMPORANEA", "Regiao predominante do ano corrente"),
    "provincia_estado": ("CONTEMPORANEA", "Provincia predominante do ano corrente"),
}

comp = (ev1[["variavel", "tipo", "forca", "classificacao", "n_categorias"]]
        .rename(columns={"forca": "forca_Y1", "classificacao": "classe_Y1"})
        .merge(ev2[["variavel", "forca", "classificacao"]]
               .rename(columns={"forca": "forca_Y2", "classificacao": "classe_Y2"}),
               on="variavel", how="outer"))
comp["disponibilidade"] = comp.variavel.map(lambda v: DISPONIBILIDADE.get(v, ("?", ""))[0])
comp["nota_disponibilidade"] = comp.variavel.map(lambda v: DISPONIBILIDADE.get(v, ("?", ""))[1])
comp = comp.merge(dec[["variavel", "decisao"]], on="variavel", how="left")
# forca combinada: a maior das duas, para ordenar o interesse global
comp["forca_max"] = comp[["forca_Y1", "forca_Y2"]].max(axis=1)
comp["muda_de_papel"] = np.where(
    (comp.classe_Y1 == "fraca") & (comp.classe_Y2.isin(["FORTE", "moderada"])),
    "SOBE em Y2 (fraca em Y1)",
    np.where((comp.classe_Y1.isin(["FORTE", "moderada"])) & (comp.classe_Y2 == "fraca"),
             "CAI em Y2 (relevante em Y1)", ""))
comp = comp.sort_values("forca_max", ascending=False, na_position="last").reset_index(drop=True)
comp = comp[["variavel", "tipo", "disponibilidade", "forca_Y1", "classe_Y1",
             "forca_Y2", "classe_Y2", "muda_de_papel", "decisao", "n_categorias",
             "nota_disponibilidade"]]
comp.to_csv(TABLES / "12_comparativo_Y1_Y2.csv", index=False)

# conjunto recomendado para cada alvo: disponivel para 2026 e associacao ao menos moderada
def recomenda(alvo_forca, alvo_classe):
    ok = comp[comp.disponibilidade.str.startswith("DISPONIVEL")
              & comp[alvo_classe].isin(["FORTE", "moderada"])
              & (comp.variavel != "tailgate_flag")]
    return ok.sort_values(alvo_forca, ascending=False)[
        ["variavel", "tipo", alvo_forca, alvo_classe, "decisao"]]

rec_y1 = recomenda("forca_Y1", "classe_Y1")
rec_y2 = recomenda("forca_Y2", "classe_Y2")
rec_y1.to_csv(TABLES / "12_recomendado_Y1.csv", index=False)
rec_y2.to_csv(TABLES / "12_recomendado_Y2.csv", index=False)
print()
print("=== FECHAMENTO DA EDA: candidatas sem vazamento, associacao >= moderada ===")
print(f"para Y1 (custo anual): {len(rec_y1)} variaveis")
print(rec_y1.to_string(index=False))
print()
print(f"para Y2 (n de OS): {len(rec_y2)} variaveis")
print(rec_y2.to_string(index=False))

xlsx = TABLES / "curadoria_features_2026-09-02.xlsx"
with pd.ExcelWriter(xlsx, engine="xlsxwriter") as xw:
    leia_me.to_excel(xw, sheet_name="00_Leia_me", index=False)
    dec.to_excel(xw, sheet_name="01_Decisoes", index=False)
    ev1.to_excel(xw, sheet_name="02_Evidencia_Y1", index=False)
    premissa.to_excel(xw, sheet_name="03_Premissa_VMRS", index=False)
    ev2.assign(alvo=Y2).to_excel(xw, sheet_name="04_Evidencia_Y2_Y3", index=False)
    ev3.assign(alvo=Y3).to_excel(xw, sheet_name="04_Evidencia_Y2_Y3", index=False,
                                 startrow=len(ev2) + 3)
    y_por_cat.to_excel(xw, sheet_name="05_Custo_por_categoria", index=False)
    mapa_dummies.to_excel(xw, sheet_name="06_Mapa_dummies", index=False)
    nao_materializadas.to_excel(xw, sheet_name="07_Dummies_nao_criadas", index=False)
    rem.to_excel(xw, sheet_name="08_Removidas", index=False)
    cod.to_excel(xw, sheet_name="09_Base_codificada", index=False)
    mapa_id.to_excel(xw, sheet_name="10_Mapa_dummies_id_carreta", index=False)
    comp.to_excel(xw, sheet_name="11_Comparativo_Y1_Y2", index=False)
    rec_y1.to_excel(xw, sheet_name="12_Recomendado_Y1", index=False)
    rec_y2.to_excel(xw, sheet_name="13_Recomendado_Y2", index=False)

    wb = xw.book
    fmt_h = wb.add_format({"bold": True, "bg_color": "#1F3864", "font_color": "white",
                           "text_wrap": True, "valign": "top", "border": 1})
    fmt_w = wb.add_format({"text_wrap": True, "valign": "top"})
    larguras = {"00_Leia_me": [26, 108],
                "01_Decisoes": [32, 24, 46, 64, 14, 14, 14, 11, 12, 14, 16],
                "02_Evidencia_Y1": [32, 14, 14, 10, 11, 11, 12, 11, 12, 12, 14],
                "03_Premissa_VMRS": [30, 26, 16, 12, 12, 14, 72],
                "04_Evidencia_Y2_Y3": [32, 14, 14, 10, 11, 11, 12, 11, 12, 12, 14, 22],
                "05_Custo_por_categoria": [28, 26, 14, 14, 14, 14, 20, 12],
                "06_Mapa_dummies": [22, 36, 26, 22, 12, 11, 14, 46],
                "07_Dummies_nao_criadas": [22, 74, 12, 14],
                "08_Removidas": [30, 46, 64, 14, 14, 14, 62],
                "10_Mapa_dummies_id_carreta": [26, 14, 14, 22],
                "11_Comparativo_Y1_Y2": [32, 13, 30, 11, 12, 11, 12, 26, 24, 12, 52],
                "12_Recomendado_Y1": [32, 14, 11, 12, 24],
                "13_Recomendado_Y2": [32, 14, 11, 12, 24]}
    for aba, ws in xw.sheets.items():
        ws.freeze_panes(1, 1)
        for i, w in enumerate(larguras.get(aba, [18] * 14)):
            ws.set_column(i, i, w, fmt_w)
    for aba, df in [("00_Leia_me", leia_me), ("01_Decisoes", dec), ("02_Evidencia_Y1", ev1),
                    ("03_Premissa_VMRS", premissa), ("05_Custo_por_categoria", y_por_cat),
                    ("06_Mapa_dummies", mapa_dummies),
                    ("07_Dummies_nao_criadas", nao_materializadas), ("08_Removidas", rem),
                    ("10_Mapa_dummies_id_carreta", mapa_id),
                    ("11_Comparativo_Y1_Y2", comp), ("12_Recomendado_Y1", rec_y1),
                    ("13_Recomendado_Y2", rec_y2)]:
        if len(df.columns):
            for j, c in enumerate(df.columns):
                xw.sheets[aba].write(0, j, c, fmt_h)
            xw.sheets[aba].autofilter(0, 0, max(len(df), 1), len(df.columns) - 1)

# tambem em CSV, para versionamento e rastreio
dec.to_csv(TABLES / "12_curadoria_decisoes.csv", index=False)
ev1.to_csv(TABLES / "12_associacao_Y1.csv", index=False)
mapa_dummies.to_csv(TABLES / "12_mapa_dummies.csv", index=False)
premissa.to_csv(TABLES / "12_premissa_vmrs.csv", index=False)

print("OK ->", xlsx, round(xlsx.stat().st_size / 1e6, 1), "MB")
print("dummies materializadas:", len(mapa_dummies), "| nao materializadas:",
      len(nao_materializadas), "| dummies id_carreta:", d_id.shape[1])
