# AGENTS.md

## Contexto do projeto

Este repositorio e o projeto aplicado do MBA para a Quatro Norte Consulting.
O tema central e analisar e modelar o **custo anual de manutencao por carreta**
(CAD/ano, em valores reais corrigidos pelo CPI do Canada) de uma operacao de
leasing/rental no Canada, no grao **carreta x ano**.

> ⚠️ **Fonte unica.** Toda a analise parte EXCLUSIVAMENTE de
> `data/raw/fato_wo_ml_2020-01-01_to_2025-12-31.csv`. Extracao SQL, modelo estrela,
> joins e feature engineering = etapa anterior de preparacao (nao reexecutar).
> Ver `docs/curadoria_features_2026-09-02.md` (autoritativo em selecao de variaveis,
> populacao e alvos), `docs/revisao_contrato_2026-08-16.md` e
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

POPULACAO (D7, firmada em 2026-09-02 — REVOGA D6): a modelagem usa a **base completa**
(47.715 carreta-anos), nao o recorte `tipo_manutencao = 'MAINT'`. A flag
`populacao_maint_flag` continua na base anual como coluna de auditoria e define o
cenario de comparacao, mas NAO entra como feature. Consequencia: `tipo_manutencao_ano`
volta a ser feature (dummy) e H6b e testada dentro do modelo, nao apenas na EDA.
Ver `docs/curadoria_features_2026-09-02.md` (autoritativo em selecao de variaveis,
populacao e definicao dos alvos).

ALVOS (D8, 2026-09-02): o alvo foi decomposto, porque
`custo_ano_real = n_os_ano x custo_medio_por_os_ano` e identidade aritmetica:
Y1 = `custo_ano_real` (principal), Y2 = `n_os_ano`, Y3 = `custo_medio_por_os_ano`.
Nenhum dos tres entra como feature dos outros. Para 2026: prever Y2 e Y3 e reconstituir
Y1 = Y2 x Y3, comparando com o modelo direto de Y1.

`id_carreta` entra como one-hot (9.584 colunas, D9) por decisao explicita do Grupo, com
a ressalva de memorizacao registrada em `docs/curadoria_features_2026-09-02.md` §2.

Fora de escopo (exigiriam outras tabelas): `tipo_contrato` (RENTAL/LEASE), mao de obra
detalhada, pecas e leituras de odometro dedicadas.

ESTADO EM 2026-09-02 (retomar por aqui — detalhes em
`docs/curadoria_features_2026-09-02.md` §14):

- Pipeline reexecutado sobre a frota completa. Melhor resultado preditivo: Y1
  **decomposto** (Y2 x Y3) com R2 0,4713, acima do direto (0,4418). Y2 R2 0,608;
  Y3 R2 0,085 (elo fraco). Explicativo 0,5776.
- H7 (tempo de contrato) NAO suportada: importancia por permutacao negativa (-0,003).
  H6b (tipo de contrato) e a 4a variavel mais importante. `flag_refrigerado` domina (0,209).
- PENDENTE: decidir 5 variaveis fracas em Y1 mas moderadas/fortes em Y2
  (`cod_montadora`, `tire_size`, `suspension_type`, `ano_modelo`, `new_used_indicator`).
  Conjuntos de features diferentes por alvo sao aceitaveis.
- BUG CONHECIDO no notebook `02`: o desempate de `vmrs_predominante_ano` usa ordem
  alfabetica (`mode().iloc[0]`) em vez da regra do Grupo (codigo mais frequente de toda a
  base). 28,4% dos pares carreta-ano empatam; 11,0% mudariam de categoria, quase sempre
  para `PM`. A variavel subestima manutencao preventiva.
- PENDENTE: nenhuma previsao de 2026 foi gerada — tudo e validacao no teste de 2025.
  Falta projetar km, somar +1 em idade e montar a linha de cada carreta para o ano.
- `notebooks/13_cascata_y2_para_y1.py` esta escrito e nao executado.

Variavel-alvo principal:

- `custo_ano_real` — custo anual de manutencao por carreta (CAD/ano, real dez/2025).

Os custos sao deflacionados a valor presente pelo **CPI all-items do Canada**
(Statistics Canada, vetor v41690973, base dez/2025) antes da modelagem.

## Hipoteses de trabalho (unidade anual)

- H1 — A idade da carreta eleva o custo anual.
- H2 — Maior quilometragem/uso esta associada a maior custo anual.
- H3 — O historico de manutencao (anos anteriores) preve o custo futuro.
- H4 — Caracteristicas do ativo (montadora, subtipo, refrigeracao) influenciam o custo.
- H5 — A regiao de operacao influencia o custo. (FORA DO MODELO desde 2026-09-02:
  `regiao_operacao` e `provincia_estado` retiradas pelo Grupo, com respaldo — eta <= 0,14.)
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

