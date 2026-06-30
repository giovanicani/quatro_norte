# Sumario executivo - Projeto Quatro Norte

## Resposta ao problema

Os custos preventivos de manutencao por km foram aproximados de forma reprodutivel no grao carreta x mes, usando linhas VMRS PM/PREVENTIVE e pecas de OS com linha preventiva. A identificacao de fatores e mais forte do que a capacidade preditiva pura: a base e zero-inflada, com 79.8% dos meses modelados sem custo preventivo, e parte do alvo tem erro de medicao por OS mistas.

O principal achado metodologico e que o problema se divide em duas partes: ocorrencia de custo e magnitude condicional. Depois de remover vazamento temporal, a ocorrencia deixa de parecer quase deterministica e passa a mostrar sinal preditivo moderado; a magnitude do custo por km permanece mais ruidosa. Assim, o R2 baixo do modelo direto deve ser lido como evidencia da dificuldade de estimar valor, nao como ausencia completa de sinal operacional.

## Desempenho preditivo

- Modelo recomendado: random_forest
- Criterio: menor RMSE no conjunto de teste temporal da populacao MAINT
- Alvo: custo_manutencao_preventiva_por_km_deflacionado
- Populacao: tipo_manutencao = MAINT; km_rodado_mes >= piso metodologico
- RMSE no teste temporal: 0.0962
- MAE no teste temporal: 0.0464
- R2 no teste temporal: 0.0630

- Hurdle ROC AUC para ocorrencia de custo: 0.6801
- Hurdle average precision: 0.3325
- Hurdle Brier score: 0.2092
- Hurdle RMSE da previsao esperada: 0.1013

O hurdle nao venceu a Random Forest no RMSE da previsao esperada. Ainda assim, ele ajuda a explicar a natureza do problema: existe algum sinal para estimar a ocorrencia de custo, mas a previsao da magnitude continua sendo o componente mais instavel.


## Alvo-espelho: mao de obra preventiva

A mao de obra preventiva e a parcela mais limpa do alvo, porque e atribuida diretamente por linha VMRS. As pecas seguem alocadas no nivel da OS, o que gera ruido quando a OS mistura tarefas preventivas e nao preventivas.

A comparacao entre alvos deve ser sustentada principalmente pelo R2, que e adimensional. O RMSE e o MAE sao reportados como contexto, mas nao devem ser interpretados como ganho proporcional, pois o alvo de mao de obra tem escala menor que o alvo total com pecas.

- Alvo preventivo total por km - Random Forest: R2 = 0.0630; RMSE = 0.0962; MAE = 0.0464
- Alvo apenas mao de obra preventiva por km - Random Forest: R2 = 0.0819; RMSE = 0.0218; MAE = 0.0122
- Interpretacao: o alvo de mao de obra preventiva e apenas marginalmente mais previsivel (delta R2 = 0.019); isso e sugestivo, mas nao conclusivo, de ruido adicional nas pecas alocadas no nivel da OS. A queda de RMSE e ilustrativa, mas parcialmente mecanica pela diferenca de escala.


## Principais fatores do modelo

O ranking abaixo vem da Random Forest interpretativa, priorizando permutation importance no teste temporal quando disponivel. Ele deve ser lido **dentro da populacao MAINT**, nao como ranking global de toda a frota. O efeito de `tipo_manutencao` deve ser interpretado na EDA comparativa, pois a modelagem principal fixa essa populacao para reduzir confundimento.

- km_rodado_mes: 0.0048
- custo_preventivo_medio_movel_3m: 0.0036
- n_os_acum: 0.0020
- flag_refrigerado: 0.0019
- n_os_preventivas_acum: 0.0017
- km_rodado_acum: 0.0016
- custo_acum_manutencao: 0.0013
- intervalo_medio_os: 0.0011

## Hipoteses avaliadas

