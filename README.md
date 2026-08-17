# Custo Anual de Manutenção por Carreta

> 📖 **Novo no projeto? Comece por [`docs/GUIA_DO_PROJETO.md`](docs/GUIA_DO_PROJETO.md)**
> e pela revisão autoritativa [`docs/revisao_contrato_2026-08-16.md`](docs/revisao_contrato_2026-08-16.md)
> (a anterior, [`revisao_anual_2026-07-07.md`](docs/revisao_anual_2026-07-07.md), segue
> válida no que não foi superado). Este README é a especificação completa da abordagem
> vigente.
>
> 📖 **A história das perguntas** — como o projeto chegou ao custo anual por carreta, e
> o mapa dos 16 itens da entrega acadêmica: [`docs/narrativa_do_projeto.md`](docs/narrativa_do_projeto.md).
>
> ✅ **Status desta versão (2026-08-16).** Base **reextraída** com **dados de contrato**
> (25 → 29 colunas) e **pipeline reexecutado ponta a ponta** (`00`→`06`, mais os
> experimentos `10` e `11`). População da modelagem: **`tipo_manutencao = MAINT`** (D6).
>
> Dois resultados centrais, ambos negativos e ambos testados: as variáveis de contrato
> têm efeito **fraco** (+0,003 de R²), e treinar **modelos separados por refrigeração**
> parecia ganhar em 2025 mas **não se sustenta** em 2023 — mantém-se o **modelo único**.
> Ver [`docs/revisao_contrato_2026-08-16.md`](docs/revisao_contrato_2026-08-16.md) §11–§12.

Projeto aplicado do MBA para a **Quatro Norte Consulting**, sobre ciência de dados
aplicada a uma operação de leasing/rental de carretas no **Canadá**.

O objetivo é **analisar os fatores que influenciam o custo anual de manutenção por
carreta** — expresso em dólares canadenses (CAD) e corrigido pela inflação — e
**desenvolver modelos** estatísticos e de Machine Learning capazes de estimar esse
custo a partir das características operacionais, históricas e estruturais da frota.

O escopo **não é restrito à manutenção preventiva**: considera todo o custo interno
absorvido pela operação (`charge_flag = 'I'`), preventivo e corretivo.

> **População (D6, firmada em 2026-08-16).** A modelagem usa as carretas sob contrato
> com manutenção inclusa (`tipo_manutencao = 'MAINT'`) — **retomada do critério original
> do projeto**, que se perdeu na virada para o grão anual apenas porque a coluna não
> existia na fonte única. O filtro é aplicado como **flag** na base anual
> (`populacao_maint_flag`), não como exclusão de linhas: a base preserva todas as
> carreta-anos, e o cenário sem filtro permanece disponível como baseline de comparação.

> **Fonte única de dados.** O estudo usa **exclusivamente** a base consolidada
> `data/raw/fato_wo_ml_2020-01-01_to_2025-12-31.csv`. A extração SQL, o modelo estrela,
> os *joins* e o *feature engineering* que a produziram pertencem a uma **etapa anterior
> de preparação** e não são reexecutados aqui. Os dados de **contrato** passaram a
> integrar essa mesma base (29 colunas) — a fonte continua **única**, sem novos *joins*.

---

## 1. Contexto da pesquisa

Empresa de leasing/rental de carretas (secas e refrigeradas de até 53′) no Canadá,
com **manutenção própria** — oficinas registram ordens de serviço (OS) com mão de obra
e peças. Todos os custos são em **CAD**. O objetivo de negócio é apoiar **orçamento
anual** e **priorização de manutenção** da frota com base no histórico de operação.

## 2. Pergunta do problema

> Quais fatores mais influenciam o **custo anual de manutenção por carreta** — e como
> estimá-lo a partir das características operacionais, históricas e estruturais da frota?

## 3. Objetivo geral

Analisar os fatores que influenciam o custo anual de manutenção por carreta, expresso
em dólares canadenses (CAD) e corrigido pela inflação, identificando as variáveis com
maior capacidade explicativa e desenvolvendo modelos estatísticos e de Machine Learning
capazes de estimar esse custo anual.

