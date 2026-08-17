# Entregas — Apresentações Acadêmicas

> ⚠️ **IMPORTANTE:** Ver [`_NOTA_SOBRE_VERSOES.md`](_NOTA_SOBRE_VERSOES.md) para status de cada arquivo.

## ✅ ENTREGA APRESENTADA — Fase 1

**`Apresentacao_QuatroNorte.pdf`** — **28 páginas · apresentado em 2026-08-05**
**`Apresentacao_QuatroNorte_agosto.pptx`** — PowerPoint de origem (34 slides, 6 ocultos)

Este é o artefato que **foi efetivamente apresentado** e a base de continuidade do
projeto. Não é exportação do `.pptx` abaixo: é uma peça **editada manualmente**, com
estrutura própria (seções 01–15), texto acentuado, comentário analítico por gráfico,
referencial teórico em tabela de 4 colunas e um slide final de **Gates de entrega**.

Características que definem a continuidade:

- Cobre os **itens 1–11** da rubrica (contexto → metodologia).
- **Declara-se Fase 1**: fala em "fonte **inicial**", "base consolidada **inicial**",
  "seleção **inicial** das variáveis", "sugestão **inicial**", e marca modelagem e
  avaliação com `*Fase 2` no fluxograma metodológico (p. 6).
- **H6 — "Contrato (duração/tipo) influencia o custo"** já consta da tabela de
  hipóteses (p. 5), aguardando dados. **Esses dados chegaram em 2026-08-16.**
- **Não traz resultados de modelagem** — sem tabela de métricas e sem importâncias.
  O slide de Gates (p. 28) registra Gates 1–3 concluídos e o Gate 4 (modelo anual)
  em aberto.

> ➡️ **A Fase 2 já foi executada** e está em `Apresentacao_QuatroNorte_Fase2.pptx`
> (abaixo), que segue esta mesma estrutura.

> ✅ **O PowerPoint de origem está no repositório:** `Apresentacao_QuatroNorte_agosto.pptx`
> (34 slides, sendo **6 ocultos** — o PDF exportou os 28 visíveis). Ele é preservado
> intacto como registro da Fase 1.

⚠️ **Números superados:** o PDF reporta 223.590 OS · 9.859 carretas (base anterior à
reextração) e 47.666 linhas carreta × ano na p. 26. Os valores vigentes são
**217.217 OS · 9.585 carretas · 47.715 carreta-anos** — atualizados no deck da Fase 2.

---

## 🆕 FASE 2 — `Apresentacao_QuatroNorte_Fase2.pptx` (46 slides)

**Não é um deck novo: é o próprio `_agosto` continuado.** Gerado por
`notebooks/09_atualiza_apresentacao_fase2.py`, que parte do PowerPoint original (sem
modificá-lo), atualiza os números a partir de `reports/`, reexibe os slides de modelagem
que estavam ocultos e acrescenta o bloco da Fase 2.

**Estrutura: 46 slides.**

| Slides | Bloco |
|---|---|
| **1–34** | **Apresentação de agosto, contígua e na ordem original** (verificado a cada execução) |
| 35–39 | Abertura da Fase 2: linha do tempo, os quatro campos de contrato, EDA de contrato, desenho da modelagem |
| **40–42** | **Item 12** — 1ª tentativa (sem contrato), 2ª tentativa (contrato + divisão), resultados finais |
| **43** | **Item 13** — implicações gerenciais |
| **44** | **Item 14** — limitações |
| **45** | **Item 15** — projetos futuros |
| **46** | **Item 16** — conclusões |

Os slides novos entram **depois** do bloco de agosto, na sequência das perguntas da
disciplina — a apresentação entregue não é reordenada nem interrompida.

Descoberta que orientou a consolidação: os slides ocultos 27, 28 e 29 já eram
*Comparação dos modelos*, *Variáveis mais importantes* e *O que dizem os dados* — foram
escondidos porque a Fase 2 ainda não existia. Foram atualizados e reexibidos, não
recriados.

O que acrescenta à Fase 1:

