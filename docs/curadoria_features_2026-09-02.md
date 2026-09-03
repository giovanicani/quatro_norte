# Curadoria de features — 2026-09-02

> **Documento autoritativo desta rodada** no que trata de seleção de variáveis, população
> de modelagem e definição dos alvos. Supersede
> [`revisao_contrato_2026-08-16.md`](revisao_contrato_2026-08-16.md) **apenas** no ponto da
> decisão **D6** (população). Todo o restante daquela revisão — fonte única, grão
> carreta × ano, deflação pelo CPI do Canadá, split temporal, anti-vazamento — continua
> valendo.

**Entregáveis desta rodada**

| Artefato | O que é |
|---|---|
| [`reports/tables/curadoria_features_2026-09-02.xlsx`](../reports/tables/curadoria_features_2026-09-02.xlsx) | Planilha didática: decisão por variável, evidência estatística, mapa das dummies e base codificada completa |
| [`notebooks/12_curadoria_features_2026-09-02.py`](../notebooks/12_curadoria_features_2026-09-02.py) | Script reprodutível que gera tudo acima |
| [`notebooks/13_cascata_y2_para_y1.py`](../notebooks/13_cascata_y2_para_y1.py) | Cascata Y2 → Y1 — **escrito, não executado** (ver §13) |
| `data/processed/base_anual_modelagem_2026-09-02.csv` | Base codificada (47.715 × 64), sem as dummies de `id_carreta` |
| `data/processed/base_anual_modelagem_id_dummy_2026-09-02.csv.gz` | Idem, **com** as 9.584 dummies de `id_carreta` |
| `reports/tables/12_*.csv` | Versões CSV das abas principais, para versionamento |
| `reports/tables/05_*.csv`, `06_*.csv` | Resultados da modelagem reexecutada (§10) |

---

## 1. Contexto

O Grupo revisou as *features* desenhadas na rodada de agosto e produziu uma curadoria
manual variável por variável. Este documento registra essas decisões, o resultado da
análise exploratória refeita sobre a base regenerada e as três decisões de escopo que a
curadoria implicava e precisaram ser confirmadas antes da execução.

**Base utilizada:** 47.715 carreta-anos · 9.585 carretas · 2020–2025 · 40 colunas,
regenerada nesta rodada a partir da extração de 29 colunas (16/ago), com os notebooks
`02` e `04` reexecutados.

> ⚠️ **Nota de infraestrutura.** O arquivo em `data/raw/` era a extração **antiga de 25
> colunas** — sem os campos de contrato. A reextração de 29 colunas estava fora do
> repositório (`~/Downloads`, 16/ago). Ela foi instalada em `data/raw/` e a antiga
> preservada em `data/raw/backup/fato_wo_ml_25col_extracao_2026-07-07.csv`. Como
> `data/raw/` e `data/processed/` são git-ignored, esse tipo de defasagem não aparece no
> `git status`: **confirmar as colunas da fonte antes de reexecutar o pipeline.**

---

## 1.1 A tabela da curadoria, como recebida

Reprodução **literal** da tabela enviada pelo Grupo em 02/09 — a grafia da coluna *Ação*
é preservada como veio, para rastreio. A coluna **"O que foi aplicado"** registra a
tradução para execução, e **"Status"** diz se a decisão está de fato em produção.

Legenda de status: ✅ aplicado · ⚠️ aplicado com ressalva · ⏳ pendente ·
❗ divergência (a execução não corresponde ao pedido) · ➖ não aplicável.

