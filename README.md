# Previsão de Custos de Manutenção de Carretas

> 📖 **Novo no projeto? Comece pelo [`docs/GUIA_DO_PROJETO.md`](docs/GUIA_DO_PROJETO.md)** —
> ele resume tudo, diz o que ler em que ordem e marca o que é vigente vs.
> desatualizado. Este README é a especificação completa.

Projeto aplicado do MBA para a **Quatro Norte Consulting**, com foco em
ciência de dados aplicada a uma operação de leasing de carretas.

O objetivo é analisar dados históricos de manutenção, contratos,
quilometragem, garantias, peças e telemetria para identificar os fatores que
mais influenciam o custo de manutenção internalizada e desenvolver modelos
capazes de estimar o custo futuro por quilômetro.

O escopo **não é restrito à manutenção preventiva**. Considera todas as
ordens de serviço com custo interno (`charge_flag = 'I'`), incluindo
manutenções preventivas e corretivas absorvidas pela operação.

---

## 1. Contexto da pesquisa

O projeto é desenvolvido para uma empresa de leasing/rental de
carretas, com o objetivo de dar suporte a decisões de manutenção e orçamento
com base em dados históricos de operação da frota própria (`cus_id_owner = 4`).

## 2. Pergunta do problema

> Quais são os fatores que mais influenciam o custo de manutenção interno
> das carretas — e como prever esse custo por km futuro com base nos dados
> históricos?

## 3. Objetivo geral

Analisar os dados históricos de manutenção das carretas para identificar os
principais fatores que influenciam os custos e desenvolver um modelo
preditivo capaz de estimar custos futuros.

## 4. Objetivos específicos

- Coletar, consolidar e organizar dados históricos de manutenção das
  carretas.
- Realizar análise exploratória dos dados para identificar padrões,
  tendências e variáveis relevantes.
- Investigar a relação entre características dos contratos de leasing e
  custos de manutenção.
- Identificar os principais fatores associados aos custos de manutenção.
- Desenvolver e avaliar modelos preditivos para estimar os custos futuros.

## 5. Hipóteses

- Contratos de leasing com maior duração tendem a apresentar custos de
  manutenção mais elevados.
- Carretas com maior tempo de utilização tendem a demandar maiores gastos
  com manutenção.
- O aumento da quilometragem percorrida está associado ao aumento dos
  custos.
- O histórico de manutenções anteriores é relevante para prever custos
  futuros.
- Variáveis operacionais e características dos contratos influenciam
  significativamente os custos de manutenção.

## 6. Referencial teórico

### Katreddi, Thiruvengadam, Thompson, Schmid e Padmanaban (2023)
*Machine learning models for maintenance cost estimation in delivery trucks
using diesel and natural gas fuels.*

- **Contexto/problema abordado:** investiga a previsão dos custos de
  manutenção por milha de caminhões de entrega movidos a diesel e gás
  natural. Os autores destacam que os custos de manutenção representam
  parcela significativa do custo total de propriedade (TCO) e que ainda
  existem poucas pesquisas utilizando dados reais de manutenção de veículos
  pesados.
- **Técnica utilizada:** comparação entre Random Forest, XGBoost, Redes
  Neurais Artificiais (ANN) e um modelo ensemble do tipo Super Learner.
  Variáveis: quilometragem, tipo de combustível, região de operação e
  características de utilização do veículo.
- **Principal achado:** o Super Learner teve o melhor desempenho (R² =
  97,28%, MAE = US$ 0,0068/milha), mostrando que modelos ensemble capturam
  bem relações não lineares entre características operacionais e custos.
  Esse desempenho elevado foi obtido em uma base específica de caminhões de
  entrega e deve ser interpretado considerando as características da
  amostra e da validação adotada pelos autores.
- **Relação com este projeto:** uma das referências mais aderentes — usa
  variáveis operacionais semelhantes às deste projeto (quilometragem,
  região, tipo/categoria do ativo, equivalentes aqui a
  `km_acumulado_data_os`, `provincia_estado` e `cod_montadora`/`cod_modelo`)
  para prever custo por unidade de distância. O resultado reforça a
  escolha, já prevista na seção 11, de priorizar modelos de árvore/ensemble
  (Random Forest, Gradient Boosting) sobre regressão linear simples, dado
  que a relação entre variáveis operacionais e custo tende a ser não
  linear. A ressalva sobre a base específica dos autores também serve de
  alerta: nossas métricas (R², RMSE, MAE) devem ser lidas no contexto da
  nossa própria amostra, sem comparação direta com o R²=97,28% relatado.