## 4. Objetivos específicos

- Consolidar a análise a partir da base única de OS (etapa de preparação já realizada).
- Definir a variável resposta anual por carreta e corrigi-la pelo CPI do Canadá.
- Realizar análise exploratória (EDA) rigorosa: univariada, relação de cada variável
  com Y, ranking e multicolinearidade.
- Selecionar as variáveis do modelo de forma fundamentada.
- Desenvolver e avaliar modelos estatísticos e de ML com validação temporal.

## 5. Hipóteses

Adaptadas à unidade de análise anual e à fonte única:

- **H1 — Idade:** a idade da carreta eleva o custo anual de manutenção.
- **H2 — Uso:** maior quilometragem/uso está associada a maior custo anual.
- **H3 — Histórico:** o histórico de manutenção (OS e custo de anos anteriores) prevê o
  custo futuro.
- **H4 — Características do ativo:** montadora, subtipo, refrigeração e configuração
  influenciam o custo.
- **H5 — Região/operação:** a região de operação influencia o custo.
- **H6 — Contrato:** o contrato (duração/tipo) influencia o custo anual. Desdobrada em
  duas hipóteses operacionais:
  - **H6a — Duração:** o tempo de contrato decorrido até o reparo influencia o custo anual.
  - **H6b — Tipo:** o tipo de manutenção contratual (`MAINT`/`NET`/`MIX`) influencia o
    custo anual absorvido pela empresa.

**H6 já constava da apresentação de 2026-08-05** como hipótese declarada e **pendente de
dados**. Com a reextração da base única em 2026-08-16, os dados chegaram e H6 passa de
declarada a **testável** — daí o desdobramento em H6a/H6b, que corresponde exatamente ao
par "duração/tipo" do enunciado original. Continua **fora de escopo** apenas o que segue
ausente da fonte: `tipo_contrato` (RENTAL/LEASE), mão de obra detalhada, peças e leituras
dedicadas de odômetro.

## 6. Referencial teórico

### Katreddi, Thiruvengadam, Thompson, Schmid e Padmanaban (2023)
*Machine learning models for maintenance cost estimation in delivery trucks using
diesel and natural gas fuels.* Comparam Random Forest, XGBoost, ANN e um Super Learner
para prever custo de manutenção por milha; o Super Learner teve o melhor desempenho
(R² = 97,28%), mostrando que ensembles capturam bem relações não lineares entre
características operacionais e custos. Reforça a prioridade a modelos de árvore/ensemble
deste projeto; as métricas devem ser lidas no contexto da própria amostra.

### Katreddi, Thiruvengadam, Thompson e Schmid (2023)
*Mixed Effects Random Forest Model for Maintenance Cost Estimation in Heavy-Duty
Vehicles.* O Mixed Effects Random Forest captura diferenças sistemáticas entre grupos
de veículos, generalizando melhor em frotas heterogêneas. Justifica incluir variáveis
categóricas de agrupamento (montadora, subtipo, refrigeração) como *features*.

### Sun Zhonghui, Guo Yanying, Sun Zhonghong, Yang Shouchen e Hao Baoyu (2024)
*Maintenance cost prediction for the vehicle based on maintenance data.* Usa registros
históricos (Mixed Weibull + estimativa iterativa) para prever custos futuros. O valor
conceitual para este projeto: o histórico de manutenção é, por si só, insumo suficiente
para prever custos — o que sustenta o uso de features históricas defasadas.

### Adekitan, Adetokun e Okokpujie (2018)
*A data-based investigation of vehicle maintenance cost components using ANN.* Com uma
ANN e desempenho mais modesto (R = 0,766), mostra que há sinal preditivo em variáveis
de uso e histórico mesmo com dados limitados; referência histórica que reforça não
priorizar redes neurais frente a métodos de árvore.

## 7. Base de dados

### 7.1 Fonte única

Todo o estudo parte de **`data/raw/fato_wo_ml_2020-01-01_to_2025-12-31.csv`**:

