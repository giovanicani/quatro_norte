# AGENTS.md

## Contexto do projeto

Este repositorio e o projeto aplicado do MBA para a Quatro Norte Consulting.
O tema central e analisar e modelar o **custo anual de manutencao por carreta**
(CAD/ano, em valores reais corrigidos pelo CPI do Canada) de uma operacao de
leasing/rental no Canada, no grao **carreta x ano**.

> ⚠️ **Fonte unica.** Toda a analise parte EXCLUSIVAMENTE de
> `data/raw/fato_wo_ml_2020-01-01_to_2025-12-31.csv`. Extracao SQL, modelo estrela,
> joins e feature engineering = etapa anterior de preparacao (nao reexecutar).
> Ver `docs/revisao_contrato_2026-08-16.md` (autoritativo) e
> `docs/revisao_anual_2026-07-07.md`.
>
> 🆕 **2026-08-16.** A base foi reextraida: **29 colunas** (25 antes), **217.217 OS**,
> **9.585 carretas**. Passou a incluir dados de CONTRATO — a fonte segue unica, sem
> joins novos. Resultados publicados em `reports/` sao da base anterior e estao
> PENDENTES de recalculo.

Pergunta do problema:

> Quais fatores mais influenciam o custo ANUAL de manutencao das carretas e como
> estima-lo a partir de suas caracteristicas operacionais, historicas e estruturais?

Objetivo geral:

Analisar os fatores que influenciam o custo anual de manutencao por carreta,
identificar as variaveis de maior capacidade explicativa e desenvolver modelos
estatisticos e de ML capazes de estima-lo.

## Idioma e estilo

- Priorize portugues do Brasil para textos, documentacao, notebooks e entregas.
- Mantenha linguagem academica, objetiva e adequada a um projeto de MBA.
- Explique decisoes tecnicas com clareza, conectando sempre o metodo ao
  problema de negocio.
- Evite conclusoes fortes sem evidencias estatisticas ou analise dos dados.

## Escopo analitico

O estudo usa apenas a base consolidada `fato_wo_ml` (grao de OS), agregada para o
grao **carreta x ano**. As variaveis candidatas derivam dessa fonte: atributos
do ativo (montadora, ano_modelo, eixos, comprimento, refrigerado, subtipo, pneu,
suspensao, novo/usado), idade, geografia (regiao/provincia), exposicao
(km_acumulado, km_rodado_ano), operacao do ano (n_os, diversidade VMRS, share PM),
historico defasado (custo/OS de anos anteriores) e **contrato** (tipo de manutencao,
tempo de contrato, cliente).

CONTRATO ESTA NO ESCOPO desde 2026-08-16 (hipotese H6, desdobrada em H6a duracao e
H6b tipo), derivado da propria fonte unica. Restricoes firmadas:
`franquia_km_mensal_contrato` REMOVIDA (99,8% zeros); `cod_cliente` NAO entra como
categorica bruta (597 categorias, risco de memorizacao). Regras de agregacao anual em
`docs/dicionario_variaveis_candidatas.md` §4.

POPULACAO (D6, firmada em 2026-08-16): `tipo_manutencao = 'MAINT'` — retomada do
criterio da fase mensal, que se perdeu na virada anual so por ausencia do dado.
Aplicar como FLAG na base anual (`populacao_maint_flag`), NAO excluir linhas: a base
guarda todas as carreta-anos e a modelagem filtra pela flag. Consequencia:
`tipo_manutencao` NAO entra como feature (constante na populacao filtrada); H6b e
respondida na EDA sobre a base completa, e H6a (tempo de contrato) e a hipotese de
contrato que entra no modelo.

Fora de escopo (exigiriam outras tabelas): `tipo_contrato` (RENTAL/LEASE), mao de obra
detalhada, pecas e leituras de odometro dedicadas.

Variavel-alvo principal:

- `custo_ano_real` — custo anual de manutencao por carreta (CAD/ano, real dez/2025).

Os custos sao deflacionados a valor presente pelo **CPI all-items do Canada**
(Statistics Canada, vetor v41690973, base dez/2025) antes da modelagem.

## Hipoteses de trabalho (unidade anual)

- H1 — A idade da carreta eleva o custo anual.
- H2 — Maior quilometragem/uso esta associada a maior custo anual.
- H3 — O historico de manutencao (anos anteriores) preve o custo futuro.
- H4 — Caracteristicas do ativo (montadora, subtipo, refrigeracao) influenciam o custo.
- H5 — A regiao de operacao influencia o custo.
- H6 — O tipo de manutencao contratual (MAINT/NET/MIX) influencia o custo anual
  absorvido pela empresa.
- H7 — O tempo de contrato ate o reparo influencia o custo anual.

(H6 e H7 entraram em 2026-08-16, com a chegada dos dados de contrato a fonte unica.)

## Feature engineering esperado

Ao preparar dados para analise ou modelagem, derive apenas variaveis sustentadas pela
fonte unica `fato_wo_ml`. Variaveis que exigem pecas, mao de obra detalhada ou leituras
dedicadas devem ser tratadas como fora de escopo desta rodada.

- `idade_carreta`: anos desde a fabricacao.
- `km_rodado_ano`: intensidade anual de uso derivada do odometro nas OS.
- `km_acumulado_fim_ano`: exposicao acumulada no fim do ano.
- `custo_acum_ate_ano_anterior`: gasto historico acumulado defasado.
- `n_os_ano_anterior`: frequencia recente de manutencao.
- `n_os_acum_ate_ano_anterior`: historico acumulado de OS.
- `n_sistemas_vmrs_distintos_ano`: diversidade de sistemas com OS no ano.
- `share_pm_ano`: proporcao de OS com VMRS preventivo no ano.
- `regiao_operacao`: local/regiao predominante da OS.
- `custo_ano_real`: custo anual deflacionado pelo CPI do Canada (CAD, valor presente).
- `tipo_manutencao_ano`: regime contratual predominante no ano (`SEM_CONTRATO` quando
  a OS nao cai em contrato algum).
- `share_maint_ano`: fracao de OS do ano sob regime MAINT.
- `tempo_contrato_meses_fim_ano` / `_inicio_ano`: maturidade contratual (a versao de
  inicio de ano e a unica admissivel no cenario preditivo).
- `trocou_contrato_ano`, `n_clientes_ano`: rotatividade contratual e comercial.

## Analise exploratoria

Antes de modelar, priorize:

- Estatistica descritiva do custo anual por carreta.
- Distribuicao, assimetria e outliers dos custos.
- Matriz de correlacao com Pearson e Spearman; ANOVA/eta para categoricas.
- Evolucao temporal (anual) do custo, idade e quilometragem.
- Comparacao por montadora, ano-modelo, subtipo, refrigeracao e regiao.
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

Na trilha vigente deste repositorio, a execucao operacional esta em `notebooks/`;
`src/` fica apenas como possibilidade futura caso o projeto volte a precisar de
scripts reutilizaveis.

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

