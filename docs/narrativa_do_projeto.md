# A história das perguntas — narrativa e linha do tempo do projeto

> **Para que serve este documento.** O projeto não respondeu uma pergunta: ele
> **refez a pergunta quatro vezes**, e cada reformulação foi consequência direta de uma
> evidência encontrada nos dados. Essa trajetória é o argumento metodológico mais forte
> da entrega — e é exatamente o que a rubrica cobra no **item 12**, ao pedir resultados
> *preliminares (1ª tentativa)*, *preliminares (2ª tentativa)* e *finais*.
>
> Este documento é a fonte da narrativa para a apresentação. Ele não substitui os
> números — que vivem em `reports/` — mas diz **em que ordem contá-los e por quê**.
>
> 🚫 **Não há mais nada em carreta × mês.** O grão mensal e o alvo "custo por km" foram
> **descontinuados** e não voltam. Aparecem aqui como **antecedente** — a evidência que
> justificou a escolha do grão anual —, nunca como alternativa em avaliação. Toda
> análise vigente é **carreta × ano**, e a apresentação defende exatamente isso.

---

> ⚠️ **Nomenclatura — atenção para não confundir.** A apresentação de 2026-08-05 usa
> "Fase 1" e "Fase 2" no sentido de **entrega**: Fase 1 = o que foi apresentado (itens
> 1–11, até a seleção de variáveis); Fase 2 = modelagem, avaliação e resultados, marcada
> com `*Fase 2` no fluxograma da p. 6. Este documento usa "Fase 0–3" no sentido de
> **evolução da pergunta**. Correspondência: as Fases 0–2 daqui compõem a **Fase 1 do
> deck**; a Fase 3 daqui **é a Fase 2 do deck**. Ao falar com a banca, use a nomenclatura
> do deck.

## 1. A linha do tempo em uma tabela

As duas primeiras colunas são **antecedentes encerrados** (grão mensal, descontinuado);
as duas últimas são a **linha vigente** do projeto, ambas em carreta × ano.

| | ⬛ Fase 0 — preventiva *(encerrada)* | ⬛ Fase 1 — custo por km *(encerrada)* | ✅ Fase 2 — custo anual | ✅ Fase 3 — contrato *(atual)* |
|---|---|---|---|---|
| **Quando** | preliminar | 2026-07-06 | 2026-07-07 | **2026-08-16** |
| **Pergunta** | Quanto custa a **manutenção preventiva por km**? | Quanto custa a **manutenção interna por km**? | Quanto custa manter **uma carreta por ano**? | **O contrato** explica o custo anual? |
| **Y** | custo preventivo/km | custo interno/km | `custo_ano_real` (CAD/ano) | `custo_ano_real` (mantido) |
| **Grão** | carreta × mês | carreta × mês | **carreta × ano** | carreta × ano |
| **Fonte** | 7 tabelas (modelo estrela) | 7 tabelas | **fonte única** (25 col.) | fonte única (**29 col.**) |
| **Deflator** | IPCA (Brasil) ❌ | **CPI Canadá** | CPI Canadá | CPI Canadá |
| **População** | MAINT + km ≥ 500 | MAINT + km ≥ 500 | todo custo interno | **MAINT** (retomado, via flag) |
| **Zeros em Y** | 79,8% | 67,1% | **3,2%** | **3,1%** |
| **Linhas** | ~749 mil | 749.664 | 49.248 | **47.715** (41.739 MAINT) |
| **R² (teste)** | 0,063 | 0,085 | 0,429 pred. · 0,572 expl. | **0,455** pred. · **0,585** expl. |
| **Contrato** | filtro implícito | filtro implícito | ⛔ fora de escopo | ✅ **testado: efeito fraco (+0,003 R²)** |

---

## 2. A história, fase a fase

> As Fases 0 e 1 estão **encerradas**. São contadas porque **provam que o grão anual não
> foi uma preferência, e sim uma conclusão** — mas nenhum número delas é resultado
> vigente do projeto.

### ⬛ Fase 0 *(encerrada)* — "Quanto custa a manutenção preventiva por km?"

A pergunta inicial era sobre **manutenção preventiva**, medida **por quilômetro**, com
custos deflacionados pelo **IPCA**.

Três problemas apareceram, nesta ordem:

1. **Vazamento temporal.** As primeiras métricas — R² 0,242 e AUC 0,938 — pareciam
   ótimas. Eram artefato: variáveis acumuladas (`custo_acum_manutencao`,
   `km_acumulado`) carregavam informação do próprio período previsto. Corrigido o
   vazamento, o R² caiu para **0,063**. *Lição: um resultado bom demais é uma hipótese
   sobre o próprio código, não sobre o negócio.*
