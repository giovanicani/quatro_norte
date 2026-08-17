"""09 - Consolidacao da apresentacao da Fase 2.

Parte de `docs/entregas/Apresentacao_QuatroNorte_agosto.pptx` (o PowerPoint de origem do
PDF apresentado em 2026-08-05), atualiza os numeros com os resultados da Fase 2,
reconstroi as tabelas a partir de `reports/`, reexibe os slides de modelagem que estavam
ocultos e acrescenta o bloco de contrato.

Saida: `docs/entregas/Apresentacao_QuatroNorte_Fase2.pptx`.
O arquivo de origem NAO e modificado.
"""
import copy
import pandas as pd
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

ROOT = Path(__file__).resolve().parent.parent
TABLES = ROOT / "reports" / "tables"
FIG = ROOT / "reports" / "figures"
FIG_EDA = FIG / "eda"
SRC = ROOT / "docs" / "entregas" / "Apresentacao_QuatroNorte_agosto.pptx"
OUT = ROOT / "docs" / "entregas" / "Apresentacao_QuatroNorte_Fase2.pptx"


def rd(n):
    p = TABLES / n
    return pd.read_csv(p) if p.exists() else pd.DataFrame()


stats = rd("03c_stats_ppt.csv").set_index("metrica")["valor"]
metr = rd("05_metricas_modelos.csv")
cmpcfg = rd("05_comparacao_configuracoes.csv")
best = rd("05_modelo_recomendado.csv")
imp = rd("05_importancia_permutacao_random_forest.csv")
hip = rd("06_hipoteses_final.csv")
sel = rd("05_selecao_variaveis.csv")
corr = rd("03b_correlacao_com_y.csv")
eta = rd("03b_eta_categoricas.csv")
vif = rd("03b_vif.csv")
est = rd("03b_estatisticas_descritivas.csv")
val = rd("02_validacao_base_anual.csv")
rec = rd("06_recomendacoes_negocio.csv")
metr_all = rd("05_metricas_por_configuracao.csv")
exp_grp = rd("10_experimento_grupos.csv")
jan = rd("11_validacao_janelas_moveis.csv")


def sv(k):
    v = stats[k]
    try:
        return float(v)
    except (TypeError, ValueError):
        return v


def vl(chave, d="—"):
    r = val.loc[val["checagem"] == chave, "valor"]
    return r.iloc[0] if len(r) else d


best_pred = best[best["cenario"] == "preditivo"].iloc[0]
best_expl = best[best["cenario"] == "explicativo"].iloc[0]
cp = cmpcfg[cmpcfg["cenario"] == "preditivo"].iloc[0]
ce = cmpcfg[cmpcfg["cenario"] == "explicativo"].iloc[0]

NAVY = RGBColor(0x14, 0x2B, 0x45)
INK = RGBColor(0x1C, 0x24, 0x33)
ORANGE = RGBColor(0xE8, 0x71, 0x3A)
PAPER = RGBColor(0xF6, 0xF1, 0xE7)
GREY = RGBColor(0x5B, 0x63, 0x6E)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

prs = Presentation(str(SRC))
slides = list(prs.slides)
print(f"origem: {len(slides)} slides")

# ============================================================
# 1) Substituicoes de texto (numeros e afirmacoes superadas)
# ============================================================
SUBS = [
    ("223.590", "217.217"),
    ("9.859", "9.585"),
    ("CAD $ 82.428 M", f"CAD $ {sv('custo_total_real_mi')} M"),
    ("82.428", str(sv("custo_total_real_mi"))),
    ("77.18 mi nominal", f"{sv('custo_total_nominal_mi')} mi nominal"),
    ("47.666", f"{int(vl('linhas_base_anual')):,}".replace(",", ".")),
    ("1673.72", f"{sv('y_media'):.2f}"),
    ("812.55", f"{sv('y_mediana'):.2f}"),
    ("4221.76", f"{sv('y_p90'):.2f}"),
    ("Assimetria 3.79", f"Assimetria {sv('assimetria')}"),
    ("3.23% de carreta", f"{sv('share_y_zero_pct')}% de carreta"),
    # afirmacoes que se inverteram
    ("Base consolidada inicial", "Base consolidada única (29 colunas)"),
    ("Fonte inicial do estudo", "Fonte única do estudo"),
    ("Fonte inicial:", "Fonte única:"),
    ("Seleção inicial das variáveis do modelo", "Seleção das variáveis do modelo"),
    ("sugestão inicial", "decisão"),
    ("Comparação inicial dos modelos", "Comparação dos modelos"),
    ("São 25 variáveis explicativas candidatas da fonte inicial.",
     "São 29 colunas na fonte única, já incluindo o bloco de contrato."),
    ("Veredito Preliminar", "Veredito"),
    ("sem dados de contrato, mão de obra detalhada e peças — reduz o conjunto explicativo",
     "contrato incorporado na Fase 2; seguem ausentes mão de obra, peças e tipo_contrato (RENTAL/LEASE)"),
    ("Sem filtro por tipo de manutenção: analisa-se todo o custo interno.",
     "População restrita a MAINT: o ganho de R² do filtro reflete amostra mais homogênea, não melhora de previsão."),
    ("Extração SQL, modelo estrela, joins e feature engineering .",
     "Extração SQL, modelo estrela, joins e feature engineering (etapa anterior de preparação)."),
    ("*Fase 2", "✓ concluído na Fase 2"),
]

n_sub = 0
for sl in slides:
    for sh in sl.shapes:
        if not sh.has_text_frame:
            continue
        for para in sh.text_frame.paragraphs:
            for run in para.runs:
                novo = run.text
                for a, b in SUBS:
                    if a in novo:
                        novo = novo.replace(a, b)
                if novo != run.text:
                    run.text = novo
                    n_sub += 1
print(f"substituicoes de texto aplicadas em {n_sub} runs")


# ============================================================
# 2) Reconstrucao de tabelas a partir de reports/
# ============================================================
def set_cell(cell, texto, bold=None):
    tf = cell.text_frame
    p0 = tf.paragraphs[0]
    if p0.runs:
        p0.runs[0].text = str(texto)
        for r in p0.runs[1:]:
            r.text = ""
        if bold is not None:
            p0.runs[0].font.bold = bold
    else:
        cell.text = str(texto)


def clonar_linha(tbl, idx_modelo=1):
    """Duplica uma linha existente preservando formatacao."""
    tr = copy.deepcopy(tbl._tbl.tr_lst[idx_modelo])
    tbl._tbl.append(tr)