| Variável | Ação (Grupo) | Justificativa (Grupo) | O que foi aplicado | Status |
|---|---|---|---|---|
| `id_carreta` | Criar variável DUMY | Identificação da Carreta | 9.584 dummies materializadas em arquivo `.csv.gz` separado; **não entraram no modelo** | ⚠️ |
| `ano` | Usar | Ano que ocorreu as OS | Usado como **chave do split temporal** (treino ≤2024 / teste 2025), não como *feature* | ❗ |
| `custo_ano_nominal` | Retirar | Numero sem a inflação | Retirada | ✅ |
| `n_os_ano` | Regressão (Y2) | Prever a quantidade de OS para o ano de 2026 | Virou alvo Y2; modelo rodado (R² 0,608) | ✅ |
| `n_sistemas_vmrs_distintos_ano` | Premissa | Realizar a media a quantidade de VMRS utilizada pelas carretas nos ultimos 5 anos (questionar o claude se essa é a melhor opção) | Premissa **testada contra 3 alternativas e vencedora**; virou `vmrs_dist_media_5a` (ρ 0,474) | ✅ |
| `share_pm_ano` | Retirar | Não vamos testar no modelo, pois pega uma classe específica de manutenção e queremos verificar custo interno | Retirada | ✅ |
| `km_acumulado_fim_ano` | Previsão Série Temporal | Verificar a estimativa de KM em 2026 | Variável mantida e usada via odômetro de início de ano. **A projeção de série temporal para 2026 não foi construída** | ⏳ |
| `vmrs_predominante_ano` | Criar variável DUMY | Repetição do código mais frequente dentro da carreta. Se empate, repetição do código mais frequente de toda base | Dummy criada, mas o **desempate usa ordem alfabética**, não o código mais frequente da base. 11,0% das linhas mudariam (quase sempre para `PM`) | ❗ |
| `regiao_operacao` | Retirar | Retirar | Retirada (H5 encerrada) | ✅ |
| `provincia_estado` | Retirar | Retirar | Retirada (H5 encerrada) | ✅ |
| `tipo_manutencao_ano` | Veriável DUMY | Verificar se veículos que possuem tipos de contrato específicos possuem impacto no custo | Dummy criada e **no modelo** — exigiu revogar D6 (ver D7). Virou a 4ª variável mais importante | ✅ |
| `share_maint_ano` | Fica | Acompanhar resultado de tipo_manutencao_ano, que é MAINT | Mantida, restrita ao cenário explicativo (redundante com as dummies de tipo) | ✅ |
| `n_tipos_manutencao_ano` | Retirar | Redundante com tipo_manutencao_ano | Retirada | ✅ |
| `tempo_contrato_meses_fim_ano` | Manter | Avaliar se tempo de contrato impacta no custo real para 2026 | Mantida (só explicativo). **Avaliada: ρ 0,140 — H7 não suportada** | ✅ |
| `n_clientes_ano` | Manter | Avaliar se carretas que possuem mais clientes possuem impacto no custo real para 2026 | Mantida (só explicativo). Avaliada: ρ 0,230 | ✅ |
| `cod_cliente_predominante_ano` | Retirar | Retirar do modelo | Retirada (η 0,609 — a maior perda de sinal entre as removidas) | ✅ |
| `descricao_carreta` | Veriável DUMY | Verifica o detalhamento da carreta | Dummy criada (top-N + OUTROS) e no modelo; η 0,594 | ✅ |
| `cod_montadora` | Retirar | Retirar do modelo | Retirada. **Rever:** η 0,333 em Y2 (forte) — ver §11.3 | ✅ |
| `flag_refrigerado` | Veriável DUMY | Porque veículos refrigerados são mais caros para fazer manutenção | Dummy criada e no modelo. **Confirmada: a variável mais importante do modelo** (0,209) | ✅ |
| `tailgate_flag` | Veriável DUMY | Também precisa de manutenção e pode afetar o custo | **Impossível:** constante na base (variância nula). Não há dummy a criar | ➖ |
| `unit_subtype` | Veriável DUMY | Classificação específica do negócio | Dummy criada e no modelo; η 0,544 | ✅ |
| `tire_size` | Veriável DUMY | Tamanho do pneu impacta no custo | **Dummy especificada e não materializada**: η 0,158, abaixo do limiar FORTE (0,30) da autorização. Aguarda decisão | ⏳ |
| `suspension_type` | Retirar | A maioria das carretas ja possuem suspensão a ar | Retirada. **Rever:** η 0,249 em Y2 — ver §11.3 | ✅ |
| `new_used_indicator` | Retirar | Para contrato sempre são carretas novas e a maioria é por leasing | Retirada. **Rever:** η 0,193 em Y2 — ver §11.3 | ✅ |
| `ano_modelo` | Retirar | Redundante com idade_carreta | Retirada. **Rever:** ρ 0,268 em Y2 — ver §11.3 | ✅ |
| `eixos` | Manter | Quantidade de eixos podem impactar no custo pois mais pneus e outras questões | Mantida. Avaliada: ρ 0,051 — quase constante (95% com 2 eixos) | ✅ |
| `comprimento` | Retirar | Informacao ja presente na descricao_carreta | Retirada | ✅ |
| `data_entrada_servico` | Retirar | Foco em custo anual | Retirada. Confirmado como acerto: η 0,60 é **inflado** por 2.091 níveis (é uma data) | ✅ |
| `idade_carreta` | Mantém | Prever para 2026 baseado nos anos anteriores | Mantida. Avaliada: ρ 0,032 em Y1 (H1 não suportada), ρ 0,196 em Y2 e **negativa**. A projeção para 2026 não foi construída | ⏳ |
| `km_rodado_ano` | Mantém | Prever para 2026 baseado nos anos anteriores | Mantida (só explicativo; ρ 0,527). **A projeção para 2026 não foi construída** | ⏳ |
| `n_os_ano_anterior` | Mantém | Utilizar no modelo | No modelo; ρ 0,539 | ✅ |
| `n_os_acum_ate_ano_anterior` | Mantém | Utilizar no modelo | No modelo; ρ 0,465 | ✅ |
| `anos_ativo_ate_ano_anterior` | Mantém | Utilizar no modelo | No modelo; ρ 0,260 | ✅ |
| `tempo_contrato_meses_inicio_ano` | Mantém | Utilizar no modelo | No modelo; ρ 0,116. **Importância negativa (−0,003): atrapalha** | ✅ |
| `trocou_contrato_ano` | Mantém | Utilizar no modelo | Mantida (só explicativo); ρ 0,084 | ✅ |
| `populacao_maint_flag` | Retirar | Retirar | Retirada do modelo; permanece na base como coluna de auditoria (ver D7) | ✅ |
| `custo_ano_real` | Y1 | Variável principal que queremos prever para 2026 | Alvo Y1. **A previsão de 2026 não foi gerada** — tudo é validação no teste de 2025 | ⏳ |
| `custo_medio_por_os_ano` | Mantém | Utilizar no modelo | **Não aplicado como pedido:** é componente aritmético de Y1 e virou alvo Y3 (ver D8). Divergência levada ao Grupo e resolvida | ❗ |
| `custo_ano_anterior` | Mantém | Utilizar no modelo | No modelo; ρ 0,538 | ✅ |
| `custo_acum_ate_ano_anterior` | Mantém | Utilizar no modelo | No modelo; ρ 0,457 | ✅ |

**Contagem:** 40 variáveis · 30 ✅ · 1 ⚠️ · 5 ⏳ · 3 ❗ · 1 ➖.

### As três divergências, explicadas

1. **`ano` — "Usar".** Interpretado como chave temporal, não *feature*. Motivo: `ano`
   como *feature* não extrapola — 2026 é um nível que o modelo nunca viu, e a árvore o
   trataria como o valor mais próximo (2025), sem ganho. O efeito do tempo já entra por
   `idade_carreta` e pelo histórico defasado. **Se a intenção era outra, é revisável.**
2. **`vmrs_predominante_ano` — desempate.** A regra pedida não está implementada. É um
   defeito, não uma decisão: ver §14, item 2.
3. **`custo_medio_por_os_ano` — "Mantém".** Não podia ser cumprido como escrito
   (identidade aritmética com Y1). O Grupo aprovou a alternativa: virou alvo Y3.

---

## 1.2 Registro de alterações aplicadas em 02/09

O que mudou no repositório nesta data, em relação ao estado de 2026-08-16.

### Dados

| Item | Antes | Depois |
|---|---|---|
| Fonte em `data/raw/` | Extração de **25 colunas** (sem contrato) | Extração de **29 colunas** (16/ago); a antiga foi para `data/raw/backup/` |
| Base analítica | 31 colunas, de 07/jul | **40 colunas**, regenerada (notebooks `02` e `04`) |
| Bases de modelagem | — | `base_anual_modelagem_2026-09-02.csv` (47.715 × 64) e a versão com dummies de `id_carreta` (`.csv.gz`) |