2. **Deflator errado.** A operação é canadense e os custos estão em **CAD**; o IPCA é a
   inflação **brasileira**. A inflação canadense no período foi ≈ 20%, muito abaixo da
   brasileira — todos os valores "reais" estavam contaminados.
3. **Alvo quase sempre zero.** **79,8%** dos meses tinham custo preventivo zero. Um
   alvo assim não é regressão: é quase uma variável binária disfarçada.

> **Por que a pergunta mudou:** o recorte "preventiva" não correspondia ao objetivo de
> negócio — a empresa absorve **todo** o custo interno, preventivo *e* corretivo.

### ⬛ Fase 1 *(encerrada)* — "Quanto custa a manutenção interna por km?" (2026-07-06)

O alvo passou a ser o **custo interno total** (`charge_flag = 'I'`), preventivo mais
corretivo, e o deflator passou a ser o **CPI do Canadá** (StatCan, vetor v41690973).
Duas correções certas — e o resultado ainda foi fraco: **R² = 0,085** (RMSE 0,243,
MAE 0,131) no teste temporal.

O diagnóstico apontou o **grão**, não o modelo:

- **67,1%** dos pares carreta × mês continuavam com custo zero. A zero-inflação caiu,
  mas seguia dominante.
- A razão **custo/km** é instável: meses de baixa quilometragem produzem denominadores
  pequenos e razões explosivas. A variável media duas coisas ao mesmo tempo.
- Nenhuma variável categórica separava bem o alvo (máximo η = 0,084).

> **Por que a pergunta mudou:** trocar de modelo não resolveria. O problema era a
> unidade de análise — e, além disso, "custo por km" **não é a pergunta que o negócio
> faz**. Orçamento de frota se faz por **ativo e por ano**.
>
> 🚫 **Aqui o grão mensal se encerra.** Os notebooks correspondentes ficaram em
> `notebooks/historico/` como registro de auditoria; nada dessa fase alimenta a análise
> vigente.

### ✅ Fase 2 — "Quanto custa manter uma carreta por ano?" (2026-07-07)

Três decisões simultâneas:

1. **Grão carreta × ano**, com Y = soma do custo interno da carreta no ano, em CAD reais
   (dez/2025).
2. **Fonte única** (*Single Source of Truth*): toda a análise passa a partir de um único
   CSV consolidado. Os *joins* e o *feature engineering* viram etapa anterior.
3. **Sem filtro MAINT** — não por escolha metodológica, mas por **imposição dos dados**:
   o filtro dependia de `fato_contratos`, ausente da fonte única.

O efeito foi grande:

- Zero-inflação: 67,1% → **3,2%**. O grão anual praticamente elimina o problema que
  travava as duas fases anteriores.
- R² preditivo: 0,085 → **0,429**; explicativo, **0,572**. Um salto de ~5×.
- Fatores dominantes: **refrigeração** (importância 0,22), **histórico de manutenção**
  e **uso acumulado**. Idade isolada, ao contrário do esperado, quase não pesa (ρ ≈ 0,02).

Mas a mudança teve um **custo declarado**: a adesão à fonte única derrubou ~metade das
46 variáveis do desenho original. As hipóteses de **contrato** foram marcadas como
**fora de escopo**, e a limitação foi registrada como pendência.

> **Por que a pergunta mudou de novo:** a limitação deixou de existir.

### ✅ Fase 3 — "O contrato explica o custo anual?" (2026-08-16, **respondida**)

A empresa disponibilizou os dados de contrato **dentro da própria base consolidada** —
a fonte segue única, agora com **29 colunas**: `tempo_contrato_meses_ate_reparo`,
`cod_cliente`, `tipo_manutencao` e `franquia_km_mensal_contrato`.

Isso fecha um ciclo com a Fase 1 de um jeito que vale contar em voz alta na
apresentação: **o filtro `MAINT`, que na fase mensal era um recorte assumido sem
verificação, agora pode ser uma hipótese testada.** O que era pressuposto vira
evidência.

**H6 — "Contrato (duração/tipo) influencia o custo" — já estava na apresentação de
2026-08-05**, declarada e aguardando dados. Ela agora se torna testável, desdobrada em
**H6a** (duração) e **H6b** (tipo de manutenção contratual). A base foi **reextraída** no
processo: 217.217 OS e 9.585 carretas, contra 223.590 e 9.859 antes.