### Katreddi, Thiruvengadam, Thompson e Schmid (2023)
*Mixed Effects Random Forest Model for Maintenance Cost Estimation in
Heavy-Duty Vehicles Using Diesel and Alternative Fuels.*

- **Contexto/problema abordado:** amplia a análise para diferentes
  categorias de veículos pesados e combustíveis alternativos (diesel, gás
  natural, propano, elétrico), considerando que tipo de veículo,
  combustível, região e condições operacionais influenciam diretamente os
  custos de manutenção.
- **Técnica utilizada:** modelo Mixed Effects Random Forest, combinando
  Random Forest com modelos de efeitos mistos, capturando tanto padrões
  globais quanto particularidades entre grupos de veículos.
- **Principal achado:** melhor capacidade de generalização que o Random
  Forest convencional, especialmente em bases heterogêneas com diferentes
  tipos de veículos e combustíveis — mais robusto a variações estruturais
  em frotas diversificadas.
- **Relação com este projeto:** a ideia central — capturar diferenças
  sistemáticas entre grupos de ativos além do efeito médio geral — é
  diretamente aplicável às nossas variáveis qualitativas de agrupamento
  (`cod_montadora`, `cod_modelo`, `classe`, `tipo_contrato`,
  `sistema_vmrs`). O modelo Mixed Effects em si está fora do escopo técnico
  previsto na seção 11, mas justifica incluir essas variáveis categóricas
  como features (via one-hot/encoding) em vez de ignorá-las, já que grupos
  distintos de carretas podem ter padrões de custo diferentes mesmo com
  quilometragem semelhante.

### Sun Zhonghui, Guo Yanying, Sun Zhonghong, Yang Shouchen e Hao Baoyu (2024)
*Maintenance cost prediction for the vehicle based on maintenance data.*

- **Contexto/problema abordado:** propõe um método para prever custos
  futuros de manutenção utilizando registros históricos de manutenção e
  falhas, com foco em apoiar programas de garantia estendida e reduzir
  incertezas sobre custos futuros.
- **Técnica utilizada:** Engenharia de Confiabilidade — modelo Mixed
  Weibull combinado com um modelo iterativo de estimativa de custos. Não
  usa algoritmos tradicionais de machine learning.
- **Principal achado:** o histórico de manutenção e falhas permite estimar
  de forma consistente os custos futuros, evidenciando a importância da
  modelagem baseada em confiabilidade para esse tipo de problema.
- **Relação com este projeto:** a abordagem via confiabilidade (Weibull)
  não se aplica diretamente aqui, pois não dispomos de dados estruturados
  de falha por componente com garantia de fábrica — nossa base
  (`fato_wo`/`fato_wo_ml`) registra ordens de serviço e custos, não taxas
  de falha por lote. O valor do artigo para este projeto é conceitual:
  reforça que o histórico de manutenção (nosso `fato_wo_ml` acumulado por
  carreta) é, por si só, insumo suficiente para prever custos futuros,
  mesmo sem informação de falha estruturada — o que dá suporte à decisão
  de manter o escopo em técnicas estatísticas/ML (seção 11) em vez de
  modelagem de confiabilidade.

### Adekitan, Adetokun e Okokpujie (2018)
*A data-based investigation of vehicle maintenance cost components using
ANN.*

- **Contexto/problema abordado:** investiga os fatores que influenciam os
  custos de manutenção de veículos corporativos, considerando utilização e
  histórico operacional.
- **Técnica utilizada:** Rede Neural Artificial (ANN), com variáveis como
  quilometragem, consumo de combustível, frequência de falhas e histórico
  de utilização.
- **Principal achado:** a rede neural identificou padrões entre
  características operacionais e custos, com coeficiente de correlação
  R = 0,766 entre valores previstos e observados.
- **Relação com este projeto:** mostra, com uma técnica mais simples
  (ANN) e desempenho mais modesto (R = 0,766) que os artigos 1 e 2, que
  mesmo com dados limitados é possível extrair sinal preditivo de
  variáveis operacionais (quilometragem, falhas, uso). Como os artigos com
  ensembles/Random Forest reportaram desempenho superior, este trabalho
  serve principalmente como referência histórica e justificativa para não
  priorizar redes neurais na seção 11, favorecendo os métodos de árvore já
  definidos ali.

