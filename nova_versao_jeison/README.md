# Nova versão — Custo anual de manutenção por carreta

Pacote autocontido da revisão metodológica do projeto. A variável resposta deixa de ser o custo por
quilômetro (CAD/km) e passa a ser o **custo interno anual de manutenção por carreta (CAD/ano)**, corrigido
pela inflação canadense (CPI, Statistics Canada) e trazido para a data-base **dezembro/2025**.

Todo o conteúdo desta pasta é gerado a partir de uma **fonte única de verdade**: o notebook
`07_analise_anual_carreta_ano.ipynb`. Nenhuma figura, tabela ou estatística é produzida manualmente para a
apresentação — reexecutar o notebook regenera integralmente `figuras/`, `tabelas/` e a base anual.

## Estrutura

```
nova_versao_jeison/
├── 07_analise_anual_carreta_ano.ipynb   # notebook único (fonte da verdade)
├── dados/
│   ├── fato_wo_ml_2020-01-01_to_2025-12-31.csv   # base consolidada (223.590 OS, entrada)
│   ├── 04_cpi_fatores.csv                         # fatores de deflação CPI Canadá → dez/2025
│   ├── base_anual_carreta_ano.csv                 # base carreta×ano gerada pelo notebook (47.666 linhas)
│   └── carretas_sem_os_excluidas.csv              # carretas sem ordem de serviço no período
├── figuras/                              # 41 figuras (.png) usadas na apresentação
├── tabelas/                              # 11 tabelas (.csv) de EDA/modelagem
└── apresentacao/
    └── Apresentacao_QuatroNorte_anual.pptx        # apresentação na visão anual
```

## Como reproduzir

Dentro desta pasta:

```bash
python3 -m pip install pandas numpy scipy scikit-learn matplotlib nbformat nbconvert jupyter
python3 -m jupyter nbconvert --to notebook --execute --inplace 07_analise_anual_carreta_ano.ipynb
```

O notebook lê apenas de `dados/` e reescreve `figuras/`, `tabelas/` e `dados/base_anual_carreta_ano.csv`.
Execução completa em ~1 minuto.

## Abordagem metodológica

1. **Base consolidada** — `fato_wo_ml` (grão de ordem de serviço), já filtrada para OS aprovadas, concluídas e
   não canceladas. Não há reconstrução da base, joins ou feature engineering fora do notebook.
2. **Correção monetária (CPI Canadá)** — cada custo é multiplicado pelo fator do CPI *all-items* (StatCan) que
   o converte para dez/2025. A deflação elimina o efeito da inflação e permite comparação temporal consistente.
   Nenhuma referência ao IPCA brasileiro é utilizada.
3. **Base carreta × ano** — agregação das OS por carreta e ano, com atributos de cadastro e variáveis de
   histórico **defasadas** (usam apenas anos anteriores — anti-vazamento).
4. **EDA** — estatística descritiva (N, ausentes, média, mediana, desvio-padrão, coeficiente de variação,
   quartis, mínimo, máximo, assimetria, curtose); distribuições (histogramas, boxplots); relação de cada
   variável com Y (Pearson/Spearman para numéricas; η e ANOVA para categóricas); heatmap de correlação.
5. **Ranking e multicolinearidade** — ordenação por força de associação e diagnóstico de VIF.
6. **Seleção das variáveis** — exclusão das variáveis derivadas do próprio Y (vazamento) e, de cada par
   colinear, manutenção de um representante.
7. **Modelagem** — split temporal (treino 2020–2024, teste 2025) comparando Regressão Linear (log),
   Random Forest e Gradient Boosting; importância por permutação; previsto × observado.

## Principais resultados (teste 2025)

- **Base:** 47.666 observações carreta × ano · custo médio CAD 1.726 / mediana CAD 859 por carreta-ano.
- **Melhor modelo:** Gradient Boosting — R² ≈ 0,69 · MAE ≈ CAD 831 · WAPE ≈ 0,41.
- **Fator dominante:** número de ordens de serviço no ano (`n_os_ano`); mesmo sem essa variável o modelo
  mantém R² ≈ 0,64, sustentado por histórico de custo, quilometragem, tipo e região.

## Tabelas geradas (`tabelas/`)

`anual_descritivas_numericas.csv`, `anual_descritivas_categoricas.csv`, `anual_correlacao_y.csv`,
`anual_eta_categoricas.csv`, `anual_evolucao_y.csv`, `anual_ranking_variaveis.csv`, `anual_vif.csv`,
`anual_variaveis_selecionadas.csv`, `anual_variaveis_excluidas.csv`, `anual_metricas_modelos.csv`,
`anual_importancia_variaveis.csv`.

## Notas de reconciliação

- A base de entrada é a **consolidada** (223.590 OS, com atributos de cadastro), correspondente ao número de
  ordens de serviço reportado na apresentação. A extração bruta pré-consolidação (238.818 OS) permanece no
  repositório como `data/raw/fato_wo_ml_..._bruto_pre_consolidacao_legado.csv`.
- A base consolidada rende **24 variáveis candidatas analisáveis** (15 numéricas + 9 categóricas) após remover
  as variáveis com vazamento e colinearidade. A meta documental de "46 variáveis" pressupõe um conjunto
  ampliado de features que não está integralmente presente na base atual — ponto a reconciliar com a origem
  dos dados.
