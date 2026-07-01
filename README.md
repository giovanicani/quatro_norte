# Previsao de Custos de Manutencao de Carretas

Projeto aplicado do MBA para a **Quatro Norte Consulting**, com foco em
ciencia de dados aplicada a uma operacao de leasing de carretas.

O objetivo e analisar dados historicos de manutencao, contratos,
quilometragem, garantias, pecas e telemetria para identificar os fatores que
mais influenciam o custo de manutencao internalizada e desenvolver modelos
capazes de estimar o custo futuro por quilometro.

Neste momento, a analise nao esta limitada a manutencao preventiva. O escopo
considera todas as ordens de servico com custo interno (`charge_flag = 'I'`),
incluindo manutencoes preventivas e corretivas absorvidas pela operacao.

## Pergunta do problema

> Quais sao os fatores que mais influenciam os custos de manutencao das
> carretas e como prever esses custos por km futuros com base nos dados
> historicos?

## Objetivo geral

Analisar os dados historicos de manutencao das carretas para identificar os
principais fatores que influenciam os custos e desenvolver um modelo preditivo
capaz de estimar custos futuros.

## Objetivos especificos

- Coletar, consolidar e organizar dados historicos de manutencao das carretas.
- Realizar analise exploratoria dos dados para identificar padroes, tendencias
  e variaveis relevantes.
- Investigar a relacao entre caracteristicas dos contratos de leasing e custos
  de manutencao.
- Identificar os principais fatores associados aos custos de manutencao.
- Desenvolver e avaliar modelos preditivos para estimar os custos futuros.

## Hipoteses

- Contratos de leasing com maior duracao tendem a apresentar custos de
  manutencao mais elevados.
- Carretas com maior tempo de utilizacao tendem a demandar maiores gastos com
  manutencao.
- O aumento da quilometragem percorrida esta associado ao aumento dos custos.
- O historico de manutencoes anteriores e relevante para prever custos futuros.
- Variaveis operacionais e caracteristicas dos contratos influenciam
  significativamente os custos de manutencao.

## Fontes de dados previstas

| Fonte | Exemplos de variaveis |
| --- | --- |
| Contratos | `id_contrato`, `duracao_meses`, `tipo_contrato`, `valor_mensal`, `data_inicio`, `data_fim` |
| Garantias e pecas | `id_peca`, `categoria_peca`, `custo_peca`, `em_garantia`, `fornecedor` |
| Ordens de servico | `id_os`, `data_os`, `tipo_manutencao`, `componente`, `custo_mao_obra`, `custo_total` |
| Quilometragem | `data_leitura`, `km_acumulado`, `km_periodo` |
| GPS e telemetria | `timestamp`, `latitude`, `longitude`, `velocidade_media`, `horas_uso`, `tipo_rota` |

As bases devem ser integradas preferencialmente por `id_carreta`.

## Variavel-alvo

```text
custo_manutencao_interno_por_km
```

Esse alvo representa o custo total internalizado por quilometro. No nivel da
ordem de servico, a base de modelagem `fato_wo_ml` usa `total_custo_interno`,
calculado como mao de obra interna mais pecas internas.

Os custos historicos devem ser deflacionados a valor presente, usando IPCA ou
indice setorial adequado, antes da modelagem. Quando necessario, as previsoes
podem ser reexpressas em valor futuro nominal para fins de orcamento.

## Feature engineering

Variaveis derivadas inicialmente previstas:

- `idade_carreta`
- `km_por_mes`
- `custo_acum_manutencao`
- `n_os_corretivas`
- `intervalo_medio_os`
- `km_acumulado_data_os`
- `delta_km_desde_ultima_os`
- `prop_pecas_garantia`
- `custo_por_componente`
- `km_desde_ult_troca`
- `regiao_operacao`
- `custo_deflacionado_ipca`

## Analise exploratoria

A EDA deve priorizar:

- Estatistica descritiva dos custos por km.
- Distribuicao dos custos, outliers e valores ausentes.
- Matriz de correlacao com Pearson e Spearman.
- Analise temporal por data, idade da carreta e quilometragem.
- Custo por componente, montadora, ano e tipo de contrato.
- Segmentacao comparativa por perfil operacional.

## Tecnicas previstas

### Estatistica

- Correlacao de Pearson e Spearman.
- Regressao linear simples.
- Regressao linear multipla.
- Regressao polinomial, se houver justificativa tecnica.

### Machine Learning

- Arvore de decisao para regressao.
- Random Forest.
- Gradient Boosting.
- K-Nearest Neighbors.

### Avaliacao

- Separacao treino/teste.
- Validacao cruzada quando aplicavel.
- Normalizacao ou padronizacao quando exigida pelo modelo.
- Metricas: `R2`, `RMSE` e `MAE`.

## Estrutura do repositorio

```text
.
├── AGENTS.md
├── README.md
└── data/
    ├── raw/          # dados originais, sem edicao manual
    ├── interim/      # dados intermediarios
    └── processed/    # bases prontas para analise e modelagem
```

## Bases extraidas

A extracao principal esta em `data/extract_custo_interno_km.sql` e gera oito
CSVs em `data/raw/`:

| Base | Uso principal |
| --- | --- |
| `dim_carretas` | Atributos do ativo |
| `fato_readings` | Leituras de odometro em KM |
| `fato_wo` | Cabecalho da OS com custo interno separado em mao de obra e pecas |
| `fato_wo_ml` | Base de OS enriquecida para modelagem, com atributos da carreta, KM na data da OS, delta de KM desde a OS anterior e `total_custo_interno` |
| `fato_wo_labour` | Linhas de mao de obra interna |
| `fato_wo_parts` | Linhas de pecas internas |
| `fato_contratos` | Contratos de leasing/rental por carreta |
| `fato_gps` | Posicoes GPS por carreta/dia |

Estrutura recomendada para proximas etapas:

```text
docs/           # referencias, briefing e entregas textuais
notebooks/      # EDA, experimentos e modelagem
reports/        # figuras, tabelas e resultados finais
src/            # scripts reutilizaveis de limpeza, features e modelos
```

## Cuidados com dados

- Nao versionar dados sensiveis, pessoais ou confidenciais.
- Usar amostras anonimizadas quando for necessario compartilhar dados no Git.
- Manter dados brutos em `data/raw/` sem edicao manual.
- Registrar filtros, transformacoes, premissas e exclusoes aplicadas.
- Evitar vazamento temporal: informacoes futuras nao devem entrar em previsoes
  de periodos passados.

## Referencias iniciais

- Katreddi, Thiruvengadam, Thompson, Schmid e Padmanaban (2023). Machine
  learning models for maintenance cost estimation in delivery trucks using
  diesel and natural gas fuels.
- Katreddi, Thiruvengadam, Thompson e Schmid (2023). Mixed Effects Random
  Forest Model for Maintenance Cost Estimation in Heavy-Duty Vehicles Using
  Diesel and Alternative Fuels.
- Sun Zhonghui, Guo Yanying, Sun Zhonghong, Yang Shouchen e Hao Baoyu (2024).
  Maintenance cost prediction for the vehicle based on maintenance data.
- Adekitan, Adetokun e Okokpujie (2018). A data-based investigation of vehicle
  maintenance cost components using ANN.

## Status

Repositorio em estruturacao inicial.
