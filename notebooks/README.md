# Notebooks

Os notebooks são agora a **fonte única e reprodutível** do projeto. Toda a
lógica que antes vivia em `src/*.py` foi convertida célula a célula, para que a
análise possa ser executada e auditada passo a passo. Não há mais scripts `.py`.

## Ordem de execução

Executar na ordem abaixo. Cada notebook grava artefatos em `data/processed/`
e `reports/` que os seguintes consomem.

| # | Notebook | Papel |
| --- | --- | --- |
| 00 | `00_contexto_inventario_dados.ipynb` | Inventário das bases brutas e modelo estrela |
| 01 | `01_qualidade_integridade_dados.ipynb` | Qualidade, chaves, custos, odômetro e datas |
| 02 | `02_base_analitica_mensal.ipynb` | Base `id_carreta × ano_mes` → `data/processed/base_mensal_carreta.csv` |
| 04 | `04_deflacao_custos_cpi_canada.ipynb` | Deflação CAD por CPI Canadá (dez/2025) → `base_mensal_carreta_deflacionada.csv` |
| 03b | `03b_eda_variaveis.ipynb` | EDA variável-a-variável, correlações, eta², VIF |
| 03c | `03c_estatisticas_resumo.ipynb` | Estatísticas-resumo do alvo e evolução anual |
| 03d | `03d_diagnostico_outliers.ipynb` | Diagnóstico de outliers (IQR/percentis) |
| 05 | `05_modelagem_preditiva.ipynb` | Modelagem MAINT com split temporal, hurdle, VIF, importâncias |
| 06 | `06_resultados_recomendacoes.ipynb` | Tabelas finais `06_*`, hipóteses e recomendações |
| 08 | `08_build_apresentacao.ipynb` | Monta o deck `.pptx` a partir de `reports/` (requer `python-pptx`) |

> A EDA (03b/03c/03d) roda **depois** da deflação (04), pois usa o alvo
> deflacionado `custo_manutencao_interno_por_km_deflacionado`.

## Painel de leitura

- `07_painel_resultados.ipynb` **não reexecuta** o pipeline: apenas lê tabelas
  e figuras já geradas em `reports/` para leitura rápida dos resultados.

## Convenção

```text
notebooks/  = fonte reprodutível (executar 00 → 08 na ordem acima)
data/       = raw (imutável) · processed (gerado pelos notebooks)
reports/    = tabelas e figuras geradas
```