### Desenho do estudo

| Item | Antes | Depois |
|---|---|---|
| População | Recorte `MAINT` — 41.739 carreta-anos (D6) | **Frota completa — 47.715** (D7) |
| Alvo | Y1 apenas | **Y1, Y2, Y3** (D8) |
| `tipo_manutencao_ano` | Fora do modelo (constante na população) | **No modelo**; 4ª variável mais importante |
| Configuração principal | `C_maint_com_contrato` | `B_todos_com_contrato` |
| Configuração C | MAINT + contrato (principal) | MAINT + contrato (**comparação**) |
| Configuração B | MAINT sem contrato | **Frota completa + contrato** |
| H5 (região) | Parcial, no modelo | **Fora do modelo**, não suportada |
| H6a / H6b | Nomenclatura da rodada anterior | **H6b** (tipo) e **H7** (tempo), alinhadas ao `AGENTS.md` |

### Variáveis do modelo

| Item | Antes | Depois |
|---|---|---|
| Retiradas | `tailgate_flag`, `franquia_*`, `cod_cliente_*`, `n_os_ano`, `custo_medio_por_os_ano`, `descricao_carreta` | **+8**: `regiao_operacao`, `provincia_estado`, `cod_montadora`, `suspension_type`, `new_used_indicator`, `ano_modelo`, `comprimento`, `share_pm_ano`, `populacao_maint_flag` |
| Reincorporada | — | `descricao_carreta` (era removida por cardinalidade) |
| Nova | — | `vmrs_dist_media_5a` (a premissa do Grupo) |
| Dummies materializadas | — | **42** (+ 9.584 de `id_carreta` em arquivo separado) |

### Código

| Arquivo | Alteração |
|---|---|
| `notebooks/02` | Reexecutado (contrato + `populacao_maint_flag`) |
| `notebooks/04` | Reexecutado (deflação sobre a base nova) |
| `notebooks/03b`, `03c`, `03d` | Reexecutados — já rodavam sobre a base completa |
| `notebooks/05` | **Reescrito**: população D7, lista curada de variáveis, `tipo_manutencao_ano` como *feature*, `vmrs_dist_media_5a`, novas configurações A/B/C e **bloco novo de D8** (Y2, Y3 e reconstituição Y1 = Y2 × Y3) |
| `notebooks/06` | Vereditos de H5/H6b/H7 atualizados; resumo numérico com os resultados de D8; recomendações de negócio reescritas |
| `notebooks/07` | Reexecutado |
| `notebooks/08` | Textos do deck corrigidos (afirmavam "população MAINT"); slide de modelagem com D8; limitações atualizadas |
| `notebooks/12_*` (novo) | Curadoria, evidência por alvo, dummies, planilha e comparativo Y1 × Y2 |
| `notebooks/13_*` (novo) | Cascata Y2 → Y1 — **escrito, não executado** |

### Documentação

`README.md` (§13 e §17), `AGENTS.md` (estado atual), `docs/GUIA_DO_PROJETO.md`
(D6 marcada como revogada), `notebooks/README.md` (scripts 12 e 13 + bug do VMRS) e
este documento.

### Correções de rota durante a execução

| O que | Correção |
|---|---|
| Regra de top-N colapsava `NET` e `MIX` em "OUTROS" | Corrigida — mataria a H6b que motivou revogar D6. Até 10 níveis, nenhum é colapsado |
| CSV com dummies de `id_carreta` com 926 MB | Comprimido para 4,4 MB (`.csv.gz`) |
| η inflado por cardinalidade em 3 variáveis | Coluna de alerta adicionada na aba 02 da planilha |

---

## 2. Decisões de escopo confirmadas em 2026-09-02

A curadoria continha três pontos que não eram apenas seleção de variável — mudavam o
desenho do estudo. Foram levados ao Grupo e confirmados.

### D7 — Revogação de D6: a população passa a ser a base completa

A curadoria manda **retirar `populacao_maint_flag`** e, ao mesmo tempo, **manter
`tipo_manutencao_ano` como dummy**. As duas coisas só convivem sem o filtro: dentro da
população `MAINT`, `tipo_manutencao_ano` é constante e não pode ser *feature*.

**Decisão do Grupo:** revogar **D6**. A modelagem passa a usar as **47.715** carreta-anos
(e não as 41.739 do recorte `MAINT`).

Consequências assumidas:

- **H6b volta ao modelo.** O regime contratual deixa de ser critério de amostra e volta a
  ser hipótese testável dentro do modelo — era exatamente o que D6 impedia.
- **Y muda de definição** (de novo). Passa a ser o custo interno anual de **toda** a
  frota, não só das carretas sob contrato com manutenção inclusa. Os números da rodada de
  agosto (§9 de `revisao_contrato_2026-08-16.md`) deixam de ser comparáveis.
- **A flag continua na base analítica** (`base_anual_carreta_deflacionada.csv`) como
  coluna de auditoria; ela apenas não entra como *feature*. Rodar o recorte `MAINT` como
  cenário de comparação continua custando uma linha de código.
- **Rastreio:** `populacao_maint_flag` tem |Spearman| = **0,307** com Y1 — associação
  FORTE. Isso não é argumento para mantê-la: a flag correlaciona com o custo porque
  carreta-ano sem OS entra como `SEM_OS` e tem custo zero. É definição de população, não
  fator explicativo.

### D8 — O alvo é decomposto em três

`custo_medio_por_os_ano` estava marcado como *feature*, mas
**Y1 = `n_os_ano` × `custo_medio_por_os_ano`** é identidade aritmética exata. Usá-lo como
*feature* de Y1 produziria R² artificial próximo de 1 — não é previsão, é a conta de
volta. E `n_os_ano` já havia sido promovido a alvo (Y2) na própria curadoria.

**Decisão do Grupo:** decompor a previsão.

| Alvo | Variável | O que se prevê |
|---|---|---|
| **Y1** | `custo_ano_real` | Custo anual de manutenção por carreta (CAD real dez/2025) |
| **Y2** | `n_os_ano` | Quantidade de OS no ano |
| **Y3** | `custo_medio_por_os_ano` | Custo médio por OS |