| Métrica | Valor |
|---|---|
| Grão | 1 linha = 1 ordem de serviço (OS) |
| Linhas | **217.217 OS** |
| Carretas | **9.585** |
| Colunas | **29** |
| Custo | `TOTAL_CUSTO_INTERNO` nominal (CAD **74,48 mi**) |
| Janela | 2020-2025 |

> Valores da base **reextraída em 2026-08-16** (antes: 223.590 OS · 9.859 carretas ·
> CAD 77,18 mi). Após curadoria: 217.040 OS analíticas (−5 fora da janela, −172 estornos).

**Base de dados completa — as 29 variáveis** (resposta ao item 6 do Bloco 2):

| # | Coluna | Bloco | Papel |
|---|---|---|---|
| 1 | `id_os` | identificador | chave da OS (única) |
| 2 | `id_carreta` | identificador | chave do ativo |
| 3 | `descricao_carreta` | ativo | tipo/classe da unidade |
| 4 | `cod_montadora` | ativo | fabricante |
| 5 | `ano_modelo` | ativo | ano do modelo |
| 6 | `data_entrada_servico` | ativo | entrada em operação (origem de `idade_carreta`) |
| 7 | `eixos` | ativo | configuração estrutural |
| 8 | `comprimento` | ativo | porte físico |
| 9 | `flag_refrigerado` | ativo | reefer (Y/N) |
| 10 | `tailgate_flag` | ativo | **constante — removida** |
| 11 | `unit_subtype` | ativo | subtipo da unidade |
| 12 | `tire_size` | ativo | tamanho de pneu |
| 13 | `suspension_type` | ativo | tipo de suspensão |
| 14 | `new_used_indicator` | ativo | novo/usado |
| 15 | `numero_os` | identificador | número da OS |
| 16 | `data_os` | temporal | data do reparo (define o ano) |
| 17 | `tempo_contrato_meses_ate_reparo` | **contrato 🆕** | meses de contrato até o reparo |
| 18 | `cod_cliente` | **contrato 🆕** | cliente faturado no contrato vigente |
| 19 | `tipo_manutencao` | **contrato 🆕** | MAINT / NET / MIX |
| 20 | `franquia_km_mensal_contrato` | **contrato 🆕** | franquia de km — **99,8% zeros, removida** |
| 21 | `vmrs` | operacional | sistema reparado (código padronizado) |
| 22 | `km_acumulado_data_os` | exposição | odômetro na data da OS |
| 23 | `delta_km_desde_ultima_os` | exposição | Δ odômetro entre OS |
| 24 | `solicitacao_reparo` | texto | descrição livre do chamado (não modelada) |
| 25 | `cod_local_os` | geografia | local da OS (origem de `regiao_operacao`) |
| 26 | `endereco_os` | geografia | endereço (texto, não modelado) |
| 27 | `cod_provincia_estado` | geografia | código da província |
| 28 | `provincia_estado` | geografia | província (cobertura parcial ~54%) |
| 29 | `total_custo_interno` | **monetária** | custo interno da OS (base de Y) |

### 7.2 Etapa anterior (contexto, não reexecutada)

A construção da base — extração SQL (`data/extract_custo_interno_km.sql`), o **modelo
estrela** (dimensão de carretas + fatos de OS, mão de obra, peças, leituras, contratos
e GPS), os *joins* e o *feature engineering* (VMRS por regex, km na data da OS,
atributos do ativo) — produziu o CSV consolidado e é tratada apenas como **contexto**.
Schema completo em [`docs/dicionario_de_dados.md`](docs/dicionario_de_dados.md).

### 7.3 Custo interno

Custo interno = linhas de OS com `charge_flag = 'I'` (absorvido pela empresa), já
consolidado em `total_custo_interno` na fonte única. Estornos (custos negativos) são
excluídos na base analítica; a única série externa é o CPI do Canadá.

## 8. Variável-alvo (Y)

```text
custo_ano_real  —  custo anual de manutenção por carreta (CAD/ano)
```