## 7. Base de dados

### 7.1 Visão geral

A extração principal está em `data/extract_custo_interno_km.sql` e gera
**8 arquivos CSV** em `data/raw/`, cobrindo a janela **2020-01-01 a
2025-12-31**, restritos à frota própria (`cus_id_owner = 4`, `active_flag =
'Y'`, com ao menos uma leitura de KM válida no período).

| Arquivo | Grão (1 linha =) | Papel |
| --- | --- | --- |
| `dim_carretas` | uma carreta | Dimensão — atributos do ativo |
| `fato_readings` | uma leitura de odômetro | Quilometragem (KM acumulado) |
| `fato_wo` | uma ordem de serviço | Cabeçalho da OS + totais internos |
| `fato_wo_ml` | uma ordem de serviço | Base enriquecida para modelagem (atributos da carreta, VMRS extraído por regex, KM na data da OS, `total_custo_interno`) |
| `fato_wo_labour` | uma linha de mão de obra | Custo interno de mão de obra |
| `fato_wo_parts` | uma linha de peça | Custo interno de peças |
| `fato_contratos` | uma carreta-contrato | Contrato de leasing/rental vigente |
| `fato_gps` | uma posição GPS por dia | Lat/long da carreta |

Todas as tabelas se conectam por `id_carreta`; `fato_wo_labour` e
`fato_wo_parts` também se conectam a `fato_wo`/`fato_wo_ml` por `id_os`.
Contratos se ligam por `id_carreta` **e** período (`data_inicio`–`data_fim`
contendo a data do evento).

### 7.2 Definição do custo interno (alvo)

Custo interno = linhas de OS com `charge_flag = 'I'` (absorvido pela
empresa, não faturado ao cliente), considerando apenas OS aprovadas,
concluídas e não canceladas.

- **Mão de obra:** `sublet_flag='Y' → total_sublet`, senão `cost_hours *
  hourly_cost`
- **Peças:** `sublet_flag='Y' → total_sublet`, senão `nvl(item_average_cost,
  item_cost) * actual_qty`

Dicionário de dados completo (schema, tipos, origem por campo): ver
[`data/dicionario_de_dados.md`](data/dicionario_de_dados.md).

### 7.3 Como calcular o custo interno por KM

1. Custo por OS: `total_custo_interno` de `fato_wo_ml`.
2. Agregar por carreta × mês (a partir de `data_os`).
3. KM do período: Δ de `km_acumulado` (fato_readings) por carreta/mês,
   tratando resets de odômetro.
4. Indicador: `custo_interno_total_mes / km_rodado_mes` por carreta.
5. Enriquecer com `dim_carretas` (idade, classe, reefer) e `fato_contratos`
   (tipo, franquia).

## 8. Variável-alvo (Y)

```text
custo_manutencao_interno_por_km
```

Grão de origem: `total_custo_interno` em `fato_wo_ml` (uma OS), agregado
para carreta × mês e dividido pelo KM rodado no período. Os custos estão em
**dólares canadenses (CAD)** e são deflacionados a valor presente (base
dez/2025) via **CPI all-items Canada** (Statistics Canada, vetor
v41690973) antes da modelagem; previsões podem ser reexpressas em valor
nominal futuro para fins de orçamento.

## 9. Variáveis explicativas (X)

### 9.1 Quantitativas naturais

| Variável | Origem |
| --- | --- |
| `ano_modelo` | dim_carretas / fato_wo_ml |
| `eixos` | dim_carretas / fato_wo_ml |
| `comprimento` | dim_carretas / fato_wo_ml |
| `km_acumulado_data_os` | fato_wo_ml |
| `delta_km_desde_ultima_os` | fato_wo_ml |
| `franquia_km_mensal` | fato_contratos |

### 9.2 Qualitativas naturais