Para 2026: prever Y2 e Y3 separadamente e reconstituir **Y1 = Y2 × Y3**, comparando com
o modelo direto de Y1. Nenhum dos três entra como *feature* dos outros.

### D9 — `id_carreta` como one-hot, com ressalva registrada

A curadoria pede dummy de `id_carreta`. São **9.585** carretas → **9.584** colunas.

**Decisão do Grupo:** materializar, ciente da ressalva.

Ressalva registrada, conforme solicitado: o one-hot por carreta **memoriza o ativo em vez
de explicar o custo**. O R² sobe sem que o modelo tenha aprendido nada generalizável, e o
modelo fica inutilizável para carreta nova — que é justamente o caso de uso de orçamento.
O η bruto de `id_carreta` com Y1 é **0,757**, mas o valor é **inflado mecanicamente** pelos
9.585 grupos: não é comparável com o η das demais variáveis.

Por isso as dummies de `id_carreta` ficam em **arquivo separado**
(`base_anual_modelagem_id_dummy_2026-09-02.csv.gz`) e **não** na planilha — 9.584 × 47.715 ≈
457 milhões de células não abrem no Excel na prática. A planilha traz o **mapa completo**
das 9.584 dummies (aba 10) e a base codificada com todas as demais (aba 09).

---

## 3. Como a associação foi medida

| Tipo de variável | Métrica | Por quê |
|---|---|---|
| Quantitativa | **\|Spearman\|** (Pearson também reportado) | O custo anual é fortemente assimétrico (cauda longa à direita). Spearman mede associação monotônica sem exigir normalidade nem relação linear |
| Categórica | **η** (razão de correlação) + ANOVA | η = √(variância entre categorias / variância total): quanto do custo a categoria explica sozinha |

**Escala adotada:** FORTE ≥ 0,30 · moderada 0,15–0,30 · fraca < 0,15.

Duas advertências que a planilha repete:

- **O p-valor não decide nada aqui.** Com ~47,7 mil linhas, quase toda variável dá
  p < 0,05. O critério é a **força** da associação.
- **η infla com a cardinalidade.** Acima de 30 categorias, parte do η vem da contagem de
  graus de liberdade, não de efeito real. A aba 02 marca essas variáveis
  (`data_entrada_servico` η 0,60, `cod_cliente_predominante_ano` η 0,61,
  `descricao_carreta` η 0,59 com 253 níveis) com alerta explícito. Não compare esses
  valores com o de uma binária.

---

## 4. Resultado da análise exploratória (associação com Y1)

Excluídos os componentes aritméticos de Y1 (`n_os_ano`, `custo_medio_por_os_ano`) e o
`custo_ano_nominal` (que é o próprio Y1 antes da deflação, |Spearman| 0,999).

**Associação FORTE (≥ 0,30) — o núcleo explicativo**

| Variável | Força | Métrica | Decisão |
|---|---|---|---|
| `n_sistemas_vmrs_distintos_ano` | 0,702 | Spearman | Manter sob premissa (§5) |
| `descricao_carreta` | 0,594 | η (253 níveis — inflado) | Dummy (22 colunas) |
| `unit_subtype` | 0,544 | η (26 níveis) | Dummy (8 colunas) |
| `n_os_ano_anterior` | 0,539 | Spearman | Manter |
| `custo_ano_anterior` | 0,538 | Spearman | Manter |
| `km_rodado_ano` | 0,527 | Spearman | Manter |
| `n_os_acum_ate_ano_anterior` | 0,465 | Spearman | Manter |
| `custo_acum_ate_ano_anterior` | 0,457 | Spearman | Manter |
| `km_acumulado_fim_ano` | 0,435 | Spearman | Manter via projeção |
| `flag_refrigerado` | 0,425 | η (binária) | Dummy (1 coluna) |
| `vmrs_predominante_ano` | 0,336 | η (23 níveis) | Dummy (7 colunas) |

**Associação fraca entre as variáveis MANTIDAS — vigiar no modelo**

| Variável | Força | Leitura |
|---|---|---|
| `idade_carreta` | **0,032** | H1 segue **não suportada** — a idade quase não ordena o custo anual. Mantida por decisão do Grupo (previsão determinística para 2026), mas não espere contribuição |
| `eixos` | 0,051 | Quase constante: 95% das carretas com 2 eixos |
| `trocou_contrato_ano` | 0,084 | Rotatividade contratual praticamente não move o custo |
| `tempo_contrato_meses_inicio_ano` | 0,116 | **H7 fraca** na versão defasada (a admissível para prever) |
| `tempo_contrato_meses_fim_ano` | 0,140 | H7 fraca também na versão contemporânea |

**Leitura de negócio:** o custo anual é governado por **histórico e intensidade de uso**
(OS e custo dos anos anteriores, km rodado, diversidade de sistemas) e por **o que a
carreta é** (descrição/subtipo/refrigeração) — não pela idade nem pela maturidade do
contrato. O contrato entrou no escopo em agosto e, medido, **não sustenta H7**: essa é a
resposta honesta, não um motivo para insistir na variável.

---

## 5. A premissa de VMRS foi testada — e a proposta do Grupo venceu

A curadoria propôs substituir `n_sistemas_vmrs_distintos_ano` pela **média dos últimos
5 anos**, pedindo verificação. Quatro versões foram comparadas (aba 03), todas as
defasadas calculadas **apenas com anos anteriores**:

| Versão | Spearman com Y1 | Disponível em |
|---|---|---|
| Contemporânea (ano corrente) | **0,702** | 100% |
| **Média móvel de 5 anos, defasada** | **0,474** | 79,9% |
| Média histórica, defasada | 0,474 | 79,9% |
| Defasagem t−1 | 0,449 | 79,9% |

**Conclusão:** a premissa do Grupo é melhor que a defasagem simples que eu havia sugerido
— a média suaviza o ruído de um ano isolado. Ambas as colunas
(`vmrs_dist_media_5a` e `vmrs_dist_t_1`) foram gravadas na base de modelagem para o
teste final. Nota técnica: com janela de 6 anos, a média móvel de 5 anos e a média
histórica coincidem.