- **Unidade:** CAD por ano · **Grão:** carreta × ano.
- **Natureza:** valores **reais**, corrigidos pela inflação canadense (**CPI
  all-items Canada**, Statistics Canada, vetor **v41690973**, base dez/2025).
- **Definição:** soma do custo interno de todas as OS da carreta no ano, deflacionada
  ao mês da OS e trazida a dezembro/2025.

A correção monetária elimina o efeito da inflação: diferenças entre anos passam a
refletir mudanças **reais** de custo, e não perda do poder de compra da moeda.

## 9. Variáveis explicativas candidatas

O universo derivável **da fonte única** é de **~25 variáveis**. Variáveis que
exigiriam outras tabelas (contrato, mão de obra, peças, leituras dedicadas de
odômetro) ficam **fora de escopo** nesta etapa. Nenhuma variável é eliminada antes da
EDA, salvo por erro técnico evidente ou ausência de informação.

### 9.1 Atributos do ativo (estáticos por carreta)

| Variável | Tipo | Origem/observação |
|---|---|---|
| `cod_montadora` | categórica | fabricante |
| `ano_modelo` | quantitativa | ano do modelo |
| `eixos` | quantitativa | configuração estrutural |
| `comprimento` | quantitativa | porte físico |
| `flag_refrigerado` | categórica | reefer (Y/N) |
| `unit_subtype` | categórica | subtipo da unidade |
| `tire_size` | categórica | tamanho de pneu |
| `suspension_type` | categórica | tipo de suspensão |
| `new_used_indicator` | categórica | novo/usado |
| `descricao_carreta` | categórica | tipo da unidade (proxy de modelo/classe) |
| `tailgate_flag` | — | **removida**: constante (variância nula) |

### 9.2 Derivadas e operacionais (grão carreta × ano)

| Variável | Tipo | Papel |
|---|---|---|
| `idade_carreta` | quantitativa | idade no ano (de `data_entrada_servico`) |
| `regiao_operacao` | categórica | local predominante da OS (`cod_local_os`) |
| `provincia_estado` | categórica | província predominante (parcial ~54%) |
| `km_acumulado_fim_ano` | quantitativa | odômetro no fim do ano (exposição) |
| `km_rodado_ano` | quantitativa | km rodado no ano (Δ odômetro; resets tratados) |
| `n_sistemas_vmrs_distintos_ano` | quantitativa | diversidade de sistemas no ano |
| `share_pm_ano` | quantitativa | fração de OS preventivas no ano |
| `vmrs_predominante_ano` | categórica | sistema VMRS predominante |
| `n_os_ano` | — | **componente de Y** (não é explicador) |
| `custo_medio_por_os_ano` | — | **componente de Y** (não é explicador) |

### 9.3 Histórico defasado (anti-vazamento)

Usam apenas informação de anos **anteriores** ao ano de referência:

| Variável | Papel |
|---|---|
| `custo_ano_anterior` | custo real do ano anterior |
| `n_os_ano_anterior` | nº de OS no ano anterior |
| `custo_acum_ate_ano_anterior` | custo real acumulado até o ano anterior |
| `n_os_acum_ate_ano_anterior` | OS acumuladas até o ano anterior |
| `anos_ativo_ate_ano_anterior` | anos de histórico disponível |

### 9.4 Contrato (reincluídas em 2026-08-16)

Derivadas dos quatro campos de contrato que passaram a integrar a fonte única. Como
contrato **muda ao longo do tempo** (51,5% das carretas têm mais de um
`tipo_manutencao` no período), exigem regra de agregação explícita no grão anual:

| Variável (carreta × ano) | Derivação | Cenário | Hipótese |
|---|---|---|---|
| `tipo_manutencao_ano` | categoria predominante no ano; ausente → `SEM_CONTRATO` | ambos | H6b |
| `share_maint_ano` | fração de OS do ano com `tipo_manutencao='MAINT'` | ambos | H6b |
| `tempo_contrato_meses_fim_ano` | maior `tempo_contrato_meses_ate_reparo` do ano | explicativo | H6a |
| `tempo_contrato_meses_inicio_ano` | valor de fim de t−1 (defasado, anti-vazamento) | preditivo | H6a |
| `trocou_contrato_ano` | indício de novo contrato no ano | ambos | H6 |
| `n_clientes_ano` | nº de `cod_cliente` distintos no ano | ambos | H6b |
| `cod_cliente_predominante_ano` | cliente com mais OS no ano — **uso descritivo** | — | — |

Duas restrições registradas: `franquia_km_mensal_contrato` é **removida** (99,8% dos
valores preenchidos são zero — variância quase nula, mesmo critério de `tailgate_flag`);
`cod_cliente` **não entra como categórica bruta** (597 categorias, 22,8% ausente — risco
de o modelo memorizar o cliente em vez de explicar o custo).

Especificação metodológica completa em
[`docs/dicionario_variaveis_candidatas.md`](docs/dicionario_variaveis_candidatas.md);
perfil de qualidade dos campos novos em
[`docs/revisao_contrato_2026-08-16.md`](docs/revisao_contrato_2026-08-16.md).

### 9.5 Variáveis criadas por feature engineering

Resposta ao item 7 do Bloco 2. Nenhuma das variáveis abaixo existe na base bruta: todas
resultam da agregação de OS para o grão **carreta × ano** (notebook `02`) e da deflação
(notebook `04`).

| Origem na base bruta | Variável derivada | Tipo de engenharia |
|---|---|---|
| `total_custo_interno` + `data_os` | `custo_ano_nominal` → **`custo_ano_real`** (Y) | agregação anual + deflação CPI |
| `data_entrada_servico` + `data_os` | `idade_carreta` | diferença temporal |
| `km_acumulado_data_os` | `km_acumulado_fim_ano`, `km_acumulado_inicio_ano`, `km_rodado_ano` | agregação + Δ com tratamento de resets |
| `vmrs` | `n_sistemas_vmrs_distintos_ano`, `share_pm_ano`, `vmrs_predominante_ano` | contagem, proporção e moda |
| `id_os` | `n_os_ano`, `custo_medio_por_os_ano` | contagem e razão (**componentes de Y**) |
| `cod_local_os` | `regiao_operacao` | mapeamento + moda no ano |
| histórico de anos anteriores | `custo_ano_anterior`, `n_os_ano_anterior`, `custo_acum_ate_ano_anterior`, `n_os_acum_ate_ano_anterior`, `anos_ativo_ate_ano_anterior` | defasagem (anti-vazamento) |
| `tipo_manutencao`, `cod_cliente`, `tempo_contrato_meses_ate_reparo` | `tipo_manutencao_ano`, `share_maint_ano`, `tempo_contrato_meses_fim_ano` / `_inicio_ano`, `trocou_contrato_ano`, `n_clientes_ano` | moda, proporção, máximo e defasagem (**🆕 2026-08-16**) |

## 10. Análise exploratória (EDA)

Protocolo (notebook `03b`): (1) estatísticas descritivas de todas as variáveis; (2)
histogramas e boxplots; (3) relação individual de cada X com Y (Pearson/Spearman para
quantitativas, ANOVA/eta para categóricas); (4) ranking de associação; (5)
multicolinearidade (matriz de Spearman + VIF).

**Distribuição do Y:** média CAD 1.673,72/ano, mediana 812,55, assimetria 3,79;
**apenas 3,2%** de carreta-anos com custo zero (o grão anual quase elimina a
zero-inflação do grão mensal). Custo real médio por carreta subiu **+52%** (2020→2025).

**Associação com Y (Spearman | eta) — explicativas mais fortes:**

| Variável | Medida | Valor |
|---|---|---|
| `n_os_ano_anterior` | Spearman | 0,540 |
| `custo_ano_anterior` | Spearman | 0,536 |
| `km_rodado_ano` | Spearman | 0,530 |
| `n_os_acum_ate_ano_anterior` | Spearman | 0,461 |
| `custo_acum_ate_ano_anterior` | Spearman | 0,452 |
| `km_acumulado_fim_ano` | Spearman | 0,428 |
| `idade_carreta` | Spearman | 0,018 (fraca) |
| `unit_subtype` | eta | 0,55 |
| `flag_refrigerado` | eta | 0,43 |
| `cod_montadora` | eta | 0,24 |