def preencher(tbl, df, cabecalho=True, ajustar=True):
    """Preenche a tabela com o df, ajustando o numero de linhas."""
    n_alvo = len(df) + (1 if cabecalho else 0)
    if ajustar:
        while len(tbl.rows) < n_alvo:
            clonar_linha(tbl)
        while len(tbl.rows) > n_alvo:
            tbl._tbl.remove(tbl._tbl.tr_lst[-1])
    ncols = len(tbl.columns)
    if cabecalho:
        for j, col in enumerate(df.columns[:ncols]):
            set_cell(tbl.cell(0, j), acentuar(col))
    off = 1 if cabecalho else 0
    for i in range(len(df)):
        for j in range(min(ncols, df.shape[1])):
            set_cell(tbl.cell(i + off, j), acentuar(df.iloc[i, j]))


def tabelas(sl):
    return [sh.table for sh in sl.shapes if sh.has_table]


ACENTOS = {
    "removida": "removida", "mantida": "mantida",
    "mantida (so explicativo)": "mantida (só explicativo)",
    "removida do modelo": "removida do modelo",
    "explicativo / inicio_ano no preditivo": "explicativo / início de ano no preditivo",
    "condicional": "condicional",
    "variavel": "variável", "decisao": "decisão", "cenario": "cenário",
    "importancia": "importância", "hipotese": "hipótese", "enunciado": "enunciado",
    "veredito": "veredito", "papel": "papel", "recomendacao": "recomendação",
    "desvio_padrao": "desvio padrão",
}


def acentuar(v):
    s_ = str(v)
    return ACENTOS.get(s_, s_)


# -- slide 5: hipoteses (agora com veredito final, H6a/H6b)
t = tabelas(slides[4])[0]
hip_v = hip[["hipotese", "enunciado", "veredito"]].copy()
hip_v.columns = ["Hipótese", "Descrição", "Veredito"]
preencher(t, hip_v)
print("slide 5: hipoteses ->", len(hip_v), "linhas")

# -- slide 11: estatisticas descritivas
t = tabelas(slides[10])[0]
cols = [c for c in ["variavel", "N", "media", "mediana", "desvio_padrao", "min", "max", "assimetria"] if c in est.columns]
ncol = len(tabelas(slides[10])[0].columns)
preencher(t, est[cols].head(16).iloc[:, :ncol])
print("slide 11: descritivas atualizadas")

# -- slide 20: correlacao e eta
tt = tabelas(slides[19])
cc = corr[["variavel", "spearman", "papel"]].sort_values("spearman", key=abs, ascending=False).head(15)
cc.columns = ["variável", "spearman", "papel"]
preencher(tt[0], cc.iloc[:, :len(tt[0].columns)])
ee = eta[["variavel", "eta", "n_categorias"]].copy()
ee.columns = ["variável", "eta", "n_categorias"]
preencher(tt[1], ee.iloc[:, :len(tt[1].columns)])
print("slide 20: correlacao/eta atualizados")

# -- slide 22: VIF
t = [x for x in tabelas(slides[21])][0]
vv = vif.copy()
vv.columns = ["variável", "vif"][: len(vv.columns)]
preencher(t, vv.iloc[:, :len(t.columns)])
print("slide 22: VIF atualizado")

# -- slide 23: selecao de variaveis (duas colunas)
tt = tabelas(slides[22])
ss = sel[["variavel", "decisao"]].copy()
ss.columns = ["variável", "decisão"]
meta = (len(ss) + 1) // 2
preencher(tt[0], ss.iloc[:meta])
preencher(tt[1], ss.iloc[meta:])
print("slide 23: selecao ->", len(ss), "variaveis")

# -- slide 27: metricas dos modelos
t = tabelas(slides[26])[0]
mm = metr.copy()
mm.columns = ["cenário", "modelo", "r2", "rmse", "mae"]
preencher(t, mm)
for sh in slides[26].shapes:
    if sh.has_text_frame and "Preditivo recomendado" in sh.text_frame.text:
        tf = sh.text_frame
        novos = [
            f"Preditivo recomendado: {best_pred['modelo']}",
            f"R² = {best_pred['r2']} · RMSE = {best_pred['rmse']}",
            f"MAE = {best_pred['mae']} CAD/ano",
            f"Explicativo (melhor): R² = {best_expl['r2']}",
            "Árvores/ensembles superam modelos lineares.",
            f"Efeito do filtro MAINT: {float(cp['delta_r2_filtro_maint']):+.4f} de R².",
            f"Efeito do contrato: {float(cp['delta_r2_contrato']):+.4f} de R² — praticamente nulo.",
        ]
        base_p = tf.paragraphs[0]
        while len(tf.paragraphs) > 1:
            tf._txBody.remove(tf.paragraphs[-1]._p)
        for i, txt in enumerate(novos):
            p = base_p if i == 0 else tf.add_paragraph()
            if p.runs:
                p.runs[0].text = "•  " + txt
                for r in p.runs[1:]:
                    r.text = ""
            else:
                r = p.add_run()
                r.text = "•  " + txt
                r.font.size = Pt(13)
                r.font.color.rgb = INK
                r.font.name = "Calibri"
print("slide 27: metricas atualizadas")

# -- slide 28: importancia por permutacao
t = tabelas(slides[27])[0]
ii = imp.head(9)[["variavel", "importancia"]].round(4).copy()
ii.columns = ["variável", "importância"]
preencher(t, ii)
for sh in slides[27].shapes:
    if sh.shape_type == 13 or sh.__class__.__name__ == "Picture":
        el = sh._element
        el.getparent().remove(el)
slides[27].shapes.add_picture(str(FIG / "05_importancia_permutacao.png"),
                              Inches(0.7), Inches(1.7), Inches(7.6), Inches(5.2))
print("slide 28: importancias atualizadas")

# (gravação no final do arquivo)


# ============================================================
# 3) Reexibir os slides de modelagem que estavam ocultos
# ============================================================
REEXIBIR = [26, 27, 28]  # 27 metricas, 28 importancias, 29 "O que dizem os dados"
for i in REEXIBIR:
    el = slides[i]._element
    if el.get("show") == "0":
        el.set("show", "1")
print("slides reexibidos:", [i + 1 for i in REEXIBIR])