O que já se sabe **antes de modelar**, só do perfil dos campos:

- `tipo_manutencao` é viável, mas **desbalanceado**: MAINT 89,7%, MIX 1,6%, NET 1,1%.
- `tempo_contrato_meses_ate_reparo` é o campo mais promissor: 92,5% de cobertura,
  mediana de 35 meses, sem valores negativos.
- `cod_cliente` tem 597 categorias — **não pode entrar bruto**, sob pena de o modelo
  memorizar clientes em vez de explicar custos.
- `franquia_km_mensal_contrato` é **degenerada**: 99,8% dos valores preenchidos são
  zero. **Removida.**
- Contrato **muda ao longo do tempo**: 51,5% das carretas têm mais de um
  `tipo_manutencao` no período. Não é atributo estático do ativo.

> **A resposta:** o contrato **não acrescenta** poder preditivo relevante. Ganho de
> **+0,0033 de R²** no cenário preditivo e **−0,0024** no explicativo;
> `tempo_contrato_meses_inicio_ano` ficou em último lugar na importância por permutação
> (0,0064, dentro do desvio). H6a e H6b resultaram **parciais/fracas**.
>
> O que o dado novo entregou de fato foi **definir a população de análise** (MAINT) —
> contribuição real, mas diferente da esperada. E o desfecho fecha o arco da narrativa:
> a hipótese que estava na apresentação desde a Fase 1 como declaração agora tem
> veredito, obtido por teste e não por suposição.

---

## 3. O fio condutor — o que essa história demonstra

Quatro reformulações, um padrão único: **a cada rodada, o obstáculo encontrado nos
dados redefiniu a pergunta.**

| Obstáculo encontrado | Reformulação que ele provocou |
|---|---|
| Métrica boa demais (R² 0,242 / AUC 0,938) | Auditoria de vazamento → R² honesto de 0,063 |
| Custos em CAD deflacionados por índice brasileiro | Troca para CPI Canadá |
| 79,8% de alvo zero | Alvo preventivo → custo interno total |
| 67,1% de zeros + razão custo/km instável | Grão mensal → **grão anual** |
| Metade das variáveis inexistente na fonte | Escopo reduzido e **declarado**, não disfarçado |
| Dados de contrato chegam à base | Limitação vira **hipótese testável** (H6a/H6b) |

É essa progressão — e não o R² final — que caracteriza o trabalho como pesquisa
aplicada. Vale afirmar isso explicitamente na apresentação: **nenhuma dessas viradas foi
troca de preferência; cada uma foi forçada por uma evidência.** O grão anual, em
particular, não é uma escolha de conveniência: é a resposta a um alvo que era zero em
67% das observações no grão mensal.

---

## 4. Onde cada item da rubrica é respondido

| # | Item da rubrica | Onde está | Estado |
|---|---|---|---|
| 1 | Contexto | `README.md` §1 · deck s.2 | ✅ |
| 2 | Pergunta do problema | `README.md` §2 · deck s.3 | ✅ |
| 3 | Objetivo geral e específicos | `README.md` §3–4 · deck s.4 | ✅ |
| 4 | Hipóteses | `README.md` §5 · deck s.5 | ⚠️ **atualizar: H6a/H6b** |
| 5 | 4+ artigos científicos | `README.md` §6 · deck s.6 | ✅ (4 artigos) |
| 6 | Base de dados completa | `README.md` §7.1 (**tabela das 29 colunas**) · deck s.7/s.10 | ⚠️ atualizado no README; **falta no deck** |
| 7 | Variáveis de *feature engineering* | `README.md` §9.5 · `dicionario_variaveis_candidatas.md` | ⚠️ atualizado no README; **falta no deck** |
| 8 | EDA realizada | `README.md` §10 · deck s.11–17 · `reports/figures/eda/` | ⚠️ refazer com contrato |
| 9 | Técnicas estatísticas / ML | `README.md` §11 · deck s.18 | ✅ (7 modelos × 2 cenários) |
| 10 | Referencial teórico | `README.md` §6 · deck s.6 | ✅ |
| 11 | Metodologia passo a passo | `README.md` §12 · deck s.7 (fluxograma) | ✅ |
| **12a** | **Resultados preliminares — 1ª tentativa** | Fase 2: custo anual **sem contrato**, base de 223.590 OS — deck atual (s.19–20) · `revisao_anual_2026-07-07.md` | ✅ **já apresentado** |
| **12b** | **Resultados preliminares — 2ª tentativa** | Fase 3 parcial: custo anual **com contrato**, base reextraída — rodada de EDA/modelagem a executar | 🔴 pendente |
| **12c** | **Resultados finais** | Fase 3 consolidada, com baseline sem contrato para isolar o ganho | 🔴 pendente |
| 13 | Implicações gerenciais | `reports/tables/06_recomendacoes_negocio.csv` · deck s.21 | ⚠️ ampliar com contrato |
| 14 | Limitações | `README.md` §15 · deck s.22 | ⚠️ atualizar (franquia, desbalanceamento) |
| 15 | Recomendações futuras | deck s.23 | ⚠️ atualizar (contrato saiu da lista) |
| 16 | Conclusões | deck s.23 · `reports/sumario_executivo.md` | ⚠️ refazer ao final |