**Multicolinearidade:** VIF > 10 em `idade_carreta` (13,5), `n_os_acum` (12,9) e
`ano_modelo` (12,2) — colinearidades esperadas (idade↔ano-modelo; acumulados). Em
modelos lineares mantém-se uma variável por família; árvores/ensembles são robustos.

## 11. Técnicas previstas

- **Estatística:** correlação de Pearson e Spearman; ANOVA/eta; regressão linear
  múltipla; ridge; regressão polinomial.
- **Machine Learning:** árvore de decisão, Random Forest, Gradient Boosting, KNN.
- **Avaliação:** split **temporal** (treino 2020–2024, teste 2025); métricas R², RMSE
  e MAE; alvo transformado por `log1p` (assimetria).

## 12. Metodologia (passo a passo)

1. Validação da qualidade da base consolidada (notebooks 00–01).
2. Construção da base anual carreta × ano a partir da fonte única (02), **incluindo a
   agregação das variáveis de contrato** (§9.4).
3. Correção monetária pelo CPI do Canadá (04) → variável resposta `custo_ano_real`.
4. EDA: univariada, relação X↔Y, ranking, multicolinearidade (03b/03c/03d).
5. Seleção fundamentada das variáveis do modelo (05).
6. Modelagem estatística e de ML, em dois cenários (explicativo e preditivo), com
   split temporal (05).
7. Avaliação (R²/RMSE/MAE), importância das variáveis e discussão (05/06).

## 13. Resultados (base reextraída, pipeline de 2026-08-16)

Fonte canônica: `reports/tables/` + `docs/revisao_contrato_2026-08-16.md`.

**Base analítica:** 47.715 carreta-anos · 9.585 carretas · custo interno CAD 74,62 mi
nominal / **79,65 mi real** (dez/2025). Y: média **CAD 1.669/ano**, mediana 812,
assimetria 3,82, **3,1%** de carreta-anos com custo zero. População de modelagem
(`MAINT`): **41.739 carreta-anos (87,5%)**.

**Modelagem (teste temporal 2025):**

| Cenário | Modelo | R² | RMSE | MAE |
|---|---|---|---|---|
| Explicativo | Gradient Boosting | 0,585 | 1.746 | 908 |
| **Preditivo** | **Gradient Boosting** ◀ recomendado | **0,455** | **2.002** | **1.093** |

**Decomposição do ganho** — três configurações, para separar o efeito do filtro do
efeito das variáveis novas:

| Cenário | A: todos, sem contrato | B: MAINT, sem contrato | C: MAINT + contrato | Efeito do filtro | **Efeito do contrato** |
|---|---|---|---|---|---|
| Preditivo | 0,4323 | 0,4516 | **0,4549** | +0,0193 | **+0,0033** |
| Explicativo | 0,5700 | 0,5878 | 0,5854 | +0,0178 | **−0,0024** |

> ⚠️ O ganho do filtro `MAINT` **não é melhora de previsão**: as 5.976 carreta-anos
> excluídas têm custo médio de CAD 689 contra 1.689 das `MAINT`, muitas com custo zero.
> Amostra mais homogênea eleva o R² sem que o modelo preveja melhor.

- **Importância (permutação, preditivo):** `flag_refrigerado` 0,169 · `n_os_ano_anterior`
  0,097 · `custo_acum_ate_ano_anterior` 0,080 · `km_acumulado_inicio_ano` 0,079 ·
  `unit_subtype` 0,057 · `idade_carreta` 0,017 · `tempo_contrato_meses_inicio_ano`
  **0,006** (último colocado, dentro do desvio).
- Árvores/ensembles superam claramente os lineares (ridge e OLS ficam em R² ≈ 0,27).