A versão contemporânea é bem mais forte (0,702), mas **não existe para prever 2026** —
usá-la seria vazamento. Os 20,1% de ausência são o primeiro ano de cada carreta, que não
tem passado.

---

## 6. Dummies criadas

Regra: até 10 níveis, **todos** preservados; acima disso, **top-N cobrindo 90% das
linhas + OUTROS**. Uma categoria é omitida como base (evita colinearidade perfeita).
Ausência vira nível **AUSENTE** — é informação, não ruído.

| Variável | Colunas | Base omitida | Força |
|---|---|---|---|
| `descricao_carreta` | 22 | `31' T/A MT LEAD REEFER VAN` | 0,594 |
| `unit_subtype` | 8 | `DC2` | 0,544 |
| `vmrs_predominante_ano` | 7 | `01` | 0,336 |
| `tipo_manutencao_ano` | 4 (`MIX`, `NET`, `SEM_CONTRATO`, `SEM_OS`) | `MAINT` | 0,183 |
| `flag_refrigerado` | 1 | `N` | 0,425 |
| `id_carreta` | 9.584 (arquivo separado) | menor id | 0,757 (inflado) |

**Duas dummies pedidas e não materializadas** (aba 07):

- **`tailgate_flag` — impossível.** Constante na base, variância nula: não há dummy a
  criar. Mesmo tratamento já dado em julho, agora reconfirmado na base nova.
- **`tire_size` — não autorizada pelo critério.** η = 0,158 (moderada), abaixo do
  limiar FORTE de 0,30 que definia a autorização automática. A especificação está pronta
  na planilha; basta a palavra do Grupo para materializar.

**Uma exceção deliberada:** `tipo_manutencao_ano` tem η = 0,183 (moderada), abaixo do
limiar — mas foi materializada, porque testá-la **é** a razão pela qual D6 foi revogada.
O status na aba 06 registra a exceção. Cautela na leitura: `NET` (2,2%) e `MIX` (1,4%)
são raros, então compare o **custo médio por nível com intervalo de confiança** (aba 05),
não apenas o η.

---

## 7. Variáveis removidas — o que se perde

Nenhuma remoção contraria a evidência, com uma exceção que precisa ficar registrada:

- **`cod_cliente_predominante_ano` (η 0,609 — FORTE).** É a maior associação entre as
  removidas, e a remoção está **certa**: 597 categorias com 22,8% de ausência; o modelo
  memorizaria o cliente. Coerente com D4. Se o Grupo quiser recuperar esse sinal sem o
  risco, o caminho é **top-N clientes + OUTROS** ou uma derivada de porte da frota do
  cliente — não a categórica bruta.
- **`data_entrada_servico` (η 0,601).** η inflado por cardinalidade (é uma data). A
  informação sobrevive em `idade_carreta`.
- **`regiao_operacao` (η 0,076) e `provincia_estado` (η 0,142).** A remoção **encerra a
  hipótese H5**, e há respaldo: a geografia praticamente não ordena o custo anual. H5
  passa de "parcial" a **não suportada / fora do modelo**.
- **`cod_montadora` (η 0,230), `suspension_type` (0,160), `share_pm_ano` (0,172),
  `n_tipos_manutencao_ano` (0,292).** Associação moderada; custo explicativo da remoção é
  baixo, e parte da informação de montadora sobrevive em `descricao_carreta`.
- **`new_used_indicator` (0,114), `comprimento` (0,097), `ano_modelo` (0,041).** Fracas
  ou redundantes. Remoção sem custo.

---

## 8. Situação das hipóteses após esta EDA

| | Hipótese | Situação |
|---|---|---|
| H1 | Idade ⇒ custo anual | ❌ **Não suportada** (Spearman 0,032). Variável mantida por decisão de previsão, não por evidência |
| H2 | Uso/quilometragem ⇒ custo | ✅ **Suportada** (`km_rodado_ano` 0,527; `km_acumulado_fim_ano` 0,435) |
| H3 | Histórico ⇒ custo futuro | ✅ **Suportada** — o bloco mais forte entre as variáveis sem vazamento |
| H4 | Características do ativo ⇒ custo | ✅ **Suportada** (`descricao_carreta` 0,594; `unit_subtype` 0,544; `flag_refrigerado` 0,425) |
| H5 | Região ⇒ custo | ❌ **Fora do modelo** por decisão do Grupo, com respaldo estatístico (η ≤ 0,142) |
| H6b | Tipo de contrato ⇒ custo | ➖ **Parcial, e mais relevante do que o η sugeria.** Associação moderada (η 0,183) mas **4ª variável mais importante** no modelo final (0,058) — ver §10.3. O valor do contrato está no tipo, não na duração |
| H7 | Tempo de contrato ⇒ custo | ❌ **Não suportada.** Além da associação fraca (0,116 / 0,140), a importância por permutação no modelo final é **negativa** (−0,003): a variável atrapalha. Veredito fechado — ver §10.3 |

---

## 9. Pendências da etapa de curadoria — resolvidas

1. ✅ **Pipeline reexecutado** (`02`, `04`, `03b/03c/03d`, `05`, `06`, `07`, `08`) sobre a
   população D7, com os três alvos de D8. Resultados em §10.
2. ✅ **Baseline do recorte `MAINT`** mantido como configuração C. Efeito medido: +0,0017.
3. ⏳ **`tire_size`** segue pendente — ver §11.3, agora com respaldo adicional de Y2.
4. ⏳ **VIF** de `tempo_contrato_*` × `idade_carreta` × `anos_ativo_ate_ano_anterior` e de
   `share_maint_ano` × dummies de `tipo_manutencao_ano` — ver §14, item 6.

A lista viva de pendências está em **§14**.


---

## 10. Resultados da reexecução (frota completa)

Reexecutados nesta rodada: `02`, `04`, `03b`, `03c`, `03d`, `05`, `06`, `07`, `08`.
Os notebooks `05`, `06` e `08` também tiveram os textos corrigidos — afirmavam
"população MAINT".

### 10.1 As três configurações