| Variável | Origem |
| --- | --- |
| `cod_montadora` | dim_carretas / fato_wo_ml |
| `cod_modelo` | dim_carretas / fato_wo_ml |
| `flag_refrigerado` | dim_carretas / fato_wo_ml |
| `provincia_estado` | fato_wo_ml |
| `vmrs` | fato_wo / fato_wo_ml |
| `classe` / `grupo_manutencao` | dim_carretas |
| `tipo_contrato` (RENTAL/LEASE) | fato_contratos |
| `tipo_manutencao` (MAINT/NET/MIX) | fato_contratos |
| `sistema_vmrs` | fato_wo_labour |
| `flag_terceirizado` | fato_wo_labour / fato_wo_parts |
| `flag_garantia` | fato_wo_parts |

### 9.3 Feature engineering

**Já implementadas** (presentes em `fato_wo_ml`):
- `vmrs` (extraído de `solicitacao_reparo` por regex quando há padrão `VMRS:`; quando ausente, assume `01`, que representa MISC)
- `km_acumulado_data_os`
- `delta_km_desde_ultima_os`

Referência dos códigos `vmrs`:

| Código | Significado |
|---|---|
| `01` | MISCELLANEOUS |
| `02` | AIR EQUIPMENT |
| `03` | LIGHTS AND WIRING |
| `04` | BRAKES |
| `05` | LANDING GEAR |
| `06` | BOGIE |
| `07` | DOORS |
| `08` | EXTERIOR BODY |
| `09` | TIRES AND ACCESSORIES (ATA 017) |
| `10` | REEFER |
| `12` | LIFT GATE |
| `13` | INTERIOR BODY |
| `14` | ABS |
| `15` | SCREENS |
| `16` | AUTO GREASER SYSTEM |
| `17` | GPS SYSTEMS |
| `CL` | CLEAN & SWEEP INTERIOR |
| `FS` | FUEL SURCHARGE |
| `MC` | MILEAGE CHARGE |
| `MF` | MANAGEMENT FEES |
| `PM` | PREVENTIVE MAINTENANCE |

**Ainda planejadas:**
- `idade_carreta` (a partir de `data_entrada_servico`)
- `km_por_mes`
- `custo_acum_manutencao`
- `n_os_corretivas`
- `intervalo_medio_os`
- `prop_pecas_garantia` (agregando `flag_garantia` de `fato_wo_parts`)
- `custo_por_componente` (agregando por `sistema_vmrs`)
- `km_desde_ult_troca`
- `regiao_operacao`
- `custo_deflacionado_cpi` (CPI Canadá — custos em CAD)

> ✏️ Atualizar esta divisão conforme cada feature for de fato calculada.

## 10. Análise exploratória (EDA)

### 10.1 Protocolo

**Para cada variável quantitativa (X e Y):**
- Histograma (distribuição, assimetria, necessidade de transformação log)
- Boxplot (outliers, dispersão)
- Estatísticas: N, média, desvio padrão, mínimo, Q1, mediana, Q3, máximo

**Para cada variável qualitativa:**
- Boxplot de Y segmentado por categoria
- Tabela de frequência das categorias
- Estatísticas de Y por categoria: N, média, desvio padrão, mínimo, máximo

Análises complementares:
- Matriz de correlação (Pearson e Spearman) entre X quantitativas e Y
- Análise temporal por data, idade da carreta e quilometragem
- Custo por componente (`sistema_vmrs`), montadora, ano e tipo de contrato
- Segmentação comparativa por perfil operacional

### 10.2 Tabela-resumo de estatísticas descritivas

Calculada sobre as **352.038** observações carreta × mês com Y válido
(`km_rodado_mes ≥ 500`). Fonte: `reports/tables/03b_estatisticas_descritivas.csv`
(gerada por `src/run_03b_eda_variaveis.py`).

