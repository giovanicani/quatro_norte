# Custo Anual de Manutenção por Carreta

> 📖 **Novo no projeto? Comece por [`docs/GUIA_DO_PROJETO.md`](docs/GUIA_DO_PROJETO.md)**
> e pela revisão autoritativa [`docs/revisao_anual_2026-07-07.md`](docs/revisao_anual_2026-07-07.md).
> Este README é a especificação completa da abordagem vigente.

Projeto aplicado do MBA para a **Quatro Norte Consulting**, sobre ciência de dados
aplicada a uma operação de leasing/rental de carretas no **Canadá**.

O objetivo é **analisar os fatores que influenciam o custo anual de manutenção por
carreta** — expresso em dólares canadenses (CAD) e corrigido pela inflação — e
**desenvolver modelos** estatísticos e de Machine Learning capazes de estimar esse
custo a partir das características operacionais, históricas e estruturais da frota.

O escopo **não é restrito à manutenção preventiva**: considera todo o custo interno
absorvido pela operação (`charge_flag = 'I'`), preventivo e corretivo.

> **Fonte única de dados.** A partir desta revisão, o estudo usa **exclusivamente** a
> base consolidada `data/raw/fato_wo_ml_2020-01-01_to_2025-12-31.csv`. A extração SQL,
> o modelo estrela, os *joins* e o *feature engineering* que a produziram pertencem a
> uma **etapa anterior de preparação** e não são reexecutados aqui.

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

Hipóteses de **contrato** (duração/tipo) ficam **fora de escopo** nesta etapa, por
ausência dessas variáveis na fonte única.

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
| Linhas | 223.590 OS |
| Carretas | 9.859 |
| Colunas | 25 |
| Custo | `TOTAL_CUSTO_INTERNO` nominal (CAD) |
| Janela | 2020-2025 |

Colunas: identificadores (`id_os`, `id_carreta`, `numero_os`), atributos do ativo
(`cod_montadora`, `ano_modelo`, `data_entrada_servico`, `eixos`, `comprimento`,
`flag_refrigerado`, `tailgate_flag`, `unit_subtype`, `tire_size`, `suspension_type`,
`new_used_indicator`, `descricao_carreta`), dados da OS (`data_os`, `vmrs`,
`km_acumulado_data_os`, `delta_km_desde_ultima_os`, `solicitacao_reparo`), geografia
(`cod_local_os`, `endereco_os`, `cod_provincia_estado`, `provincia_estado`) e
`total_custo_interno`.

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

Especificação metodológica completa em
[`docs/dicionario_variaveis_candidatas.md`](docs/dicionario_variaveis_candidatas.md).

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
2. Construção da base anual carreta × ano a partir da fonte única (02).
3. Correção monetária pelo CPI do Canadá (04) → variável resposta `custo_ano_real`.
4. EDA: univariada, relação X↔Y, ranking, multicolinearidade (03b/03c/03d).
5. Seleção fundamentada das variáveis do modelo (05).
6. Modelagem estatística e de ML, em dois cenários (explicativo e preditivo), com
   split temporal (05).
7. Avaliação (R²/RMSE/MAE), importância das variáveis e discussão (05/06).

## 13. Resultados (números vigentes)

Fonte canônica: `reports/tables/` + `reports/sumario_executivo.md` +
`docs/revisao_anual_2026-07-07.md`.

**Modelagem (teste temporal 2025):**

| Cenário | Modelo | R² | RMSE | MAE |
|---|---|---|---|---|
| Explicativo | Gradient Boosting | 0,572 | 1.753 | 895 |
| **Preditivo** | **Random Forest** ◀ recomendado | **0,429** | **2.026** | **1.064** |

- Árvores/ensembles superam claramente os modelos lineares (caudas extremas).
- **Importância (permutação, preditivo):** `flag_refrigerado` 0,22 (dominante) ·
  `n_os_ano_anterior` 0,12 · `km_acumulado_inicio_ano` 0,072 · `custo_ano_anterior`
  0,066 · histórico acumulado ~0,06 · `idade_carreta` 0,032.

**Hipóteses:** H2 (uso), H3 (histórico) e H4 (ativo) suportadas; H1 (idade isolada)
não suportada; H5 (região) parcial; contrato fora de escopo.

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

Pipeline completo executado a partir da **fonte única** `fato_wo_ml`, no grão **carreta
× ano**:

- Base anual construída: **49.248 linhas carreta × ano** (9.859 carretas), custos em
  CAD deflacionados pelo **CPI Canadá** (StatCan v41690973, base dez/2025).
- Custo interno total: **CAD 77,18 mi nominal / 82,43 mi real**.
- EDA variável-a-variável completa (histogramas, boxplots, correlações, eta, ranking,
  VIF) em `reports/figures/eda/` e `reports/tables/03b_*`.
- Modelagem: **Random Forest** recomendado no cenário preditivo (R² = 0,43; teste 2025);
  **Gradient Boosting** atinge R² = 0,57 no cenário explicativo. `flag_refrigerado`,
  histórico defasado e uso são os fatores dominantes.
- Apresentação acadêmica (23 slides): `docs/entregas/Apresentacao_QuatroNorte.pptx`
  (regenerável via `notebooks/08_build_apresentacao.ipynb`).