# slide 29 - "O que dizem os dados": atualizar a leitura frente a literatura
for sh in slides[28].shapes:
    if not sh.has_text_frame:
        continue
    for para in sh.text_frame.paragraphs:
        for run in para.runs:
            t0 = run.text
            t1 = (t0.replace("R² 0,43 (preditivo) a 0,57 (explicativo)",
                             f"R² {float(best_pred['r2']):.2f} (preditivo) a {float(best_expl['r2']):.2f} (explicativo)")
                    .replace("regressões lineares ficam com R²<0",
                             "regressões lineares ficam muito atrás (R² ~ 0,27)")
                    .replace("idade isolada ρ=0,02", "idade isolada ρ=0,03")
                    .replace("removê-la derruba o R² em 0,22", "removê-la derruba o R² em 0,17")
                    .replace("o R² cai de 0,57 → 0,43",
                             f"o R² cai de {float(best_expl['r2']):.2f} para {float(best_pred['r2']):.2f}"))
            if t1 != t0:
                run.text = t1

# ============================================================
# 4) Novos slides da Fase 2 (mesma identidade visual)
# ============================================================
LAYOUT = next((l for l in prs.slide_layouts if l.name == "Blank"), prs.slide_layouts[6])


def novo_slide(bg=PAPER):
    sl = prs.slides.add_slide(LAYOUT)
    r = sl.shapes.add_shape(1, 0, 0, prs.slide_width, prs.slide_height)
    r.fill.solid()
    r.fill.fore_color.rgb = bg
    r.line.fill.background()
    r.shadow.inherit = False
    sl.shapes._spTree.remove(r._element)
    sl.shapes._spTree.insert(2, r._element)
    return sl