| Cenário | A: todos, sem contrato | B: todos + contrato | C: MAINT + contrato | **Contrato** (B−A) | Recorte MAINT (C−B) |
|---|---|---|---|---|---|
| Preditivo | 0,4059 | **0,4418** | 0,4435 | **+0,0359** | +0,0017 |
| Explicativo | 0,5644 | **0,5776** | 0,5673 | **+0,0132** | −0,0103 |

**D7 se justificou empiricamente.** Restringir a população a `MAINT` mexeu **+0,0017**
no R² preditivo — ruído. Em agosto esse número era +0,0193 e já havia sido lido como
artefato de amostra (§9 da revisão de 2026-08-16); agora, com o contrato dentro do
modelo, ele praticamente desaparece. A frota completa não custa poder preditivo **e**
permite testar H6b.

### 10.2 Os três alvos (D8), cenário preditivo

| Alvo | Melhor modelo | R² | RMSE |
|---|---|---|---|
| Y1 `custo_ano_real` — direto | Gradient Boosting | 0,4418 | 2.008,7 |
| **Y1 — decomposto (Y2 × Y3)** | **RF × RF** | **0,4713** | **1.954,9** |
| Y2 `n_os_ano` | Random Forest | **0,6080** | 2,77 |
| Y3 `custo_medio_por_os_ano` | Random Forest | **0,0851** | 319,9 |

**A decomposição venceu:** +0,0295 de R² e 54 CAD menos de erro que o modelo direto —
e sobre uma população mais difícil que a de agosto (a frota completa inclui as
carreta-anos de custo baixo ou zero que o recorte `MAINT` escondia). É o melhor número
preditivo do projeto: **0,4713 contra 0,4549** de agosto.

Ela funciona **apesar** de Y3 ser quase imprevisível (R² 0,085): Y2 é bem previsto e Y3
opera como multiplicador quase constante. É em Y3 que está a folga de melhoria.

### 10.3 Importância das variáveis (permutação, Y1 preditivo)

| Variável | Importância |
|---|---|
| `flag_refrigerado` | **0,209** |
| `custo_acum_ate_ano_anterior` | 0,100 |
| `n_os_ano_anterior` | 0,092 |
| **`tipo_manutencao_ano`** | **0,058** |
| `km_acumulado_inicio_ano` | 0,056 |
| `idade_carreta` | 0,039 |
| `descricao_carreta` | 0,039 |
| `anos_ativo_ate_ano_anterior` | −0,001 |
| `tempo_contrato_meses_inicio_ano` | **−0,003** |

Duas leituras de negócio:

- **Refrigeração sozinha vale mais que todo o resto somado.** É a história principal do
  custo, e se repete em todas as rodadas.
- **O valor do dado de contrato está no tipo, não na duração.** `tipo_manutencao_ano` é a
  4ª variável mais importante — e só existe como *feature* porque D6 foi revogada. Já
  `tempo_contrato_meses_inicio_ano` tem importância **negativa**: atrapalha. **H7 está
  respondida, e a resposta é não.**

### 10.4 O que a curadoria custou

Comparação limpa — mesma população, mesma configuração sem contrato, só a lista de
variáveis muda entre agosto e agora:

| Config A (frota completa, sem contrato) | Agosto | Agora | Δ |
|---|---|---|---|
| Preditivo R² | 0,4323 | 0,4059 | **−0,0264** |
| Explicativo R² | 0,5700 | 0,5644 | −0,0056 |

Retirar `cod_montadora`, `suspension_type`, `new_used_indicator`, `tire_size`,
`ano_modelo`, `comprimento`, `share_pm_ano` e a geografia removeu sinal real.
Individualmente cada uma era fraca ou moderada em Y1; somadas valiam ~0,026 de R².
Reincorporar `descricao_carreta` e `vmrs_dist_media_5a` não compensou.

**Isso não invalida a curadoria** — o saldo da rodada é positivo por causa da
decomposição. Mas o custo está medido e registrado, e §11 mostra onde recuperá-lo.

---

## 11. Fechamento da EDA: Y1 e Y2 lado a lado

Abas novas na planilha: **`11_Comparativo_Y1_Y2`**, **`12_Recomendado_Y1`**,
**`13_Recomendado_Y2`**. CSVs correspondentes em `reports/tables/12_*.csv`.

A aba 11 traz uma coluna que faltava: **disponibilidade**. Ela separa o que existe em
janeiro — e portanto serve para prever o ano — do que só descreve o ano já ocorrido:

| Status | Significado |
|---|---|
| `DISPONIVEL` | Atributo estático ou histórico defasado: entra no cenário preditivo |
| `CONTEMPORANEA` | Descreve o ano corrente: só vale no cenário explicativo |
| `ALVO` / `VAZAMENTO` / `POPULACAO` | Não é *feature* |

### 11.1 Candidatas sem vazamento e com associação ao menos moderada

**Para Y1 (13 variáveis)** — as oito primeiras já estão no modelo:
`data_entrada_servico` 0,601 · `descricao_carreta` 0,594 · `unit_subtype` 0,544 ·
`n_os_ano_anterior` 0,539 · `custo_ano_anterior` 0,538 ·
`n_os_acum_ate_ano_anterior` 0,465 · `custo_acum_ate_ano_anterior` 0,457 ·
`flag_refrigerado` 0,425 · `anos_ativo_ate_ano_anterior` 0,260 ·
`cod_montadora` 0,230 · `tipo_manutencao_ano` 0,183 · `suspension_type` 0,160 ·
`tire_size` 0,158.

**Para Y2 (16 variáveis)** — o topo é o mesmo, mas com força bem maior:
`descricao_carreta` 0,696 · `data_entrada_servico` 0,656 · `unit_subtype` 0,649 ·
`n_os_ano_anterior` 0,618 · `flag_refrigerado` 0,567 · `custo_ano_anterior` 0,493 ·
`n_os_acum_ate_ano_anterior` 0,440 · `custo_acum_ate_ano_anterior` 0,367 ·
**`cod_montadora` 0,333** · `ano_modelo` 0,268 · `suspension_type` 0,249 ·
`tipo_manutencao_ano` 0,248 · `tire_size` 0,210 · `idade_carreta` 0,196 ·
`new_used_indicator` 0,193 · `anos_ativo_ate_ano_anterior` 0,185.