**Sobre o item 12.** As três rodadas de resultados correm **inteiramente dentro do grão
anual**: 1ª tentativa = anual sem contrato (o que o deck já apresenta); 2ª = anual com
contrato sobre a base reextraída; final = a versão consolidada, com baseline. As Fases 0
e 1 **não são "tentativas" no sentido da rubrica** — são o antecedente que justificou a
escolha do grão, e permanecem em `docs/historico/` e `notebooks/historico/` apenas como
registro de auditoria.

---

## 5. O que isso implica para a apresentação

> ✅ **Executado.** A apresentação da Fase 2 (`Apresentacao_QuatroNorte_Fase2.pptx`)
> preserva os **34 slides de agosto contíguos e na ordem original** e acrescenta **12
> slides depois deles**, na sequência das perguntas da disciplina (itens 12 a 16). O
> plano abaixo, de revisar slides no lugar, foi substituído por essa estrutura — a
> apresentação entregue não é reordenada nem interrompida.

| Ação | Slide | Conteúdo |
|---|---|---|
| ✏️ Revisar | s.5 (Hipóteses) | incluir **H6 e H7**; substituir a linha "contrato — fora de escopo" |
| ✏️ Revisar | s.7/s.10 (Base) | **29 colunas · 217.217 OS · 9.585 carretas** (item 6 da rubrica) |
| ✏️ Revisar | s.11–17 (EDA) | incluir contrato na descritiva, no ranking e no VIF |
| ✏️ Revisar | s.19–20 (Modelos) | resultados finais + **baseline sem contrato**, lado a lado, para isolar o ganho — é aqui que a 1ª e a 2ª tentativa aparecem como comparação, não como slides separados |
| ✏️ Revisar | s.22–23 (Limitações/Futuro) | contrato **sai** de "trabalhos futuros" e entra em "resultados"; entram as novas limitações (franquia degenerada, desbalanceamento de MAINT) |
| ➕ Opcional | após s.4 (Objetivos) | **"A evolução da pergunta"** — a tabela da §1, se o Grupo quiser tornar a trajetória explícita em vez de deixá-la para a fala |

Se a evolução for contada **oralmente** em vez de virar slide, o ponto de entrada
natural é o s.3 (Problema): explicar por que a pergunta é *anual por carreta* — porque
as formulações anteriores esbarraram em 80% e 67% de alvo zero. Uma frase, e o júri
entende que o grão anual é conclusão, não conveniência.

**Ponto de atenção na narrativa oral:** a base foi reextraída **e** ganhou contrato na
mesma rodada. Se o R² final subir, parte do ganho pode vir da mudança de população, não
das variáveis novas. Por isso o notebook `05` precisa rodar um **baseline sem contrato
sobre a base nova** — é o que permite dizer, com honestidade, quanto o contrato de fato
acrescentou. Sem esse número, a conclusão da Fase 3 não se sustenta.

**Decisão pendente que afeta a história:** manter todo o custo interno com
`tipo_manutencao` como variável (premissa atual) ou voltar a filtrar `MAINT`. A primeira
opção é a que fecha a narrativa — o filtro assumido na Fase 1 vira hipótese testada na
Fase 3. Ver [`revisao_contrato_2026-08-16.md`](revisao_contrato_2026-08-16.md) §4, D6.

---

**Documentos-fonte desta narrativa:** `docs/historico/revisao_feedback.md` ·
`docs/historico/registro_alteracoes_2026-07-06.md` ·
`docs/historico/revisao_pos_base_nova_2026-07-07.md` ·
`docs/revisao_anual_2026-07-07.md` · `docs/revisao_contrato_2026-08-16.md`

**Data:** 2026-08-16 · Grupo 01 — Marlon Wenzel, Jeison Lima, Rodrigo Queiroz, Giovani Cani