| Variável | Tipo | N | Média | DP | Min | Q1 | Mediana | Q3 | Max | Assim. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `custo_manutencao_interno_por_km_deflacionado` (Y) | Y | 352.038 | 0,091 | 0,374 | 0,000 | 0,000 | 0,000 | 0,032 | 29,28 | 14,44 |
| `ano_modelo` | Quant. | 352.006 | 2016,3 | 4,70 | 1981 | 2013 | 2017 | 2019 | 2026 | −0,59 |
| `eixos` | Quant. | 351.608 | 2,08 | 0,29 | 1 | 2 | 2 | 2 | 4 | 3,06 |
| `comprimento` | Quant. | 347.492 | 52,04 | 4,20 | 28 | 53 | 53 | 53 | 60 | −4,42 |
| `idade_carreta` | Quant. | 223.515 | 6,23 | 4,21 | 0,0 | 3,08 | 5,33 | 8,53 | 27,86 | 0,98 |
| `km_rodado_mes` | Quant. | 352.038 | 2.874 | 2.862 | 500 | 994 | 1.937 | 3.789 | 108.359 | 4,62 |
| `km_acumulado` | Quant. | 348.087 | 128.370 | 135.066 | 0 | 36.134 | 85.563 | 179.530 | 7.210.786 | 3,19 |
| `km_por_mes` | Quant. | 223.132 | 1.822 | 2.088 | 0 | 336 | 923 | 2.847 | 23.385 | 1,96 |
| `franquia_km_mensal` | Quant. | 273.524 | 0,66 | 28,71 | 0 | 0 | 0 | 0 | 1.667 | 45,09 |
| `duracao_contrato_meses` | Quant. | 350.236 | 63,7 | 34,2 | 0 | 39,5 | 60,0 | 79,7 | 211,0 | 0,86 |
| `idade_contrato_meses_no_mes` | Quant. | 350.236 | 37,9 | 31,1 | 0 | 14,0 | 30,9 | 53,9 | 209,0 | 1,16 |
| `custo_acum_manutencao` | Quant. | 352.038 | 4.467 | 13.669 | −310 | 604 | 1.962 | 5.229 | 1.934.021 | 94,22 |
| `custo_preventivo_acum` | Quant. | 352.038 | 1.347 | 1.920 | −538 | 215 | 636 | 1.673 | 26.240 | 3,23 |
| `n_os_acum` | Quant. | 352.038 | 14,6 | 94,2 | 0 | 4 | 9 | 18 | 15.006 | 136,45 |
| `n_os_preventivas_acum` | Quant. | 352.038 | 6,67 | 6,12 | 0 | 2 | 5 | 9 | 38 | 1,41 |
| `custo_medio_movel_3m` | Quant. | 351.028 | 161,3 | 405,6 | −1.846 | 0 | 40,8 | 165,9 | 39.095 | 32,18 |
| `custo_preventivo_medio_movel_3m` | Quant. | 351.028 | 49,3 | 140,7 | −249 | 0 | 4,6 | 34,9 | 4.093 | 8,42 |
| `intervalo_medio_os` | Quant. | 319.900 | 101,4 | 75,9 | 0 | 50,0 | 80,6 | 138,7 | 1.644 | 2,57 |
| `meses_desde_ultima_os` | Quant. | 341.714 | 3,37 | 3,64 | 1 | 1 | 2 | 4 | 60 | 4,97 |

Notas de leitura:
- **Y** é zero-inflado (mediana 0, 67% de meses sem custo) e de cauda muito
  longa (assimetria 14,4) → exige `log1p`/perda robusta e leitura em duas partes.
- Assimetrias extremas em `n_os_acum` (máx 15.006) e `custo_acum_manutencao`
  (máx 1.934.021) sinalizam **anomalia de cadastro** em pouquíssimas carretas
  (ver §10.5 e diagnóstico de outliers `03d_diagnostico_outliers.csv`).
- `km_rodado_mes` tem máx de 108.359 km/mês (reset de odômetro residual);
  tratado por winsorização/robustez de árvore.

### 10.3 Correlação com a variável-alvo (seleção de variáveis)

Para decidir quais variáveis entram no modelo, calcular a correlação de
cada X com Y (`custo_manutencao_interno_por_km`) e ranqueá-las por força de
associação:

- **X quantitativas:** correlação de Pearson (relação linear) e Spearman
  (relação monotônica, mais robusta a outliers) com Y.
- **X qualitativas:** força de associação via análise de variância da média
  de Y entre categorias (ex: ANOVA / eta²), ou diferença de média de Y
  entre categorias observada nos boxplots da seção 10.1.
- Ranquear todas as X (naturais + engineered) da maior para a menor
  correlação/associação com Y.
- Priorizar no modelo as variáveis com maior correlação com Y **e** baixa
  colinearidade entre si (ver seção 10.4) — a variável entra se ajuda a
  explicar Y sem duplicar informação de outra já incluída.

Fontes: `reports/tables/03b_correlacao_com_y.csv` (quantitativas) e
`03b_eta_categoricas.csv` (qualitativas). Quantitativas ranqueadas por
**|Spearman|** (mais robusto a outliers). **Nenhuma variável isolada é forte
(máx ρ = 0,22)** — o ganho preditivo vem de interações, o que favorece
árvores/ensembles.