### 11.2 Quatro conclusões da EDA fechada

1. **O núcleo é comum aos dois alvos.** Oito variáveis no topo de ambos: descrição,
   subtipo, refrigeração e os quatro blocos de histórico defasado. Esse conjunto está
   sólido e aplicado.
2. **Cinco variáveis retiradas valem mais em Y2 que em Y1** — ver §11.3. Como Y2 virou
   peça da previsão, retirá-las cobra preço justamente onde elas importam.
3. **`data_entrada_servico` é uma armadilha.** Aparece no topo dos dois (η 0,60 e 0,66),
   mas são **2.091 categorias** — é uma data. Boa parte do η é cardinalidade, não efeito.
   A informação real está em `idade_carreta` e `anos_ativo`. **Manter retirada.**
4. **`idade_carreta` só tem função em Y2** (0,032 em Y1 · 0,196 em Y2) e com **sinal
   negativo**: carreta mais velha faz *menos* OS por ano. Provável seleção de
   sobrevivência ou uso menos intenso — merece um parágrafo na discussão, porque
   contraria a intuição de H1.

### 11.3 Cinco decisões pendentes para o Grupo

| Variável | Y1 | Y2 | Recomendação |
|---|---|---|---|
| `cod_montadora` | 0,230 | **0,333 FORTE** | **Reincorporar nos dois alvos** |
| `tire_size` | 0,158 | 0,210 | **Materializar a dummy** |
| `suspension_type` | 0,160 | 0,249 | Reincorporar só em Y2 |
| `ano_modelo` | 0,041 | 0,268 | Reincorporar só em Y2 |
| `new_used_indicator` | 0,114 | 0,193 | Reincorporar só em Y2 |
| `data_entrada_servico` | 0,601 | 0,656 | **Manter retirada** (η inflado) |

Nada impede conjuntos de variáveis **diferentes por alvo** — é a saída natural aqui.

> 📊 **Evidência parcial já disponível.** A Etapa 1 do script `13` chegou a rodar antes
> de o treino ser interrompido, e mediu o efeito das cinco por **validação cruzada no
> treino** (`GroupKFold` por `id_carreta`, sem tocar o teste) — resultado em
> [`reports/tables/13_selecao_modelo_y2.csv`](../reports/tables/13_selecao_modelo_y2.csv):
>
> | Conjunto de features de Y2 | Melhor modelo | CV R² (treino) | nº features |
> |---|---|---|---|
> | **curado + 5 reincorporadas** | Random Forest | **0,6895** | 19 |
> | curado (D7) | Random Forest | 0,6815 | 14 |
>
> **As cinco valem +0,0080 de CV R² em Y2.** Ganho pequeno mas consistente: aparece nas
> quatro famílias de modelo testadas (RF, GB, ridge, linear), sempre a favor do conjunto
> ampliado. Reforça a recomendação de reincorporá-las **no modelo de Y2**.

### 11.4 Variáveis fortes que ficam de fora por vazamento

Fortes, mas descrevem o ano que já aconteceu — não existem em janeiro de 2026:
`n_sistemas_vmrs_distintos_ano` (0,702 em Y1 / **0,845** em Y2) · `km_rodado_ano`
(0,527 / 0,620) · `km_acumulado_fim_ano` (0,435 / 0,371) · `share_pm_ano`
(0,172 / 0,349, negativa) · `vmrs_predominante_ano` · `n_clientes_ano` ·
`tempo_contrato_meses_fim_ano`.

Elas sustentam o **cenário explicativo** (R² 0,578) e só entram no preditivo via
projeção — que é a pendência da série temporal de km.

---

## 12. Regressão em Y2: o que a EDA indica sobre a forma do modelo

`n_os_ano` é **contagem**, e a distribuição define a forma:

| | |
|---|---|
| Média | 4,55 OS/ano · mediana 3 · máx 59 |
| Variância | 18,22 |
| **Variância / média** | **4,0** → superdispersão |
| Zeros | 1.486 (3,1%) |
| Assimetria | 2,41 |

- **Poisson está descartado**: assume variância = média; produziria erros-padrão
  subestimados e significância inflada.
- **Binomial Negativa (log link) é a forma correta**, com coeficientes interpretáveis
  como razão de taxa ("carreta refrigerada faz X% mais OS/ano") — bom para a entrega.
- **Não há inflação de zeros** (3,1%): não precisa de ZIP/ZINB.
- A alternativa pragmática já rodando (`log1p` + linear) chega a R² 0,577.

**A regressão linear é defensável em Y2, ao contrário de Y1.** Fica a 0,031 do Random
Forest (0,577 vs 0,608) — em Y1 a distância é muito maior. Cuidado com a **polinomial
grau 2**, que colapsou em Y3 (R² −185): extrapolação descontrolada, não usar.

---

## 13. Usar Y2 e Y3 para prever Y1

Pergunta do Grupo: *"o que queremos é utilizar talvez o Y2 e Y3 para prever o Y1. Isso é
possível?"* — **Sim, e já é o resultado vigente do projeto.** Mas a resposta tem duas
metades opostas, e a distinção entre elas é a decisão metodológica mais importante desta
rodada.

### 13.1 Com os valores REAIS de Y2 e Y3: não é previsão, é a conta de volta

A identidade `Y1 = Y2 × Y3` é **exata** na base. Verificado sobre as 47.715 carreta-anos:

| Verificação | Resultado |
|---|---|
| Diferença absoluta máxima entre `custo_ano_real` e `n_os_ano × custo_medio_por_os_ano` | **0,00000000 CAD** |
| Linhas com diferença > 0,01 CAD | **0** |
| R² usando os valores **reais** de Y2 e Y3 (teste 2025) | **1,000000** |

R² = 1,0 exato. Isso **não é um modelo bom** — é a multiplicação de volta. E é inútil
para 2026: em janeiro não se sabe quantas OS a carreta terá nem quanto cada uma custará.
São exatamente as duas coisas que precisam ser previstas.

