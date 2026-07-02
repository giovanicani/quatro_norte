# Previsão de Custos de Manutenção de Carretas

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

> Quais são os fatores que mais influenciam os custos de manutenção das
> carretas e como prever esses custos por km futuros com base nos dados
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
| `fato_wo_ml` | uma ordem de serviço | Base enriquecida para modelagem (atributos da carreta, KM na data da OS, `total_custo_interno`) |
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
para carreta × mês e dividido pelo KM rodado no período. Deflacionado a
valor presente via IPCA (ou índice setorial) antes da modelagem; previsões
podem ser reexpressas em valor nominal futuro para fins de orçamento.

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
| `classe` / `grupo_manutencao` | dim_carretas |
| `tipo_contrato` (RENTAL/LEASE) | fato_contratos |
| `tipo_manutencao` (MAINT/NET/MIX) | fato_contratos |
| `sistema_vmrs` | fato_wo_labour |
| `flag_terceirizado` | fato_wo_labour / fato_wo_parts |
| `flag_garantia` | fato_wo_parts |

### 9.3 Feature engineering

**Já implementadas** (presentes em `fato_wo_ml`):
- `km_acumulado_data_os`
- `delta_km_desde_ultima_os`

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
- `custo_deflacionado_ipca`

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

> ✏️ Preencher após rodar a EDA. Uma linha por variável X (natural +
> engineered) e uma para Y.

| Variável | Tipo | N | Média | Desvio Padrão | Min | Q1 | Mediana | Q3 | Max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `custo_manutencao_interno_por_km` (Y) | Quant. | | | | | | | | |
| `ano_modelo` | Quant. | | | | | | | | |
| `eixos` | Quant. | | | | | | | | |
| `comprimento` | Quant. | | | | | | | | |
| `km_acumulado_data_os` | Quant. | | | | | | | | |
| `delta_km_desde_ultima_os` | Quant. | | | | | | | | |
| `franquia_km_mensal` | Quant. | | | | | | | | |
| ... | | | | | | | | | |

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

> ✏️ Preencher após o cálculo.

| Variável | Tipo | Correlação com Y (Pearson/Spearman ou eta²) | Prioridade para o modelo |
| --- | --- | --- | --- |
| `ano_modelo` | Quant. | | |
| `eixos` | Quant. | | |
| `comprimento` | Quant. | | |
| `km_acumulado_data_os` | Quant. | | |
| `delta_km_desde_ultima_os` | Quant. | | |
| `franquia_km_mensal` | Quant. | | |
| `cod_montadora` | Quali. | | |
| `flag_refrigerado` | Quali. | | |
| `tipo_contrato` | Quali. | | |
| `tipo_manutencao` | Quali. | | |
| `sistema_vmrs` | Quali. | | |
| ... | | | |

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
3. Deflação dos custos históricos via IPCA.
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

Bases extraídas e integradas (8 CSVs, `data/raw/`); dicionário de dados
completo; feature engineering parcialmente implementada em `fato_wo_ml`;
EDA e modelagem preditiva pendentes.