**Quantitativas (Pearson / Spearman com Y):**

| Variável | Pearson | Spearman | Prioridade | Hipótese |
| --- | --- | --- | --- | --- |
| `n_os_acum` | +0,127 | **+0,220** | Alta | H4 |
| `custo_acum_manutencao` | +0,155 | **+0,197** | Alta | H4 |
| `intervalo_medio_os` | −0,051 | **−0,193** | Alta | H4 |
| `n_os_preventivas_acum` | +0,098 | +0,190 | Alta | H4 |
| `custo_preventivo_acum` | +0,104 | +0,165 | Média | H4 |
| `km_acumulado` | +0,066 | +0,155 | Média | H3 |
| `km_por_mes` | −0,014 | +0,123 | Média | H3 |
| `km_rodado_mes` | −0,081 | +0,094 | Cautela (denominador do Y) | H3 |
| `custo_medio_movel_3m` | +0,101 | +0,085 | Média | H4 |
| `comprimento` | −0,022 | −0,067 | Baixa | — |
| `meses_desde_ultima_os` | −0,007 | −0,062 | Baixa | H4 |
| `idade_contrato_meses_no_mes` | +0,023 | +0,049 | Baixa | H1 |
| `ano_modelo` | −0,055 | +0,045 | Baixa | H2 |
| `idade_carreta` | +0,082 | +0,037 | Baixa | H2 |
| `custo_preventivo_medio_movel_3m` | +0,007 | −0,021 | Baixa | H4 |
| `duracao_contrato_meses` | −0,015 | +0,019 | Baixa | H1 |
| `eixos` | +0,020 | +0,004 | Nula | — |
| `franquia_km_mensal` | +0,001 | −0,004 | Nula | H1 |

**Qualitativas (η — força de separação do Y entre categorias):**

| Variável | η | Categorias | Prioridade |
| --- | --- | --- | --- |
| `regiao_operacao` | 0,084 | 46 | Média (a mais forte; H5) |
| `cod_montadora` | 0,068 | 22 | Média |
| `flag_refrigerado` | 0,063 | 2 | Média (reefer desloca o custo) |
| `cod_classe` | 0,056 | 5 | Baixa |
| `tipo_manutencao` | 0,046 | 4 | Fixada em MAINT na modelagem |
| `tipo_contrato` | 0,040 | 3 | Baixa (H1/H5) |
| `cod_grupo_manutencao` | 0,016 | 11 | Nula |

### 10.4 Multicolinearidade

Antes da modelagem, avaliar multicolinearidade entre as variáveis X
quantitativas (naturais + engineered):

- **Matriz de correlação (Pearson)** entre pares de X — sinalizar pares com
  `|r| > 0.7` como candidatos a colinearidade.
- **VIF (Variance Inflation Factor)** para cada X quantitativa — referência
  usual: `VIF > 5` requer atenção, `VIF > 10` indica colinearidade
  problemática.
- Para X qualitativas convertidas via one-hot/dummy, verificar também o VIF
  das colunas resultantes (evitar dummy trap — sempre remover uma categoria
  de referência).
- Ação recomendada quando houver colinearidade: remover uma das variáveis
  correlacionadas, combiná-las (ex: PCA) ou usar métodos robustos a
  colinearidade (árvores, Random Forest, Gradient Boosting).

> ✏️ Preencher após o cálculo: tabela de VIF por variável e decisão tomada
> (manter, remover ou combinar).

| Variável | VIF | Decisão |
| --- | --- | --- |
| `ano_modelo` | | |
| `eixos` | | |
| `comprimento` | | |
| `km_acumulado_data_os` | | |
| `delta_km_desde_ultima_os` | | |
| `franquia_km_mensal` | | |
| ... | | |

### 10.5 Achados

> ✏️ A preencher após execução da EDA.

## 11. Técnicas previstas

### Estatística
- Correlação de Pearson e Spearman.
- Regressão linear simples.
- Regressão linear múltipla.
- Regressão polinomial, se houver justificativa técnica.

### Machine Learning
- Árvore de decisão para regressão.
- Random Forest.
- Gradient Boosting.
- K-Nearest Neighbors.