| Slide | O que é | Origem |
|---|---|---|
| 5 | Hipóteses **com veredito**, incluindo H6a e H6b | tabela reconstruída |
| 6 | **Os quatro campos de contrato** — cobertura, perfil e destino | novo |
| 22–23 | Distribuições de contrato e **custo por regime contratual (H6b)** | novos |
| 30 | **Como isolamos o efeito de cada mudança** — as três configurações | novo |
| 31–32 | Comparação dos modelos e importâncias | **reexibidos** e atualizados |
| 33 | "O que dizem os dados" — resultados × literatura | **reexibido** e atualizado |
| 34 | Implicações gerenciais | novo |
| 39 | Conclusões | novo |
| 40 | Gates — 4 e 5 concluídos | atualizado |

Também atualizados em todo o deck: 19 trechos de texto (223.590→217.217 OS,
9.859→9.585 carretas, CAD 82.428→79.645 M, 47.666→47.715 carreta-anos, estatísticas de Y)
e 7 tabelas (hipóteses, descritivas, correlações, eta, VIF, seleção, métricas).
As afirmações que se inverteram — "fonte inicial", "sem dados de contrato", "sem filtro
MAINT" — foram reescritas.

**Resultado central:** contrato testado, efeito **fraco** (+0,0033 de R² no preditivo).
Modelo recomendado: **Gradient Boosting**, R² 0,455 · RMSE 2.002 · MAE 1.093 CAD/ano.

> Para regenerar: `py notebooks/09_atualiza_apresentacao_fase2.py`
> (o `_agosto` é apenas lido; a saída é sempre reconstruída do zero a partir dele)

---

## 🕓 Linhagem paralela — deck gerado por notebook

**`Apresentacao_QuatroNorte.pptx`** (23 slides)

- Grão: **carreta × ano**
- Alvo: **custo anual de manutenção** (CAD/ano, real dez/2025)
- Metodologia: fonte única `fato_wo_ml`, CPI Canadá, split temporal
- **Reprodutível:** gerado automaticamente por `notebooks/08_build_apresentacao.ipynb` a partir de tabelas e figuras em `reports/`
- Desempenho: RF preditivo R² 0,43; GB explicativo R² 0,57
- Gerado em: 2026-07-07

> 🔴 **Não é a apresentação entregue.** Este deck é uma linhagem **paralela e anterior**
> ao PDF: estrutura diferente, sem acentuação, sem os Gates, sem a moldura de Fase 1 /
> Fase 2. Não use como base da continuidade — mas **não descarte**: é o único artefato
> **reprodutível** e a forma mais rápida de materializar tabelas e figuras novas
> (métricas, importâncias, contrato) para depois levá-las à apresentação real.
>
> Seus números também estão defasados: base anterior à reextração e sem contrato.

> Para regenerar: execute `notebooks/08_build_apresentacao.ipynb`

---

## 🕓 Arquivos Históricos (Desatualizados)

### `Apresentacao_QuatroNorte_v2.pptx`

- **Estado:** ❌ Desatualizado (fase anterior: custo por km, grão mensal)
- Grão: carreta × mês
- Alvo: custo por km
- Desempenho histórico: RF R² 0,085
- **Motivo:** Criação manual; não foi atualizado para a metodologia anual
- **Uso:** Referência de evolução metodológica apenas

### `Apresentacao_QuatroNorte_v2.html`

- **Estado:** ❌ Desatualizado (fase anterior: custo por km, grão mensal)
- Relatório web (página única)
- **Motivo:** Edição manual; não foi atualizado para a metodologia anual
- **Uso:** Referência de evolução metodológica apenas

---

## 📋 Recomendação

- ✅ **`Apresentacao_QuatroNorte.pdf`** é a entrega apresentada e a **base da Fase 2** —
  a Fase 2 parte dela; o PowerPoint de origem é `Apresentacao_QuatroNorte_agosto.pptx`
- 🔁 **`Apresentacao_QuatroNorte.pptx`** (notebook 08): use como **gerador de tabelas e
  figuras** reprodutíveis, não como a apresentação
- 🕓 Ignore `versao antiga/v2.*` — referência histórica da fase mensal, descontinuada

Ver [`_NOTA_SOBRE_VERSOES.md`](_NOTA_SOBRE_VERSOES.md) para detalhes completos.