def txt(sl, x, y, w, h, texto, size=16, cor=INK, bold=False):
    box = sl.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    for i, linha in enumerate(str(texto).split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        r = p.add_run()
        r.text = linha
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.color.rgb = cor
        r.font.name = "Calibri"
    return box


def cabecalho(sl, kicker, titulo):
    bar = sl.shapes.add_shape(1, Inches(0.6), Inches(0.55), Inches(0.16), Inches(0.9))
    bar.fill.solid()
    bar.fill.fore_color.rgb = ORANGE
    bar.line.fill.background()
    bar.shadow.inherit = False
    txt(sl, 0.9, 0.5, 11.8, 0.4, kicker.upper(), 12, ORANGE, True)
    txt(sl, 0.9, 0.86, 11.8, 0.9, titulo, 27, NAVY, True)


def marcadores(sl, x, y, w, h, itens, size=15):
    box = sl.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    for i, it in enumerate(itens):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(7)
        r = p.add_run()
        r.text = "•  " + it
        r.font.size = Pt(size)
        r.font.color.rgb = INK
        r.font.name = "Calibri"
    return box


def nova_tabela(sl, df, x, y, w, h, fs=11):
    nr, nc = df.shape
    gt = sl.shapes.add_table(nr + 1, nc, Inches(x), Inches(y), Inches(w), Inches(h)).table
    for j, col in enumerate(df.columns):
        c = gt.cell(0, j)
        c.text = str(col)
        c.fill.solid()
        c.fill.fore_color.rgb = NAVY
        p = c.text_frame.paragraphs[0]
        p.runs[0].font.size = Pt(fs)
        p.runs[0].font.bold = True
        p.runs[0].font.color.rgb = WHITE
        p.runs[0].font.name = "Calibri"
    for i in range(nr):
        for j in range(nc):
            c = gt.cell(i + 1, j)
            c.text = str(df.iloc[i, j])
            c.fill.solid()
            c.fill.fore_color.rgb = WHITE if i % 2 == 0 else RGBColor(0xEE, 0xEA, 0xDE)
            p = c.text_frame.paragraphs[0]
            if p.runs:
                p.runs[0].font.size = Pt(fs)
                p.runs[0].font.color.rgb = INK
                p.runs[0].font.name = "Calibri"
    return gt


def kpi(sl, x, y, w, h, valor, rotulo, cor=ORANGE):
    c = sl.shapes.add_shape(1, Inches(x), Inches(y), Inches(w), Inches(h))
    c.fill.solid()
    c.fill.fore_color.rgb = WHITE
    c.line.color.rgb = NAVY
    c.shadow.inherit = False
    txt(sl, x + 0.2, y + 0.08, w - 0.4, 0.45, valor, 22, cor, True)
    txt(sl, x + 0.2, y + 0.58, w - 0.4, 0.30, rotulo, 11, GREY)


novos = []

# A. Os quatro campos de contrato
sl = novo_slide()
novos.append(("contrato_campos", sl))
cabecalho(sl, "Fase 2 · dados novos", "Contrato: os quatro campos que chegaram à base")
txt(sl, 0.9, 1.68, 11.6, 0.4,
    "H6 estava declarada desde a fase anterior, sem dados para testá-la. Os campos de contrato passaram a integrar a fonte única.",
    12, GREY)
campos = pd.DataFrame([
    {"campo": "tempo_contrato_meses_ate_reparo", "cobertura": "92,5%",
     "perfil": "mediana 35,1 meses · sem valores negativos", "destino": "MODELADA — responde H6a"},
    {"campo": "tipo_manutencao", "cobertura": "92,5%",
     "perfil": "MAINT 89,7% · MIX 1,6% · NET 1,1%", "destino": "define a população; H6b na EDA"},
    {"campo": "cod_cliente", "cobertura": "77,2%",
     "perfil": "597 clientes distintos", "destino": "descritiva — fora do modelo"},
    {"campo": "franquia_km_mensal_contrato", "cobertura": "71,6%",
     "perfil": "99,8% dos preenchidos são ZERO", "destino": "DESCARTADA — variância nula"},
])
nova_tabela(sl, campos, 0.7, 2.2, 12.0, 2.2, fs=11)
marcadores(sl, 0.9, 4.8, 11.6, 2.1, [
    "A fonte permanece ÚNICA: os campos vieram dentro do próprio CSV consolidado, sem join novo.",
    "Contrato não é atributo fixo do ativo — 51,5% das carretas mudam de regime no período, o que exigiu agregação por carreta-ano.",
    "Retomamos o filtro MAINT do desenho original, agora como flag: a base guarda tudo e a modelagem seleciona.",
], 14)

# B. EDA de contrato
sl = novo_slide()
novos.append(("contrato_eda", sl))
cabecalho(sl, "Fase 2 · EDA de contrato", "Distribuições das variáveis de contrato")
for nome, fx, fy in [("quant_tempo_contrato_meses_fim_ano.png", 0.8, 1.8),
                     ("quant_share_maint_ano.png", 6.9, 1.8),
                     ("quant_n_clientes_ano.png", 0.8, 4.4),
                     ("quant_trocou_contrato_ano.png", 6.9, 4.4)]:
    p = FIG_EDA / nome
    if p.exists():
        sl.shapes.add_picture(str(p), Inches(fx), Inches(fy), height=Inches(2.4))

# C. Boxplot por regime contratual (H6b)
sl = novo_slide()
novos.append(("contrato_h6b", sl))
cabecalho(sl, "Fase 2 · EDA de contrato", "Custo anual por regime contratual — evidência de H6b")
p = FIG_EDA / "quali_tipo_manutencao_ano.png"
if p.exists():
    sl.shapes.add_picture(str(p), Inches(0.9), Inches(1.85), height=Inches(4.9))
_et = eta.loc[eta["variavel"] == "tipo_manutencao_ano", "eta"]
_et = float(_et.iloc[0]) if len(_et) else float("nan")
marcadores(sl, 8.6, 2.0, 4.2, 4.6, [
    f"eta = {_et:.3f}: separação fraca entre regimes.",
    "MAINT concentra 89,7% das OS; NET e MIX somam 2,7% — baixa potência estatística.",
    "Avaliado sobre a base COMPLETA: dentro da população MAINT a variável é constante.",
    "Diferença entre regimes pode refletir quem paga o reparo, não quanto ele custa.",
], 13)

# D. Como isolamos o efeito de cada mudanca
sl = novo_slide()
novos.append(("configs", sl))
cabecalho(sl, "Fase 2 · desenho da modelagem", "Como isolamos o efeito de cada mudança")
txt(sl, 0.9, 1.68, 11.6, 0.4,
    "A base foi reextraída E ganhou contrato na mesma rodada. Sem separar as causas, qualquer ganho de R² seria ambíguo.",
    12, GREY)
cfgs = pd.DataFrame([
    {"configuração": "A — baseline", "população": "todas as carretas", "variáveis": "sem contrato",
     "responde": "efeito da nova extração"},
    {"configuração": "B — filtro", "população": "somente MAINT", "variáveis": "sem contrato",
     "responde": "efeito do filtro de contrato"},
    {"configuração": "C — completa", "população": "somente MAINT", "variáveis": "com contrato",
     "responde": "efeito das variáveis novas"},
])
nova_tabela(sl, cfgs, 0.9, 2.2, 11.6, 1.7, fs=12)
kpi(sl, 0.9, 4.3, 3.5, 1.15, f"{float(cp['A_todos_sem_contrato__r2']):.4f}", "A · R² preditivo", NAVY)
kpi(sl, 4.8, 4.3, 3.5, 1.15, f"{float(cp['B_maint_sem_contrato__r2']):.4f}", "B · R² preditivo (MAINT)", NAVY)
kpi(sl, 8.7, 4.3, 3.5, 1.15, f"{float(cp['C_maint_com_contrato__r2']):.4f}", "C · R² preditivo (+ contrato)", ORANGE)
txt(sl, 0.9, 5.75, 11.6, 0.5,
    f"Efeito do filtro MAINT: {float(cp['delta_r2_filtro_maint']):+.4f} de R²         "
    f"Efeito das variáveis de contrato: {float(cp['delta_r2_contrato']):+.4f} de R²", 16, NAVY, True)
txt(sl, 0.9, 6.35, 11.6, 0.7,
    "O ganho do filtro não é melhora de previsão: as carreta-anos excluídas têm custo médio bem menor e muitas têm custo zero.\n"
    "Amostra mais homogênea eleva o R² sem que o modelo preveja melhor.", 12, GREY)

# E. Implicacoes gerenciais
sl = novo_slide()
novos.append(("implicacoes", sl))
cabecalho(sl, "Item 13 · implicações gerenciais", "O que a empresa faz com estes resultados")
if not rec.empty:
    nova_tabela(sl, rec, 0.7, 1.9, 12.0, 4.2, fs=10)
txt(sl, 0.7, 6.35, 12.0, 0.6,
    f"Erro médio do modelo recomendado: CAD $ {best_pred['mae']}/ano por carreta — margem a declarar ao usar a estimativa em orçamento.",
    13, NAVY, True)

# F. Conclusoes
sl = novo_slide()
novos.append(("conclusoes", sl))
cabecalho(sl, "Item 16 · conclusões", "Resposta à pergunta de pesquisa")
c = sl.shapes.add_shape(1, Inches(0.9), Inches(1.8), Inches(11.5), Inches(1.45))
c.fill.solid()
c.fill.fore_color.rgb = NAVY
c.line.fill.background()
c.shadow.inherit = False
txt(sl, 1.2, 1.95, 11.0, 1.25,
    "O custo anual real por carreta é explicado sobretudo por REFRIGERAÇÃO, HISTÓRICO DE MANUTENÇÃO e USO.\n"
    f"O modelo {best_pred['modelo']} estima o custo do ano seguinte com R² = {best_pred['r2']} "
    f"e erro médio de CAD $ {best_pred['mae']}/ano.", 16, WHITE, True)
marcadores(sl, 0.9, 3.5, 11.6, 3.3, [
    f"O grão anual eliminou a zero-inflação que travava as formulações anteriores ({sv('share_y_zero_pct')}% de carreta-anos com custo zero).",
    "A idade isolada NÃO explica o custo: atua por meio do histórico e do uso.",
    "As variáveis de contrato, incorporadas nesta fase, mostraram efeito fraco — hipótese testada, não assumida.",
    "O contrato serviu principalmente para DEFINIR a população de análise (MAINT), não para prever o custo.",
    "O modelo é utilizável para orçamento e priorização, desde que a margem de erro seja declarada.",
], 14)


# ---- G. Linha do tempo: o que mudou desde a apresentação ----
sl = novo_slide()
novos.append(("linha_do_tempo", sl))
cabecalho(sl, "Fase 2 · o que mudou", "Linha do tempo desde a apresentação de agosto")
txt(sl, 0.9, 1.68, 11.6, 0.4,
    "A Fase 1 encerrou na seleção de variáveis, com a modelagem marcada como Fase 2. Um dado novo mudou o que era possível testar.",
    12, GREY)
linha = pd.DataFrame([
    {"quando": "05/ago", "o que aconteceu": "Apresentação da Fase 1 (28 slides)",
     "situação": "H6 declarada, sem dados; Gate 4 em aberto"},
    {"quando": "16/ago", "o que aconteceu": "Base reextraída, com dados de contrato",
     "situação": "25 → 29 colunas · 223.590 → 217.217 OS · 9.859 → 9.585 carretas"},
    {"quando": "16/ago", "o que aconteceu": "População redefinida (retomada do filtro MAINT)",
     "situação": f"{vl('carreta_ano_populacao_maint')} carreta-anos sob contrato com manutenção inclusa"},
    {"quando": "16/ago", "o que aconteceu": "Modelagem executada em 3 configurações",
     "situação": "efeito do filtro +0,0193 de R²; efeito do contrato +0,0033"},
    {"quando": "16/ago", "o que aconteceu": "Experimento: modelo único × dividido por refrigeração",
     "situação": "validado em 3 anos de teste (2023, 2024, 2025)"},
])
nova_tabela(sl, linha, 0.7, 2.2, 12.0, 2.7, fs=11)
marcadores(sl, 0.9, 5.3, 11.6, 1.6, [
    "A fonte permanece ÚNICA: o contrato veio dentro do próprio CSV consolidado, sem join novo.",
    "Todos os slides da apresentação anterior foram mantidos, na mesma ordem — os números é que foram atualizados.",
], 14)

# ---- I. Resultados preliminares — 1ª tentativa (sem variáveis de contrato) ----
sl = novo_slide()
novos.append(("preliminar1", sl))
cabecalho(sl, "Item 12 · resultados preliminares", "1ª tentativa — sem as variáveis de contrato")
txt(sl, 0.9, 1.65, 11.6, 0.45,
    "É o desenho da apresentação anterior: um modelo único, sem qualquer informação de contrato. Recalculado sobre a base reextraída.",
    12, GREY)
if not metr_all.empty:
    mA_ = metr_all[metr_all["config"] == "A_todos_sem_contrato"][["cenario", "modelo", "r2", "rmse", "mae"]]
    mA_ = mA_.sort_values(["cenario", "r2"], ascending=[True, False])
    mA_.columns = ["cenário", "modelo", "R²", "RMSE", "MAE"]
    nova_tabela(sl, mA_, 0.7, 2.2, 7.5, 4.3, fs=9)
    _bp = metr_all[(metr_all["config"] == "A_todos_sem_contrato") & (metr_all["cenario"] == "preditivo")].sort_values("rmse").iloc[0]
    _be = metr_all[(metr_all["config"] == "A_todos_sem_contrato") & (metr_all["cenario"] == "explicativo")].sort_values("rmse").iloc[0]
    kpi(sl, 8.5, 2.3, 4.2, 1.15, f"{float(_bp['r2']):.4f}", f"melhor preditivo ({_bp['modelo']})", ORANGE)
    kpi(sl, 8.5, 3.65, 4.2, 1.15, f"{float(_be['r2']):.4f}", f"melhor explicativo ({_be['modelo']})", NAVY)
    marcadores(sl, 8.5, 5.05, 4.3, 1.7, [
        "Árvores e ensembles superam os lineares.",
        "Fatores dominantes: refrigeração, histórico defasado e uso.",
    ], 12)

# ---- J. Resultados preliminares — 2ª tentativa (contrato + divisão) ----
sl = novo_slide()
novos.append(("preliminar2", sl))
cabecalho(sl, "Item 12 · resultados preliminares", "2ª tentativa — contrato incluído e divisão por refrigeração")
txt(sl, 0.9, 1.62, 11.6, 0.45,
    "Duas mudanças testadas nesta fase: (a) incluir as variáveis de contrato; (b) treinar um modelo para refrigeradas e outro para secas.",
    12, GREY)
comp = []
if cp is not None:
    comp.append({"o que foi testado": "(a) incluir variáveis de contrato",
                 "R² preditivo": f"{float(cp['B_maint_sem_contrato__r2']):.4f} → {float(cp['C_maint_com_contrato__r2']):.4f}",
                 "diferença": f"{float(cp['delta_r2_contrato']):+.4f}",
                 "veredito": "efeito desprezível"})
if not exp_grp.empty:
    _g = exp_grp[(exp_grp["cenario"] == "preditivo") & (exp_grp["modelo"] == "gradient_boosting")].iloc[0]
    comp.append({"o que foi testado": "(b) dividir por refrigeração (teste 2025)",
                 "R² preditivo": f"{float(_g['r2_unico']):.4f} → {float(_g['r2_por_grupo']):.4f}",
                 "diferença": f"{float(_g['delta_r2']):+.4f}",
                 "veredito": "promissor — exigiu validação"})
if comp:
    nova_tabela(sl, pd.DataFrame(comp), 0.7, 2.25, 12.0, 1.5, fs=12)
marcadores(sl, 0.9, 4.1, 11.6, 2.6, [
    "As variáveis de contrato quase não acrescentam poder preditivo: +0,0033 de R², contra +0,0193 apenas por restringir a população a MAINT.",
    "Como flag_refrigerado é a variável mais importante do modelo (0,169), testamos tratá-la como grupo — a lógica do MERF de Katreddi (2023).",
    "Testando só em 2025, dividir parecia vencer com folga (bootstrap de 2.000 reamostragens: 99,6% de probabilidade de ganho).",
    "Mas esse bootstrap mede apenas o ruído DENTRO de um ano. A validação em vários anos vem a seguir — e muda a conclusão.",
], 13)

# ---- K. Resultados finais ----
sl = novo_slide()
novos.append(("finais", sl))
cabecalho(sl, "Item 12 · resultados finais", "Qual modelo mantemos")
txt(sl, 0.9, 1.62, 11.6, 0.45,
    "O mesmo confronto repetido com três anos de teste, cada um treinado só com os anos anteriores.",
    12, GREY)
if not jan.empty:
    jt = jan[["ano_teste", "modelo", "r2_unico", "r2_por_grupo", "delta_r2"]].copy()
    jt.columns = ["ano de teste", "modelo", "único", "dividido", "diferença"]
    nova_tabela(sl, jt, 0.7, 2.15, 7.4, 2.9, fs=10)
marcadores(sl, 8.3, 2.25, 4.5, 2.9, [
    "No Gradient Boosting o ganho INVERTE de sinal em 2023.",
    "No Random Forest é consistente, mas cai para +0,003 em dois dos três anos.",
    "A variação entre anos é maior que o ganho medido em 2025.",
], 12)
c = sl.shapes.add_shape(1, Inches(0.7), Inches(5.35), Inches(12.0), Inches(1.65))
c.fill.solid()
c.fill.fore_color.rgb = NAVY
c.line.fill.background()
c.shadow.inherit = False
_txt_final = (f"MANTEMOS O MODELO ÚNICO — {best_pred['modelo']}, R² = {best_pred['r2']} · "
              f"RMSE = {best_pred['rmse']} · MAE = {best_pred['mae']} CAD/ano.\n"
              "Dividir por refrigeração não se sustenta fora de 2025, e dobraria o número de modelos a treinar e monitorar.\n"
              "As variáveis de contrato permanecem no modelo: o efeito é pequeno, mas registram o teste de H6 e não custam nada.")
txt(sl, 1.0, 5.5, 11.4, 1.45, _txt_final, 13, WHITE, True)


# ============================================================
# 5) Reordenar os novos slides para as posicoes certas
# ============================================================
sldIdLst = prs.slides._sldIdLst


def id_do_slide(sl):
    for x in list(sldIdLst):
        if prs.part.related_part(x.rId) is sl.part:
            return x
    raise ValueError("slide nao encontrado no sldIdLst")


# ---- L. Item 14 — Limitações atualizadas na Fase 2 ----
sl = novo_slide()
novos.append(("limitacoes_f2", sl))
cabecalho(sl, "Item 14 · limitações", "O que mudou nas limitações após a Fase 2")
txt(sl, 0.9, 1.62, 11.6, 0.45,
    "As limitações declaradas em agosto continuam válidas, exceto as que esta fase resolveu — e há três novas, criadas pelas próprias escolhas da Fase 2.",
    12, GREY)
lim = pd.DataFrame([
    {"limitação declarada em agosto": "Sem dados de contrato — reduz o conjunto explicativo",
     "situação após a Fase 2": "RESOLVIDA — contrato incorporado e H6 testada"},
    {"limitação declarada em agosto": "Sem filtro por tipo de manutenção",
     "situação após a Fase 2": "RESOLVIDA — população MAINT retomada, como flag"},
    {"limitação declarada em agosto": "km derivado do odômetro; província parcial (~54%)",
     "situação após a Fase 2": "permanece"},
])
nova_tabela(sl, lim, 0.7, 2.2, 12.0, 1.7, fs=11)
txt(sl, 0.9, 4.15, 11.6, 0.4, "Limitações novas, decorrentes das escolhas desta fase:", 14, NAVY, True)
marcadores(sl, 0.9, 4.6, 11.6, 2.3, [
    "A população MAINT é mais homogênea: o ganho de R² do filtro (+0,0193) reflete amostra mais fácil, não previsão melhor.",
    "NET e MIX somam 2,7% das OS — conclusões sobre esses regimes têm baixa potência estatística.",
    "cod_cliente não foi modelado (597 categorias) e franquia_km_mensal_contrato foi descartada (99,8% de zeros).",
    "A avaliação usa um ano de teste por vez; a variação entre anos mostrou-se maior que os ganhos medidos dentro de um ano.",
], 13)

# ---- M. Item 15 — Recomendações para projetos futuros ----
sl = novo_slide()
novos.append(("futuros", sl))
cabecalho(sl, "Item 15 · projetos futuros", "Recomendações para as próximas etapas")
txt(sl, 0.9, 1.62, 11.6, 0.45,
    "Contrato sai desta lista: deixou de ser trabalho futuro e virou resultado.",
    12, GREY)
fut = pd.DataFrame([
    {"frente": "Dados", "recomendação": "Integrar mão de obra e peças para decompor o custo por origem; incorporar tipo_contrato (RENTAL/LEASE), único campo de contrato ainda ausente"},
    {"frente": "Modelagem", "recomendação": "Testar Mixed Effects Random Forest (Katreddi, 2023) como alternativa à divisão manual por grupo, que não se sustentou entre anos"},
    {"frente": "Avaliação", "recomendação": "Adotar validação com janelas móveis como padrão — foi ela que evitou adotar um ganho aparente medido em um único ano"},
    {"frente": "Alvo", "recomendação": "Modelar a cauda de custos extremos: a assimetria de 3,82 é o limite estrutural do R² atual"},
    {"frente": "Exposição", "recomendação": "Incorporar quilometragem planejada e telemetria (GPS) como medida de uso"},
])
nova_tabela(sl, fut, 0.7, 2.2, 12.0, 3.6, fs=11)
txt(sl, 0.7, 6.1, 12.0, 0.7,
    "A prioridade é a decomposição do custo por origem (mão de obra × peças): é o que permitiria dizer não só quanto custa, mas por quê.",
    13, NAVY, True)

# Os 34 slides apresentados em agosto permanecem CONTIGUOS e na ordem original.
# Todos os slides da Fase 2 entram DEPOIS deles, na sequencia das perguntas da disciplina.
ORDEM_FASE2 = [
    "linha_do_tempo",     # abertura do bloco: o que mudou
    "contrato_campos",    # dados novos
    "contrato_eda",       # EDA de contrato
    "contrato_h6b",       # EDA de contrato (H6b)
    "configs",            # desenho da modelagem
    "preliminar1",        # item 12 - 1a tentativa
    "preliminar2",        # item 12 - 2a tentativa
    "finais",             # item 12 - resultados finais
    "implicacoes",        # item 13
    "limitacoes_f2",      # item 14
    "futuros",            # item 15
    "conclusoes",         # item 16
]
mapa = dict(novos)
for chave in ORDEM_FASE2:
    el = id_do_slide(mapa[chave])
    sldIdLst.remove(el)
    sldIdLst.append(el)
print(f"bloco da Fase 2 anexado ao final: {len(ORDEM_FASE2)} slides")

def slide_dos_gates():
    """Localiza o slide de Gates pelo conteudo — a posicao muda quando o bloco da
    Fase 2 e anexado ao final."""
    for sl in prs.slides:
        for sh in sl.shapes:
            if sh.has_text_frame and "Entregas do Projeto" in sh.text_frame.text:
                return sl
    raise ValueError("slide de Gates nao encontrado")


# ============================================================
# 6) Gates: fechar Gate 4 e registrar o contrato
# ============================================================
gates_sl = slide_dos_gates()
for sh in gates_sl.shapes:
    if not sh.has_text_frame:
        continue
    for p in sh.text_frame.paragraphs:
        for r in p.runs:
            if "Resultados promissores" in r.text:
                r.text = (f"Gradient Boosting: R² {best_pred['r2']} (preditivo) e "
                          f"{best_expl['r2']} (explicativo) no teste temporal de 2025.")
            elif "Fatores: n" in r.text and "VMRS" in r.text:
                r.text = "Fatores: refrigeração, histórico defasado, exposição acumulada e subtipo."
            elif "Verificar estabilidade por ano de teste" in r.text:
                r.text = ("Contrato incorporado e testado: H6a e H6b com efeito fraco "
                          f"({float(cp['delta_r2_contrato']):+.4f} de R²).")


# ============================================================
# 7) Correcoes de revisao (2026-08-16)
# ============================================================
# Aplicadas sobre TODOS os slides, inclusive os acrescentados nesta fase.

CORRECOES_TEXTO = [
    # -- afirmacao que contradiz o resultado final: a segmentacao nao se sustentou --
    ("→ tratar a frota por grupos (refrigerada × seca), como no MERF, melhora a previsão.",
     "→ a relevância da refrigeração motivou testar modelos por grupo; o ganho, porém, "
     "não se mostrou estável entre os anos."),
    # -- metodologia superada (slide oculto 'Desenho do estudo') --
    ("População: todo o custo interno; sem filtro MAINT, pois o dado de contrato não existe na fonte única.",
     "População principal: contrato com manutenção inclusa (MAINT), aplicada como flag; "
     "o cenário sem filtro é mantido como baseline de comparação."),
    ("Universo de variáveis: 25 candidatas da fonte — atributos do ativo, uso/quilometragem, geografia e histórico defasado.",
     "Universo de variáveis: fonte única com 29 colunas — atributos do ativo, uso/quilometragem, "
     "geografia, histórico defasado e contrato (H6 avaliada nesta fase)."),
    # -- moeda errada e mistura de limite do grafico com maximo dos dados --
    ("Distribuição fortemente assimétrica à direita — a maioria dos veículos custa pouco (mediana ~R$ 1.000) "
     "e uma cauda longa de outliers chega a R$ 12.000.",
     "Distribuição fortemente assimétrica à direita — a maioria das carretas custa pouco "
     "(mediana CAD 812/ano). O eixo do gráfico é cortado em ~CAD 12.000 (p99 = 11.804), "
     "mas a cauda real vai até CAD 62.231."),
    # -- KNN faltando na lista de tecnicas --
    ("Machine Learning: árvore de decisão, Random Forest, Gradient Boosting.",
     "Machine Learning: árvore de decisão, Random Forest, Gradient Boosting e KNN."),
    # -- afirmacao forte demais sobre zero-inflacao --
    ("O grão anual eliminou a zero-inflação que travava as formulações anteriores "
     f"({sv('share_y_zero_pct')}% de carreta-anos com custo zero).",
     f"O grão anual reduziu a zero-inflação a {sv('share_y_zero_pct')}%, deixando-a residual para a modelagem."),
]

# -- numeracao das secoes: sequencia unica e sem duplicidade --
RENUMERA = {
    # unica correcao no bloco de agosto: duplicidade de secao no referencial
    "12 · REFERENCIAL TEÓRICO": "11 · REFERENCIAL TEÓRICO",
}

def substituir_no_paragrafo(par, de, para):
    """Substitui texto que pode estar dividido em varios runs, preservando o formato
    do primeiro run do paragrafo."""
    inteiro = "".join(r.text for r in par.runs)
    if de not in inteiro:
        return False
    novo_txt = inteiro.replace(de, para)
    if not par.runs:
        return False
    par.runs[0].text = novo_txt
    for r in par.runs[1:]:
        r.text = ""
    return True


n_corr = 0
for sl in prs.slides:
    for sh in sl.shapes:
        if not sh.has_text_frame:
            continue
        bruto = sh.text_frame.text.strip()
        if bruto in RENUMERA:
            for p_ in sh.text_frame.paragraphs:
                if substituir_no_paragrafo(p_, bruto, RENUMERA[bruto]):
                    n_corr += 1
            continue
        for p_ in sh.text_frame.paragraphs:
            for a, b in CORRECOES_TEXTO:
                if substituir_no_paragrafo(p_, a, b):
                    n_corr += 1
print(f"correcoes de revisao aplicadas: {n_corr}")

# -- Gates: status coerente (Gate 4 e Gate 5 concluidos; so o Gate 6 fica pendente) --
gates_sl = slide_dos_gates()
STATUS = {(3.88, 11.36): "Concluída",   # Gate 4 - Modelo anual de custo
          (5.29, 5.18): "Concluída"}    # Gate 5 - Validacao e robustez
for sh in gates_sl.shapes:
    if not sh.has_text_frame:
        continue
    if sh.text_frame.text.strip() not in ("Próximos passos", "Concluída"):
        continue
    top_in = round(sh.top / 914400, 2)
    left_in = round(sh.left / 914400, 2)
    for (t_, l_), novo_status in STATUS.items():
        if abs(top_in - t_) < 0.06 and abs(left_in - l_) < 0.06:
            for p_ in sh.text_frame.paragraphs:
                for r_ in p_.runs:
                    r_.text = novo_status
            print(f"  gate em (top={t_}, left={l_}) -> {novo_status}")

# ordem de leitura: no XML o bloco do Gate 6 vem antes do Gate 5. Reposiciona os
# elementos para que a ordem do arquivo acompanhe a ordem visual (esquerda -> direita).
spTree = gates_sl.shapes._spTree
blocos = [sh for sh in gates_sl.shapes if sh.has_text_frame and sh.top is not None
          and abs(sh.top / 914400 - 5.28) < 0.45]
if blocos:
    for sh in sorted(blocos, key=lambda s: (s.left, s.top)):
        el = sh._element
        spTree.remove(el)
        spTree.append(el)
    print("  ordem de leitura dos Gates 5/6 normalizada")


# ============================================================
# 8) Correcoes de PRECISAO (revisao 2026-08-16)
# ============================================================
PRECISAO = [
    # -- 1. definicao da populacao: escopo do custo != populacao de modelagem --
    ("Escopo: todo o custo interno absorvido pela empresa (preventiva + corretiva).",
     "Escopo do custo: todo o custo interno absorvido pela empresa (preventiva + corretiva). "
     "População de modelagem: as carretas sob contrato com manutenção inclusa (MAINT) — "
     "41.739 dos 47.715 carreta-anos."),

    # -- 2. janela temporal: 6 anos de dados, 5 modelaveis --
    ("Fonte única   — CSV consolidado fato_wo_ml (217.217 OS · 9.585 carretas únicas).",
     "Fonte única — CSV consolidado fato_wo_ml (217.217 OS · 9.585 carretas · 2020–2025)."),
    ("Base carreta × ano   —  define o alvo Y = custo anual de manutenção por carreta (47.715 linhas).",
     "Base carreta × ano — alvo Y = custo anual por carreta (47.715 linhas; 41.739 na população MAINT). "
     "São 6 anos de dados, mas só 5 modeláveis: 2020 não tem ano anterior para as variáveis defasadas."),
    ("Modelagem — split temporal   —  treino 2020–2024 / teste 2025; lineares, árvores e ensembles.",
     "Modelagem — split temporal — treino 2020–2024 / teste 2025; validação adicional com 2023 e 2024 "
     "como anos de teste; lineares, árvores e ensembles."),

    # -- 3. importancia por permutacao: embaralhar != remover --
    ("Refrigeração é o que mais pesa: carretas refrigeradas custam mais e são a variável nº 1 do modelo "
     "(removê-la derruba o R² em 0,17).",
     "Refrigeração é a variável nº 1 do modelo: embaralhar seus valores reduz o R² em 0,17 "
     "(importância por permutação). Isso mede a dependência do modelo ajustado — não equivale a "
     "retreinar sem a variável."),

    # -- 8. inferencias atribuidas a literatura --
    ("→ custo × operação é não linear, como no Super Learner de Katreddi (R²≈97%).",
     "→ a relação custo × operação é não linear, como reporta Katreddi (2023). O R² de 97% daquele "
     "estudo não é comparável ao nosso: outra frota, outro alvo e outra unidade."),
    ("→ confirma Sun (histórico prevê custo); a idade sozinha não manda.",
     "→ resultado consistente com Sun (2024), que usa o histórico para prever custo; aqui a idade, "
     "isolada, tem associação fraca."),
    ("→ número honesto; avaliação temporal como defende a literatura.",
     "→ a queda mostra quanto do R² explicativo vinha de variáveis do próprio ano; a avaliação "
     "temporal segue a prática recomendada na literatura."),

    # -- 5. conclusao sobre idade: mediacao nao foi testada --
    ("A idade isolada NÃO explica o custo: atua por meio do histórico e do uso.",
     "A idade, isoladamente, tem associação fraca com o custo (ρ = 0,03) e baixa importância no modelo. "
     "Não testamos se o efeito da idade é mediado por histórico e uso — é hipótese, não resultado."),

    # -- 4 e 6. MAE e alegacao de aplicacao operacional --
    ("O modelo é utilizável para orçamento e priorização, desde que a margem de erro seja declarada.",
     "O erro médio (MAE) é de CAD 1.093/ano, cerca de 51% do custo médio do ano de teste: o modelo "
     "serve para PRIORIZAR carretas e para provisionar no agregado da frota, não para estimar o "
     "valor de um ativo isolado."),
    ("Erro médio do modelo recomendado: CAD $ 1092.7/ano por carreta — margem a declarar ao usar a "
     "estimativa em orçamento.",
     "MAE = CAD 1.093/ano por carreta — é o erro MÉDIO, não um limite: metade dos casos erra menos e a "
     "cauda erra muito mais. Equivale a ~51% do custo médio do ano de teste (CAD 2.151)."),
    ("Aplicação ao planejamento   —  apoia o controle dos custos internos e a elaboração de orçamentos "
     "mais aderentes à idade, às especificações e à aplicação de cada equipamento da frota.",
     "Aplicação ao planejamento — apoia a priorização de carretas e o provisionamento agregado por "
     "perfil de frota; o erro por ativo isolado é alto demais para orçamento individual."),
    ("Deployment e atualização contínua   —  disponibiliza os scripts de ML para integração com APIs "
     "que alimentem o pipeline trimestralmente, permitindo revalidar e atualizar os resultados do modelo.",
     "Deployment e atualização — o pipeline é reprodutível ponta a ponta pelos notebooks; a integração "
     "com APIs e a atualização periódica são etapa futura, ainda não implementada."),

    # -- 7. Gates: descrever o que foi de fato entregue --
    ("Resultados promissores, superiores aos modelos lineares no teste temporal.",
     "Gradient Boosting: R² 0,455 (preditivo) e 0,585 (explicativo) no teste 2025; lineares ficam em ~0,27."),
    ("Fatores: nº de OS, VMRS, custo acumulado, subtipo, km e região.",
     "Fatores dominantes: refrigeração, histórico defasado, exposição acumulada e subtipo."),
    ("Verificar estabilidade por ano de teste, região, tipo de carreta e perfil de manutenção.",
     "FEITO: estabilidade verificada com 3 anos de teste (2023–2025) e contrato testado (H6a/H6b, efeito fraco)."),
    ("Testar sensibilidade a outliers, seleção de variáveis e hiperparâmetros.",
     "PENDENTE: sensibilidade a outliers, seleção de variáveis e hiperparâmetros."),
    ("Avaliar extensões: MERF, modelos hierárquicos e abordagens zero-infladas.",
     "PENDENTE: MERF e modelos hierárquicos — a divisão manual por grupo foi testada e não se sustentou."),
]

n_prec = 0
for sl in prs.slides:
    for sh in sl.shapes:
        if not sh.has_text_frame:
            continue
        for p_ in sh.text_frame.paragraphs:
            for a, b in PRECISAO:
                if substituir_no_paragrafo(p_, a, b):
                    n_prec += 1
print(f"correcoes de precisao aplicadas: {n_prec}")

# Gate 5 nao esta concluido: parte do escopo segue pendente
for sh in slide_dos_gates().shapes:
    if not sh.has_text_frame:
        continue
    if sh.text_frame.text.strip() != "Concluída":
        continue
    if abs(sh.top / 914400 - 5.29) < 0.06 and abs(sh.left / 914400 - 5.18) < 0.06:
        for p_ in sh.text_frame.paragraphs:
            substituir_no_paragrafo(p_, "Concluída", "Parcial")
        print("  Gate 5 -> Parcial (validação feita; robustez pendente)")

OUT.parent.mkdir(parents=True, exist_ok=True)
prs.save(str(OUT))
print(f"OK: {OUT.name} - {len(prs.slides._sldIdLst)} slides")