### Avaliação
- Separação treino/teste (temporal, para evitar vazamento).
- Validação cruzada quando aplicável.
- Normalização ou padronização quando exigida pelo modelo.
- Métricas: `R²`, `RMSE` e `MAE`.

## 12. Metodologia (procedimento passo a passo)

1. Extração e consolidação das bases (`extract_custo_interno_km.sql` →
   `data/raw/*.csv`).
2. Limpeza e tratamento de dados faltantes, outliers e resets de odômetro.
3. Deflação dos custos históricos (CAD) via CPI Canadá (StatCan), base dez/2025.
4. Feature engineering (variáveis derivadas listadas na seção 9.3).
5. Agregação carreta × mês e cálculo do indicador `custo_interno_por_km`.
6. Integração das bases por `id_carreta` (e por período, no caso de
   contratos).
7. Análise exploratória (univariada, bivariada, correlação) — seção 10.
8. Separação treino/teste com corte temporal (evitando vazamento de
   informações futuras).
9. Modelagem estatística e de machine learning (seção 11).
10. Avaliação dos modelos (`R²`, `RMSE`, `MAE`) e seleção do modelo final.

## 13. Estrutura do repositório

```text
.
├── AGENTS.md
├── README.md
└── data/
    ├── dicionario_de_dados.md
    ├── raw/          # dados originais, sem edição manual
    ├── interim/      # dados intermediários
    └── processed/    # bases prontas para análise e modelagem
```

Estrutura recomendada para próximas etapas:

```text
docs/           # referências, briefing e entregas textuais
notebooks/      # EDA, experimentos e modelagem
reports/        # figuras, tabelas e resultados finais
src/            # scripts reutilizáveis de limpeza, features e modelos
```

## 14. Cuidados com dados

- Não versionar dados sensíveis, pessoais ou confidenciais.
- Usar amostras anonimizadas quando for necessário compartilhar dados no
  Git.
- Manter dados brutos em `data/raw/` sem edição manual.
- Registrar filtros, transformações, premissas e exclusões aplicadas.
- Evitar vazamento temporal: informações futuras não devem entrar em
  previsões de períodos passados.
- Atenção a resets de odômetro (`km_reset_em`/`km_reset_para`), que podem
  gerar Δ de KM negativo.
- "Interno" (`charge_flag='I'`) ≠ "preventivo": é o custo absorvido pela
  empresa, de qualquer natureza (preventiva ou corretiva).

## 15. Referências

- Katreddi, Thiruvengadam, Thompson, Schmid e Padmanaban (2023). *Machine
  learning models for maintenance cost estimation in delivery trucks using
  diesel and natural gas fuels.*
- Katreddi, Thiruvengadam, Thompson e Schmid (2023). *Mixed Effects Random
  Forest Model for Maintenance Cost Estimation in Heavy-Duty Vehicles Using
  Diesel and Alternative Fuels.*
- Sun Zhonghui, Guo Yanying, Sun Zhonghong, Yang Shouchen e Hao Baoyu (2024).
  *Maintenance cost prediction for the vehicle based on maintenance data.*
- Adekitan, Adetokun e Okokpujie (2018). *A data-based investigation of
  vehicle maintenance cost components using ANN.*

## 16. Status

Pipeline completo executado (notebooks 00–06 + scripts em `src/`):

- Base analítica mensal construída: 749.664 linhas carreta × mês
  (`data/processed/base_mensal_carreta.csv`), 352.038 observações com alvo
  válido (km ≥ 500/mês).
- Deflação corrigida: custos em CAD deflacionados pelo **CPI Canadá**
  (StatCan v41690973, base dez/2025) — substituindo o IPCA usado em versão
  anterior (`src/run_04_deflacao_cpi.py`).
- EDA variável-a-variável completa (histogramas, boxplots, frequências,
  correlações, eta, VIF) em `reports/figures/eda/` e `reports/tables/03b_*`.
- Modelagem com alvo `custo_manutencao_interno_por_km_deflacionado`
  (população MAINT, split temporal): **Random Forest recomendado — R² =
  0,088, RMSE = 0,242, MAE = 0,132** no teste temporal; zero-inflação de
  67% dos meses.
- Apresentação acadêmica: `docs/Apresentacao_QuatroNorte.pptx` (63 slides,
  perguntas 1–11 da disciplina).
