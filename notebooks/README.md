# Notebooks

Os notebooks são a **fonte única e reprodutível** do projeto. Toda a análise parte
**exclusivamente** da base consolidada `data/raw/fato_wo_ml_2020-01-01_to_2025-12-31.csv`
(1 linha = 1 ordem de serviço). A extração SQL, o modelo estrela, os *joins* e o
*feature engineering* que originaram esse arquivo são **etapa anterior de preparação**
e não são reexecutados aqui.

Variável resposta do projeto: **custo anual de manutenção por carreta** (`custo_ano_real`,
CAD/ano em valores reais de dez/2025, corrigidos pelo CPI do Canadá). Grão: **carreta × ano**.

## Ordem de execução

Executar na ordem abaixo. Cada notebook grava artefatos em `data/processed/` e
`reports/` que os seguintes consomem.

| # | Notebook | Papel |
| --- | --- | --- |
| 00 | `00_contexto_inventario_dados.ipynb` | Contexto + inventário da base consolidada única |
| 01 | `01_qualidade_integridade_dados.ipynb` | Qualidade e integridade da base consolidada |
| 02 | `02_base_analitica_anual.ipynb` | Base `carreta × ano` → `data/processed/base_anual_carreta.csv` |
| 04 | `04_deflacao_custos_cpi_canada.ipynb` | Deflação CAD pelo CPI Canadá (dez/2025) → `base_anual_carreta_deflacionada.csv` |
| 03b | `03b_eda_variaveis.ipynb` | EDA variável-a-variável, relação X↔Y, ranking, eta, VIF |
| 03c | `03c_estatisticas_resumo.ipynb` | Estatísticas-resumo do Y anual e evolução |
| 03d | `03d_diagnostico_outliers.ipynb` | Diagnóstico de outliers por variável |
| 05 | `05_modelagem_preditiva.ipynb` | Seleção de variáveis + modelagem (2 cenários, split temporal, importâncias) |
| 06 | `06_resultados_recomendacoes.ipynb` | Tabelas finais `06_*`, hipóteses e recomendações |
| 08 | `08_build_apresentacao.ipynb` | Monta o deck `.pptx` a partir de `reports/` (requer `python-pptx`) |

> A EDA (03b/03c/03d) roda **depois** da deflação (04), pois usa o alvo real
> `custo_ano_real`. A modelagem (05) é apresentada como **consequência** da EDA, do
> ranking e da seleção de variáveis.

## Painel de leitura

- `07_painel_resultados.ipynb` **não reexecuta** o pipeline: apenas lê tabelas e
  figuras já geradas em `reports/` para leitura rápida.

## Dependências

`pandas`, `numpy`, `matplotlib`, `scipy`, `scikit-learn` (modelagem), `python-pptx`
(deck). A série de CPI (`data/raw/cpi_canada_statcan_2020_2025.csv`) é dado público da
Statistics Canada (vetor v41690973).

## Histórico

`notebooks/historico/` guarda a versão anterior (grão mensal, custo por km, baseada nas
7 tabelas do modelo estrela), preservada para rastreio metodológico.

## Convenção

```text
notebooks/  = fonte reprodutível (executar 00 → 08 na ordem acima)
data/       = raw (imutável) · processed (gerado pelos notebooks)
reports/    = tabelas e figuras geradas
```