- Contratos de maior duracao tendem a maior custo por km: nao suportada nesta EDA (Ocorrencia: Spearman = 0.029; magnitude positiva: Spearman duracao vs custo/km = -0.038)
- Carretas mais antigas tendem a ter maior custo por km: suportada (Ocorrencia: Spearman = -0.068; spread de taxa por quintil = 0.094; magnitude positiva: Spearman idade vs custo/km = 0.354)
- Maior quilometragem mensal esta associada ao custo absoluto: nao suportada nesta EDA (Spearman km_rodado_mes vs custo_preventivo_total_mes = 0.079; ocorrencia = 0.081; custo/km positivo = -0.572 (relacao mecanica com denominador))
- Historico de manutencoes ajuda a prever custo futuro: parcialmente suportada (Maior |Spearman| entre proxies historicos = 0.261; principais proxies: intervalo_medio_os: ocorrencia=-0.141, magnitude=0.261; custo_preventivo_medio_movel_3m: ocorrencia=-0.123, magnitude=-0.205; meses_desde_ultima_os: ocorrencia=0.050, magnitude=0.193; custo_medio_movel_3m: ocorrencia=-0.046, magnitude=-0.172)
- Caracteristicas contratuais influenciam o custo: parcialmente suportada (Razao media por tipo_contrato em MAINT = 1.50; mediana positiva = 1.99; tipo_manutencao na base completa e caveat estrutural NET/MIX, nao tamanho de efeito (25.93))
- Componentes/sistemas concentram parte relevante do custo: suportada (Top 5 sistemas VMRS representam 64.0% do custo de mao de obra)

## Recomendacoes

- orcamento de manutencao: usar previsao mensal por carreta como apoio ao planejamento financeiro, comunicando desempenho preditivo modesto e alta proporcao de meses sem custo
- zero-inflacao: usar a probabilidade de ocorrencia do hurdle como sinal complementar de priorizacao, comunicando que o desempenho e moderado apos remover vazamento temporal
- gestao de frota: monitorar perfis com maior probabilidade prevista de custo preventivo e maior erro historico, usando os fatores recalculados do modelo como priorizacao
- contratos: comparar custo preventivo previsto por km com franquia, duracao e tipo de contrato; tratar NET/MIX separadamente de MAINT
- manutencao preventiva: priorizar investigacao dos sistemas VMRS com maior concentracao de custo de mao de obra
- dados: preservar no extrato o vinculo peca-linha de mao de obra para reduzir ruido nas pecas preventivas; ampliar cobertura historica de GPS
- modelagem futura: avaliar Mixed-Effects Random Forest/MERF, modelos hierarquicos e alternativas zero-infladas para representar efeito-carreta e ocorrencia de custo

## Limitacoes

- GPS tem cobertura parcial, concentrada no fim de 2025.
- A manutencao preventiva e uma aproximacao por VMRS PM/PREVENTIVE; a mao de obra e atribuivel por linha, mas pecas foram alocadas no nivel da OS porque o CSV nao traz o vinculo da peca com a linha de mao de obra.
- Entre OS com linha preventiva, 85.3% tambem possuem linhas nao-preventivas, sinalizando ruido de medicao no alvo preventivo.
- A distribuicao e zero-inflada; o modelo direto tem desempenho preditivo modesto e o hurdle mostra sinal moderado para prever ocorrencia de custo.
- A base praticamente nao registra pecas em garantia; por isso `prop_pecas_garantia` foi mantida como diagnostico, mas retirada da modelagem principal.
- NET/MIX foram tratados como caveat/segmento; a modelagem principal usa MAINT.
- Meses com baixa quilometragem foram excluidos dos alvos por km pelo piso metodologico de 500 km/mes.
- Custos negativos podem representar estornos ou ajustes contabeis.
- O modelo deve ser usado como apoio a decisao, nao como substituto de validacao operacional.
- MERF/modelos hierarquicos sao uma extensao recomendada para tratar explicitamente o efeito individual de cada carreta.