Foi por isso que `custo_medio_por_os_ano` **não pôde permanecer como *feature*** conforme
a curadoria pedia — a divergência ❗ registrada em §1.1 e resolvida por D8.

### 13.2 Com as PREVISÕES de Y2 e Y3: funciona, e é o melhor resultado do projeto

O acento sobre o Ŷ é toda a diferença. `Ŷ2` e `Ŷ3` são previstos a partir de informação
disponível **no início do ano** (atributos da carreta + histórico até t−1); nenhum dado do
ano corrente entra.

| Caminho | R² | RMSE | MAE |
|---|---|---|---|
| Y1 direto | 0,4418 | 2.008,7 | 1.074,3 |
| **Y1 = Ŷ2 × Ŷ3** | **0,4713** | **1.954,9** | **1.059,0** |

**+0,0295 de R²** e 54 CAD menos de erro — sobre uma população mais difícil que a de
agosto. É o caminho recomendado no `README.md`.

### 13.3 Três formas de fazer, duas já medidas

| # | Forma | Situação |
|---|---|---|
| 1 | **Multiplicativa** — impõe `Y1 = Ŷ2 × Ŷ3` | ✅ Rodada: **R² 0,4713** |
| 2 | **Cascata** — `Ŷ2` como *feature* de um modelo de Y1 | ⏳ Escrita, não executada |
| 3 | **Cascata dupla** — `Ŷ2` **e** `Ŷ3` como *features* | ⏳ Escrita, não executada |

**Multiplicativa.** Respeita a identidade real do negócio e é fácil de defender na banca:
"prevemos quantas OS a carreta terá e quanto cada uma custa". O risco é a composição de
erros — se `Ŷ2` erra 10% e `Ŷ3` erra 10% no mesmo sentido, o produto erra ~21%.

**Cascata.** Mais flexível: o modelo de Y1 decide o peso de `Ŷ2` e pode corrigir o viés
do produto. Proposta do Grupo, implementada em
[`notebooks/13_cascata_y2_para_y1.py`](../notebooks/13_cascata_y2_para_y1.py) —
**ainda não executada**, porque o Grupo optou por fechar a EDA antes de treinar.

### 13.4 O cuidado que a cascata exige e a multiplicativa não

Se o modelo de Y1 for treinado com `Ŷ2` calculado **nas mesmas linhas** em que Y2 foi
treinado, esse `Ŷ2` é artificialmente preciso no treino. O modelo de Y1 aprende a confiar
nele em excesso e o desempenho cai no teste — um vazamento sutil, que não aparece como
erro e passa por bom resultado.

**Mitigação implementada:** o `Ŷ2` das linhas de treino é *out-of-fold*
(`GroupKFold` agrupado por `id_carreta`, 5 folds); as linhas de teste recebem a previsão
do modelo ajustado em todo o treino. O agrupamento por carreta impede que anos diferentes
da **mesma** carreta caiam em folds distintos.

### 13.5 Onde está a folga: Y3

| Alvo | Melhor R² |
|---|---|
| Y2 `n_os_ano` | **0,608** |
| Y3 `custo_medio_por_os_ano` | **0,085** |

**Y3 é o gargalo dos três caminhos.** A decomposição já vence *apesar* dele: Y2 é bem
previsto e Y3 opera como multiplicador quase constante. Elevar Y3 de 0,085 para ~0,20
melhoraria as três formas de uma só vez — é o investimento de maior retorno agora, à
frente de qualquer ajuste fino de hiperparâmetro.

### 13.6 O que o script `13` compara

Quatro caminhos no mesmo teste temporal de 2025:

| Caminho | Forma |
|---|---|
| A | `Y1 ~ features` (direto) |
| B | `Y1 = Ŷ2 × Ŷ3` (multiplicativo) |
| **C** | `Y1 ~ features + Ŷ2` ← proposta do Grupo |
| D | `Y1 ~ features + Ŷ2 + Ŷ3` |

A etapa 1 do script também testa reincorporar em Y2 as cinco variáveis de §11.3, com
seleção por **validação cruzada no treino** — nunca no teste (ver a evidência parcial
já disponível em §11.3).

---

## 14. Pendências — retomar por aqui

Em ordem de custo/benefício:

1. **Decidir as cinco variáveis de §11.3.** Bloqueia o treino da cascata, porque muda o
   conjunto de *features* de Y2.
2. **Corrigir o desempate de `vmrs_predominante_ano`.** A regra pedida pelo Grupo — em
   caso de empate, usar o código mais frequente de toda a base — **não foi
   implementada**: o notebook `02` resolve por ordem alfabética (`mode().iloc[0]`).
   Impacto medido: **28,4%** dos pares carreta-ano têm empate e **11,0% (5.067 linhas)
   mudariam de categoria**, quase sempre para `PM`. Hoje a variável **subestima
   manutenção preventiva** como sistema predominante, e a dummy foi criada sobre a
   versão errada. Correção barata, no notebook `02`.
3. **Executar a cascata** (`notebooks/13_*`) e comparar os quatro caminhos.
4. **Construir a previsão de 2026** — nada foi previsto ainda; tudo é validação em 2025.
   Falta: projetar `km_rodado_ano` e `km_acumulado_fim_ano` (a "previsão de série
   temporal" pedida na curadoria), somar +1 em `idade_carreta`, montar a linha de cada
   carreta com o histórico de 2025 e aplicar o caminho vencedor.
5. **Melhorar Y3** (R² 0,085) — é o elo fraco da decomposição e onde há mais folga.
6. **Binomial Negativa em Y2** com tabela de coeficientes como razão de taxa, mais VIF do
   bloco de histórico defasado (bem colinear entre si).
7. **Atualizar a apresentação** em `docs/entregas/`.

**Não são pendências:** `tailgate_flag` (constante, impossível) e as dummies de
`id_carreta` (geradas em `.csv.gz`; entrar no modelo é decisão separada, com a ressalva
de memorização de §2).

---

**Autoria:** Grupo 01 — Marlon Wenzel, Jeison Lima, Rodrigo Queiroz, Giovani Cani.
**Data:** 2026-09-02 · **Natureza:** curadoria de variáveis, EDA de associação e três
decisões de escopo (D7, D8, D9).