**Hipóteses:** H2 (uso), H3 (histórico) e H4 (ativo) **suportadas**; H1 (idade isolada)
**não suportada** (ρ 0,032); H5 (região) **parcial**; **H6a** (duração de contrato,
ρ 0,140) e **H6b** (tipo contratual, η 0,183) **parciais/fracas** — testadas, não
assumidas.

**Experimento complementar (modelos por grupo de refrigeração).** Testado e descartado:
em 2025 o ganho era +0,0124 de R², mas em 2023 inverte de sinal. A validação com três
anos de teste (`notebooks/11_*`) é o que decide o modelo final.

**Escala do erro.** MAE de 1.093 CAD/ano equivale a **~51%** do custo médio do ano de
teste (CAD 2.151). O modelo serve para **priorizar** carretas e **provisionar no
agregado**; não sustenta orçamento por ativo isolado.

**Estabilidade entre anos.** O R² do modelo único vai de 0,4941 (teste 2023) a 0,4549
(teste 2025). O número de 2025 é o mais conservador dos três, não uma constante do modelo.

## 14. Estrutura do repositório

```text
.
├── README.md
├── data/
│   ├── raw/          # fonte única fato_wo_ml + série de CPI (público)
│   └── processed/    # bases anuais geradas pelos notebooks
├── docs/             # documentação, entregas, diagramas e histórico
├── notebooks/        # pipeline reprodutível (00 → 08); historico/ = versão mensal
└── reports/          # figuras e tabelas geradas
```

Os **notebooks são a fonte única e reprodutível**. Execute na ordem de
[`notebooks/README.md`](notebooks/README.md) (00 → 01 → 02 → 04 → 03b/03c/03d → 05 →
06 → 08). Para consultar resultados já gerados, use `07_painel_resultados.ipynb`.

## 15. Cuidados com dados

- Não versionar dados sensíveis; `data/raw/` é confidencial (exceção: série pública de
  CPI). Registrar filtros, transformações e exclusões.
- Evitar vazamento temporal: features históricas são defasadas (ano anterior) e o
  teste é o ano mais recente (2025).
- Atenção a resets/ruído de odômetro (deltas negativos ou > 250 mil km → ausente).
- "Interno" (`charge_flag='I'`) ≠ "preventivo": é o custo absorvido pela empresa, de
  qualquer natureza.

## 16. Referências

- Katreddi et al. (2023). *Machine learning models for maintenance cost estimation in
  delivery trucks using diesel and natural gas fuels.*
- Katreddi et al. (2023). *Mixed Effects Random Forest Model for Maintenance Cost
  Estimation in Heavy-Duty Vehicles Using Diesel and Alternative Fuels.*
- Sun Zhonghui et al. (2024). *Maintenance cost prediction for the vehicle based on
  maintenance data.*
- Adekitan, Adetokun e Okokpujie (2018). *A data-based investigation of vehicle
  maintenance cost components using ANN.*

## 17. Status

**2026-08-16 — pipeline reexecutado ponta a ponta** (`00` → `01` → `02` → `04` →
`03b/03c/03d` → `05` → `06`) sobre a fonte única reextraída, no grão carreta × ano:

- Base anual: **47.715 linhas carreta × ano** (9.585 carretas), custos deflacionados pelo
  **CPI Canadá** (StatCan v41690973, dez/2025).
- **Contrato incorporado**: 6 variáveis derivadas no grão anual + flag
  `populacao_maint_flag`. `franquia_km_mensal_contrato` removida (99,8% zeros);
  `cod_cliente` fora do modelo (597 categorias).
- Modelagem em **três configurações**, isolando o efeito do filtro `MAINT` do efeito do
  contrato. **Gradient Boosting** recomendado nos dois cenários.
- **Conclusão da rodada:** o contrato acrescenta pouco (+0,003 R²). Refrigeração,
  histórico defasado e uso seguem dominantes.

Pendente: atualização da apresentação em `docs/entregas/` (ver
[`docs/plano_fase2.md`](docs/plano_fase2.md)).
