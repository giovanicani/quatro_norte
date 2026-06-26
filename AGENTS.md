# AGENTS.md

## Contexto do projeto

Este repositorio e o projeto aplicado do MBA para a Quatro Norte Consulting.
O tema central e a previsao de custos de manutencao preventiva de carretas em
uma operacao de leasing, usando dados historicos e tecnicas de ciencia de dados
para estimar o custo futuro por quilometro.

Pergunta do problema:

> Quais fatores mais influenciam os custos de manutencao das carretas e como
> prever esses custos por km futuros com base nos dados historicos?

Objetivo geral:

Analisar dados historicos de manutencao de carretas, identificar os principais
fatores que influenciam os custos e desenvolver um modelo preditivo capaz de
estimar custos futuros.

## Idioma e estilo

- Priorize portugues do Brasil para textos, documentacao, notebooks e entregas.
- Mantenha linguagem academica, objetiva e adequada a um projeto de MBA.
- Explique decisoes tecnicas com clareza, conectando sempre o metodo ao
  problema de negocio.
- Evite conclusoes fortes sem evidencias estatisticas ou analise dos dados.

## Escopo analitico

O projeto deve considerar, quando os dados estiverem disponiveis, a integracao
das seguintes fontes por `id_carreta`:

- Contratos: `id_contrato`, `duracao_meses`, `tipo_contrato`, `valor_mensal`,
  `data_inicio`, `data_fim`.
- Garantias e pecas: `id_peca`, `categoria_peca`, `custo_peca`,
  `em_garantia`, `fornecedor`.
- Ordens de servico: `id_os`, `data_os`, `tipo_manutencao`, `componente`,
  `custo_mao_obra`, `custo_total`.
- Quilometragem: `data_leitura`, `km_acumulado`, `km_periodo`.
- GPS e telemetria: `timestamp`, `latitude`, `longitude`, `velocidade_media`,
  `horas_uso`, `tipo_rota`.

Variavel-alvo principal:

- `custo_manutencao_preventiva_por_km`

Os custos historicos devem ser deflacionados a valor presente, por IPCA ou
indice setorial apropriado, antes da modelagem. Quando necessario para
orcamento, a previsao pode ser reexpressa em valor futuro nominal.

## Hipoteses de trabalho

- Contratos de leasing com maior duracao tendem a apresentar custos de
  manutencao mais elevados.
- Carretas com maior tempo de utilizacao tendem a demandar maiores gastos com
  manutencao.
- O aumento da quilometragem percorrida esta associado ao aumento dos custos.
- O historico de manutencoes anteriores e relevante para prever custos futuros.
- Variaveis operacionais e caracteristicas contratuais podem influenciar
  significativamente o custo de manutencao.

## Feature engineering esperado

Ao preparar dados para analise ou modelagem, considere derivar variaveis como:

- `idade_carreta`: anos desde a fabricacao.
- `km_por_mes`: intensidade media de rodagem.
- `custo_acum_manutencao`: gasto total acumulado.
- `n_os_corretivas`: quantidade de falhas ou manutencoes nao programadas.
- `intervalo_medio_os`: dias medios entre manutencoes.
- `prop_pecas_garantia`: proporcao de pecas cobertas por garantia.
- `custo_por_componente`: custo por sistema, como freio, pneu, refrigeracao,
  suspensao ou estrutura.
- `km_desde_ult_troca`: desgaste estimado desde a ultima troca relevante.
- `regiao_operacao`: cluster de rota derivado de GPS ou telemetria.
- `custo_deflacionado_ipca`: custo em reais a valor presente.

## Analise exploratoria

Antes de modelar, priorize:

- Estatistica descritiva dos custos por km.
- Distribuicao, assimetria e outliers dos custos.
- Matriz de correlacao com Pearson e Spearman.
- Evolucao temporal do custo por data, idade e quilometragem.
- Comparacao por montadora, ano, tipo de contrato e componente.
- Analise de valores ausentes e criterios de tratamento.
- Decomposicao dos custos por sistema da carreta.

## Modelagem

Tecnicas inicialmente alinhadas ao projeto:

- Regressao linear simples.
- Regressao linear multipla.
- Regressao polinomial, se houver justificativa.
- Arvore de decisao para regressao.
- Random Forest.
- Gradient Boosting.
- K-Nearest Neighbors.

Boas praticas:

- Separar treino e teste antes de avaliar desempenho.
- Usar validacao cruzada quando o volume de dados permitir.
- Padronizar ou normalizar variaveis quando o modelo exigir.
- Comparar modelos com `R2`, `RMSE` e `MAE`.
- Registrar premissas, filtros, exclusoes e transformacoes aplicadas.
- Evitar vazamento de dados temporais: informacoes futuras nao devem entrar em
  previsoes de periodos passados.

## Estrutura recomendada

Use esta organizacao quando forem adicionados artefatos ao repositorio:

```text
data/
  raw/          # dados originais, sem edicao manual
  interim/      # dados intermediarios
  processed/    # bases prontas para analise/modelagem
docs/           # referencias, briefing e entregas textuais
notebooks/      # EDA, experimentos e modelagem
reports/        # figuras, tabelas e resultados finais
src/            # scripts reutilizaveis de limpeza, features e modelos
```

Nao versionar dados sensiveis, dados pessoais, bases grandes ou arquivos que
violem restricoes de confidencialidade. Quando necessario, use amostras
anonimizadas e documente a origem esperada dos dados.

## Referencias do infografico

- Katreddi, Thiruvengadam, Thompson, Schmid e Padmanaban (2023):
  machine learning para estimativa de custo de manutencao em caminhoes de
  entrega.
- Katreddi, Thiruvengadam, Thompson e Schmid (2023):
  Mixed Effects Random Forest para estimativa de custo de manutencao em
  veiculos pesados.
- Sun Zhonghui, Guo Yanying, Sun Zhonghong, Yang Shouchen e Hao Baoyu (2024):
  previsao de custo de manutencao com base em dados de manutencao veicular.
- Adekitan, Adetokun e Okokpujie (2018):
  componentes de custo de manutencao veicular usando ANN.

