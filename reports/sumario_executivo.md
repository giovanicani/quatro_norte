# Sumario executivo - Projeto Quatro Norte

Atualizado em 2026-07-06. Alvo oficial do projeto:
`custo_manutencao_interno_por_km_deflacionado` (custo interno total por km,
CAD deflacionados pelo CPI Canada, base dez/2025). Substitui a versao
anterior (alvo preventivo + IPCA), preservada como historico em
`docs/historico/revisao_feedback.md`.

## Pergunta da pesquisa

Quais sao os fatores que mais influenciam o custo de manutencao interno das
carretas — e como prever esse custo por km futuro com base nos dados
historicos?

## Resposta ao problema

Os fatores dominantes sao o **historico operacional da carreta**: numero de
OS acumuladas (Spearman +0,22), custo interno acumulado (+0,20) e intervalo
medio entre OS (-0,19). Atributos estaticos (ano do modelo, eixos,
comprimento) e caracteristicas contratuais (duracao, franquia) tem efeito
fraco isoladamente. Entre as categoricas, regiao de operacao (eta = 0,084),
montadora (0,068) e flag reefer (0,063) deslocam o custo, mas nenhuma e
forte sozinha.

A capacidade de identificar fatores e maior que a de prever o valor pontual:
a base e zero-inflada (67,1% dos meses carreta x mes sem custo interno) e o
custo mensal tem forte componente aleatorio. O modelo apoia priorizacao e
planejamento orcamentario, nao previsao pontual precisa.

## Dados e deflacao

- Base mensal: 749.664 linhas carreta x mes; 352.038 observacoes com alvo
  valido (km_rodado_mes >= 500).
- Custos em CAD deflacionados pelo CPI all-items Canada (StatCan v41690973),
  mes-base dez/2025. Custo interno total: CAD 79,0 mi nominais = CAD 84,3 mi
  reais.
- Mesmo em valores reais, o custo medio por km cresceu de CAD 0,074 (2020)
  para CAD 0,126 (2025) — tendencia genuina, nao inflacao.

## Desempenho preditivo (teste temporal, populacao MAINT)

- Modelo recomendado: **Random Forest** (menor RMSE entre os elegiveis).
- R2 = 0,086 | RMSE = 0,2424 | MAE = 0,1317.
- Comparacao: gradient boosting R2 = 0,077; hurdle (ocorrencia x magnitude)
  R2 = 0,071; modelos lineares R2 = 0,036-0,041; KNN (benchmark amostral)
  R2 = 0,005.
- Anti-vazamento aplicado: features historicas defasadas, split temporal
  (teste = ultimos 12 meses) e `regiao_operacao` defasada em 1 mes por
  carreta.

## Principais fatores do modelo (permutation importance, teste temporal)

1. km_rodado_mes (atencao: tambem denominador do alvo — relacao em parte
   mecanica; para uso futuro requer km planejado/previsto)
2. custo_acum_manutencao
3. custo_preventivo_medio_movel_3m
4. flag_refrigerado
5. intervalo_medio_os

## Hipoteses avaliadas

- H1 duracao de contrato => custo: NAO SUPORTADA (Spearman +0,02).
- H2 idade => custo: PARCIAL (efeito direto fraco, +0,04; idade opera via
  historico acumulado).
- H3 quilometragem => custo: PARCIAL (km_acumulado +0,16; km mensal tem
  relacao mecanica com o denominador).
- H4 historico preve custo futuro: SUPORTADA (bloco mais forte do ranking).
- H5 operacao/contrato influenciam: PARCIAL (regiao eta 0,084; reefer e
  montadora deslocam medianas; efeito contratual fraco).

## Limitacoes

- Zero-inflacao de 67%; desempenho pontual modesto — usar como apoio a
  decisao.
- km_rodado_mes e denominador do alvo e feature.
- Cap de outliers (p99,5) calculado antes do split temporal (limitacao
  conhecida).
- Duracao de contratos vigentes censurada em 2025-12.
- GPS com cobertura parcial; regiao derivada das OS (defasada na modelagem).
- Custos negativos (estornos) excluidos da modelagem.

## Recomendacoes

- Orcamento: usar a previsao mensal por carreta como apoio, comunicando o
  desempenho moderado e a alta proporcao de meses sem custo.
- Priorizacao de frota: monitorar carretas com maior historico de OS e
  menor intervalo entre manutencoes — melhor sinal individual de custo.
- Contratos: caracteristicas contratuais nao mostraram efeito relevante;
  precificar pelo perfil operacional (uso, reefer, regiao), nao pela duracao.
- Dados: preservar vinculo peca-linha de mao de obra na extracao; ampliar
  cobertura de GPS para regiao mais precisa.
- Evolucao: Mixed-Effects Random Forest / modelos hierarquicos e modelos
  zero-inflados como proximos passos.
