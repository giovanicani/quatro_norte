# Plano Analítico em Jupyter Notebooks — Projeto Quatro Norte

## Summary

Construir uma trilha reprodutível de análise em notebooks para responder à pergunta central:
**quais fatores influenciam os custos de manutenção das carretas e como prever o custo futuro por km com base nos dados históricos?**

A solução implementada organiza o trabalho em 7 notebooks sequenciais, partindo do inventário e qualidade dos dados, passando pela construção da base analítica mensal por carreta, análise exploratória das hipóteses, deflação dos custos, modelagem preditiva e consolidação dos resultados para uso no projeto final do MBA.

## Revisão metodológica incorporada

Após revisão crítica, a trilha foi ajustada para responder melhor ao objetivo formal do projeto:

- O alvo principal passou a ser `custo_manutencao_preventiva_por_km`, aproximado por linhas VMRS `PM` / `PREVENTIVE MAINTENANCE` e peças de OS com linha preventiva.
- `custo_manutencao_interno_por_km` foi mantido como alvo secundário/sensibilidade, pois custo interno não é sinônimo de manutenção preventiva.
- `tipo_manutencao` (`MAINT` / `NET` / `MIX`) passou a ser tratado como variável de segmentação e possível confundidor; a modelagem principal usa população `MAINT`.
- Meses com custo preventivo zero foram mantidos, pois representam custo esperado mensal para orçamento.
- Foi definido piso metodológico de `500 km/mês` para cálculo das razões custo/km.
- A quilometragem mensal passou a ser prorrateada entre meses-calendário a partir dos intervalos entre leituras consecutivas.
- Foram adicionadas `duracao_contrato_meses`, `idade_contrato_meses_no_mes`, `prop_pecas_garantia` e `regiao_operacao`; `prop_pecas_garantia` ficou como diagnóstico, pois quase não há registros de garantia suficientes para sustentar modelagem.
- A modelagem passou a incluir validação temporal expansiva, modelo linear com transformação `log1p` e diagnóstico de multicolinearidade por VIF aproximado.
- A zero-inflação do alvo passou a ser tratada explicitamente: além dos modelos diretos, foi incluído um modelo hurdle em duas partes.
- O ruído de medição do alvo preventivo foi quantificado por meio do percentual de OS preventivas que também possuem linhas não preventivas.
- A revisão crítica de `Ajustes.md` foi incorporada: `meses_desde_ultima_os` passou a considerar apenas OS anteriores ao mês previsto, `km_acumulado` passou a ser defasado e contratos fora da janela analítica deixaram de ser clipados artificialmente para dezembro de 2025.
- A EDA passou a alinhar a população principal com a modelagem (`MAINT`) e a separar zero-inflação em duas leituras: ocorrência de custo e magnitude condicional nos meses positivos.
- O resultado do hurdle passou a ser tratado como decomposição metodológica: depois da remoção do vazamento temporal, a ocorrência de custo preventivo tem sinal preditivo moderado, enquanto a magnitude permanece mais ruidosa.
- Foi criado o alvo-espelho `custo_preventivo_mao_obra_por_km`, mais limpo por ser atribuído diretamente por linha VMRS, para comparar contra o alvo preventivo total que inclui peças alocadas no nível da OS.
- A narrativa final foi calibrada para diferenciar capacidade preditiva modesta de identificação de fatores dentro da população `MAINT`.
- A interpretação do ranking de fatores passou a priorizar permutation importance no teste temporal, reduzindo a dependência da importância impurity-based da Random Forest.
- Mixed-Effects Random Forest / MERF foi registrado como extensão metodológica futura, não como modelo executável nesta versão.

## Passo a passo dos notebooks

### 1. `00_contexto_inventario_dados.ipynb`

Objetivo: documentar o problema, inventariar as bases e registrar os riscos iniciais.

Conteúdo:

- Ler os 7 CSVs em `data/raw`.
- Registrar volume de linhas, colunas, chaves e período coberto.
- Confirmar o modelo estrela: `dim_carretas` + fatos por `ID_CARRETA`.
- Identificar granularidade de cada tabela.
- Criar tabelas de inventário e validação do modelo estrela.
- Registrar riscos metodológicos iniciais:
  - GPS cobre apenas parte de 2025.
  - Existem poucos registros de OS em `2026-01-01`.
  - Há custos negativos e zerados.
  - O alvo preventivo precisa ser derivado.
  - `tipo_manutencao` pode confundir conclusões.
  - Meses com baixa quilometragem podem distorcer razões custo/km.

Saídas principais:

- `reports/tables/00_inventario_bases.csv`
- `reports/tables/00_validacao_modelo_estrela.csv`
- `reports/tables/00_riscos_iniciais.csv`

### 2. `01_qualidade_integridade_dados.ipynb`

Objetivo: avaliar se os dados são confiáveis o suficiente para análise e modelagem.

Conteúdo:

- Validar chaves:
  - `ID_CARRETA` de todos os fatos deve existir em `dim_carretas`.
  - `ID_OS` de `fato_wo_labour` e `fato_wo_parts` deve existir em `fato_wo`, quando aplicável.
- Avaliar duplicidades nas chaves primárias.
- Medir valores ausentes por coluna.
- Analisar custos negativos, zerados e extremos.
- Avaliar leituras de odômetro:
  - valores nulos;
  - valores negativos;
  - resets;
  - saltos anormais de quilometragem.
- Verificar consistência temporal.
- Identificar linhas preventivas com base em VMRS `PM` / `PREVENTIVE`.
- Medir proporção de peças em garantia.
- Calcular perfil inicial de duração dos contratos.
- Consolidar regras de tratamento para a base analítica.

Decisões implementadas:

- Manter dados brutos intactos.
- Remover da base analítica eventos de OS com `DATA_OS >= 2026-01-01`.
- Preservar custos negativos no diagnóstico e tratá-los como possíveis estornos/ajustes.
- Tratar deltas inválidos de odômetro antes da alocação mensal.
- Usar piso de `500 km/mês` para cálculo dos alvos por km.
- Classificar manutenção preventiva por VMRS `PM` / `PREVENTIVE`.
- Usar população `MAINT` como base principal da modelagem.

Saídas principais:

- `reports/tables/01_integridade_chaves.csv`
- `reports/tables/01_valores_ausentes.csv`
- `reports/tables/01_diagnostico_custos.csv`
- `reports/tables/01_diagnostico_odometro.csv`
- `reports/tables/01_perfil_preventiva_garantia_contrato.csv`
- `reports/tables/01_regras_tratamento.csv`

### 3. `02_base_analitica_mensal.ipynb`

Objetivo: construir a base principal no grão **carreta × mês**.

Conteúdo:

- Agregar custos internos totais por `ID_CARRETA` e mês:
  - `custo_mao_obra_mes`;
  - `custo_pecas_mes`;
  - `custo_total_mes`.
- Agregar custos preventivos por `ID_CARRETA` e mês:
  - `custo_preventivo_mao_obra_mes`;
  - `custo_preventivo_pecas_mes`;
  - `custo_preventivo_total_mes`;
  - `n_os_preventivas_mes`.
- Quantificar o erro potencial de medição do alvo preventivo:
  - OS com linha preventiva;
  - OS preventivas mistas, isto é, com linhas preventivas e não preventivas;
  - proporção de OS preventivas mistas.
- Calcular quilometragem mensal por prorrateio:
  - ordenar leituras por carreta e data;
  - calcular delta entre leituras consecutivas;
  - remover deltas negativos ou anormais;
  - distribuir o delta proporcionalmente entre os meses-calendário atravessados pelo intervalo.
- Criar alvos:
  - `custo_manutencao_preventiva_por_km`;
  - `custo_preventivo_mao_obra_por_km`;
  - `custo_manutencao_interno_por_km`.
- Aplicar o piso `km_rodado_mes >= 500` para cálculo dos alvos por km.
- Enriquecer com `dim_carretas`:
  - montadora;
  - modelo;
  - ano;
  - idade;
  - eixos;
  - refrigerado;
  - classe;
  - grupo de manutenção.
- Enriquecer com contrato vigente:
  - `tipo_contrato`;
  - `tipo_manutencao`;
  - `franquia_km_mensal`;
  - `cod_cliente`;
  - `cod_local_contrato`;
  - `duracao_contrato_meses`;
  - `idade_contrato_meses_no_mes`.
- Filtrar contratos que não se sobrepõem à janela analítica, evitando atribuir contratos iniciados após 2025 a dezembro de 2025.
- Enriquecer com garantia e geografia operacional:
  - `prop_pecas_garantia`;
  - `regiao_operacao`.
- Construir variáveis históricas defasadas:
  - `custo_acum_manutencao`;
  - `custo_preventivo_acum`;
  - `n_os_acum`;
  - `n_os_preventivas_acum`;
  - `custo_medio_movel_3m`;
  - `custo_preventivo_medio_movel_3m`;
  - `intervalo_medio_os`;
  - `meses_desde_ultima_os`;
  - `km_por_mes`.
- Manter `km_acumulado` como informação disponível até o mês anterior; `km_acumulado_fim_mes` fica apenas como coluna de auditoria.
- Calcular `meses_desde_ultima_os` com base apenas em OS anteriores, sem marcar zero no próprio mês que contém OS.

Saídas principais:

- `data/processed/base_mensal_carreta.csv`
- `reports/tables/02_classificacao_preventiva.csv`
- `reports/tables/02_os_preventivas_mistas.csv`
- `reports/tables/02_diagnostico_km.csv`
- `reports/tables/02_validacao_base_mensal.csv`
- `reports/tables/02_dicionario_base_mensal.csv`

### 4. `03_analise_exploratoria_hipoteses.ipynb`

Objetivo: investigar as hipóteses do projeto com estatística descritiva, visualizações e correlações.

Conteúdo:

- Analisar a distribuição de `custo_manutencao_preventiva_por_km`.
- Medir assimetria, percentis e proporção de zeros.
- Usar a populacao `MAINT` como recorte principal da EDA, mantendo `NET`/`MIX` apenas em comparacoes explicitas de segmentacao.
- Separar a interpretacao do alvo zero-inflado:
  - ocorrencia de custo preventivo no mes;
  - magnitude condicional nos meses com custo positivo.
- Analisar evolução temporal do custo preventivo por km com media e mediana condicional ao positivo, evitando graficos de mediana colados em zero.
- Comparar segmentos por:
  - montadora;
  - ano/modelo;
  - tipo de contrato;
  - tipo de manutenção contratual;
  - refrigerado vs. não refrigerado;
  - grupo de manutenção;
  - região operacional.
- Calcular correlações de Pearson e Spearman.
- Testar as hipóteses do README:
  - duração de contrato vs. custo por km;
  - idade da carreta vs. custo por km;
  - quilometragem mensal vs. custo absoluto e custo/km;
  - histórico de manutenção vs. custo futuro;
  - características contratuais vs. custo;
  - concentração de custos por sistemas VMRS.
- Evitar circularidade na hipótese de quilometragem, testando `km_rodado_mes` contra `custo_preventivo_total_mes` e contra custo/km separadamente.

Saídas principais:

- `reports/tables/03_distribuicao_custo_por_km.csv`
- `reports/tables/03_evolucao_temporal.csv`
- `reports/tables/03_correlacao_pearson.csv`
- `reports/tables/03_correlacao_spearman.csv`
- `reports/tables/03_correlacao_spearman_positivos.csv`
- `reports/tables/03_correlacao_ocorrencia.csv`
- `reports/tables/03_ocorrencia_por_faixa.csv`
- `reports/tables/03_historico_manutencao_proxies.csv`
- `reports/tables/03_segmento_tipo_manutencao_todos.csv`
- `reports/tables/03_custo_por_sistema_vmrs.csv`
- `reports/tables/03_sintese_hipoteses.csv`
- `reports/tables/03_features_candidatas.csv`
- `reports/figures/03_distribuicao_custo_por_km.png`
- `reports/figures/03_evolucao_custo_por_km.png`
- `reports/figures/03_correlacao_spearman.png`

### 5. `04_deflacao_custos_ipca.ipynb`

Objetivo: converter custos históricos nominais para valor presente antes da modelagem.

Conteúdo:

- Incorporar série mensal de IPCA do Banco Central do Brasil, SGS série 433.
- Definir mês-base como `2025-12`.
- Calcular fator de correção monetária.
- Criar custos deflacionados:
  - `custo_total_mes_deflacionado`;
  - `custo_mao_obra_mes_deflacionado`;
  - `custo_pecas_mes_deflacionado`;
  - `custo_preventivo_total_mes_deflacionado`;
  - `custo_preventivo_mao_obra_mes_deflacionado`;
  - `custo_preventivo_pecas_mes_deflacionado`.
- Criar alvos deflacionados:
  - `custo_manutencao_preventiva_por_km_deflacionado`;
  - `custo_preventivo_mao_obra_por_km_deflacionado`;
  - `custo_manutencao_interno_por_km_deflacionado`.
- Comparar distribuição nominal vs. deflacionada.

Saídas principais:

- `data/raw/ipca_mensal_bcb_2020_2025.csv`
- `data/processed/base_mensal_carreta_deflacionada.csv`
- `reports/tables/04_ipca_fatores.csv`
- `reports/tables/04_validacao_deflacao.csv`
- `reports/tables/04_comparacao_nominal_deflacionado.csv`
- `reports/figures/04_nominal_vs_deflacionado.png`

### 6. `05_modelagem_preditiva.ipynb`

Objetivo: treinar e comparar modelos para prever custo preventivo futuro por km.

Conteúdo:

- Definir alvo principal:
  - `custo_manutencao_preventiva_por_km_deflacionado`.
- Definir população principal:
  - `tipo_manutencao = MAINT`;
  - `km_rodado_mes >= 500`;
  - alvo preventivo não nulo.
- Manter meses com custo preventivo zero.
- Excluir apenas alvos negativos e outliers extremos acima do p99,5 para modelagem.
- Definir features:
  - idade da carreta;
  - km mensal;
  - km acumulado;
  - histórico de custos;
  - histórico de OS;
  - duração e idade do contrato;
  - `km_acumulado` defasado;
  - montadora;
  - modelo;
  - refrigerado;
  - tipo de contrato;
  - grupo de manutenção;
  - região operacional.
- Remover `prop_pecas_garantia` da modelagem principal, mantendo-a apenas como diagnóstico por baixa variação observada.
- Separar treino/teste respeitando tempo:
  - treino: meses anteriores;
  - teste: últimos 12 meses.
- Comparar modelos:
  - regressão linear simples;
  - regressão linear múltipla;
  - Ridge;
  - Ridge com `log1p` no alvo;
  - regressão polinomial;
  - árvore de decisão;
  - Random Forest;
  - Gradient Boosting;
  - KNN como benchmark amostral.
- Incluir modelo hurdle em duas partes:
  - classificador para estimar a probabilidade de haver custo preventivo no mês;
  - regressor condicional para estimar a magnitude quando há custo;
  - previsão esperada = probabilidade de ocorrência × magnitude condicional.
- Reportar alvo-espelho de mão de obra preventiva:
  - treinar Random Forest com o mesmo desenho temporal e as mesmas features;
  - comparar `custo_manutencao_preventiva_por_km_deflacionado` contra `custo_preventivo_mao_obra_por_km_deflacionado`;
  - avaliar se a parte mais limpa do custo é mais previsível do que o alvo total com peças alocadas no nível da OS.
- Avaliar com:
  - `R2`;
  - `RMSE`;
  - `MAE`.
- Incluir validação temporal expansiva.
- Diagnosticar multicolinearidade com VIF aproximado.
- Interpretar importância de variáveis da Random Forest com permutation importance no teste temporal como ranking principal.
- Medir erro por segmento.

Observação operacional:

- Para manter execução viável em notebook, modelos pesados usam amostras controladas de treino, mas são avaliados no teste temporal completo quando elegíveis à recomendação.
- KNN é reportado como benchmark amostral e não concorre ao modelo recomendado.

Saídas principais:

- `reports/tables/05_resumo_populacao_modelagem.csv`
- `reports/tables/05_particao_temporal.csv`
- `reports/tables/05_metricas_modelos.csv`
- `reports/tables/05_validacao_temporal_expansiva.csv`
- `reports/tables/05_hurdle_classificacao.csv`
- `reports/tables/05_hurdle_metricas.csv`
- `reports/tables/05_alvo_espelho_mao_obra.csv`
- `reports/tables/05_features_removidas_modelagem.csv`
- `reports/tables/05_vif_features_numericas.csv`
- `reports/tables/05_importancia_variaveis_random_forest.csv`
- `reports/tables/05_importancia_permutacao_random_forest.csv`
- `reports/tables/05_erro_por_segmento.csv`
- `reports/tables/05_modelo_recomendado.csv`

### 7. `06_resultados_recomendacoes.ipynb`

Objetivo: consolidar os achados em formato adequado para apresentação do MBA.

Conteúdo:

- Responder diretamente à pergunta do problema.
- Apresentar ranking dos fatores mais relevantes no modelo.
- Mostrar desempenho do melhor modelo.
- Consolidar status das hipóteses.
- Explicar limitações:
  - GPS parcial;
  - manutenção preventiva aproximada por VMRS;
  - peças preventivas alocadas no nível da OS;
  - alta proporção de meses sem custo preventivo;
  - OS preventivas mistas como fonte de ruído do alvo;
  - ocorrência de manutenção preventiva com sinal preditivo moderado, mas magnitude de custo ruidosa;
  - alvo-espelho de mão de obra preventiva como evidência sobre ruído de peças;
  - `NET`/`MIX` tratados como caveat;
  - piso de quilometragem;
  - custos negativos/estornos;
  - MERF/modelos hierárquicos como extensão futura.
- Traduzir achados para decisão de negócio:
  - orçamento de manutenção;
  - priorização por probabilidade de ocorrência;
  - gestão de frota;
  - contratos;
  - manutenção preventiva;
  - melhoria de dados;
  - evolução de modelagem.

Saídas principais:

- `reports/tables/06_resumo_numerico_final.csv`
- `reports/tables/06_top_fatores_modelo.csv`
- `reports/tables/06_hipoteses_final.csv`
- `reports/tables/06_recomendacoes_negocio.csv`
- `reports/sumario_executivo.md`

## Artefatos e interfaces de dados

Artefatos principais mantidos ou criados:

- `notebooks/00_contexto_inventario_dados.ipynb`
- `notebooks/01_qualidade_integridade_dados.ipynb`
- `notebooks/02_base_analitica_mensal.ipynb`
- `notebooks/03_analise_exploratoria_hipoteses.ipynb`
- `notebooks/04_deflacao_custos_ipca.ipynb`
- `notebooks/05_modelagem_preditiva.ipynb`
- `notebooks/06_resultados_recomendacoes.ipynb`
- `tools/create_analysis_notebooks.py`
- `data/raw/ipca_mensal_bcb_2020_2025.csv`
- `data/processed/base_mensal_carreta.csv`
- `data/processed/base_mensal_carreta_deflacionada.csv`
- `reports/figures/`
- `reports/tables/`
- `reports/sumario_executivo.md`
- `reports/revisao_feedback.md`

Grão da base final:

- uma linha por `id_carreta` × `ano_mes`.

Colunas mínimas da base final:

- identificadores: `id_carreta`, `ano_mes`;
- alvo principal: `custo_manutencao_preventiva_por_km_deflacionado`;
- alvo-espelho: `custo_preventivo_mao_obra_por_km_deflacionado`;
- alvo secundário: `custo_manutencao_interno_por_km_deflacionado`;
- custos: `custo_total_mes`, `custo_mao_obra_mes`, `custo_pecas_mes`, `custo_preventivo_total_mes`;
- operação: `km_rodado_mes`, `km_acumulado`, `km_valido_modelagem_flag`;
- ativo: `idade_carreta`, `cod_montadora`, `cod_modelo`, `ano_modelo`, `flag_refrigerado`;
- contrato: `tipo_contrato`, `tipo_manutencao`, `franquia_km_mensal`, `duracao_contrato_meses`, `idade_contrato_meses_no_mes`;
- garantia e região: `prop_pecas_garantia`, `regiao_operacao`;
- histórico: `custo_acum_manutencao`, `custo_preventivo_acum`, `n_os_acum`, `n_os_preventivas_acum`, `intervalo_medio_os`.

## Validação executada

Todos os notebooks foram executados de ponta a ponta com:

```bash
python -m jupyter nbconvert --execute --to notebook --inplace notebooks/NOME_DO_NOTEBOOK.ipynb
```

Cenários de validação:

- Todos os CSVs de `data/raw` carregam sem erro.
- Nenhum fato possui `ID_CARRETA` fora de `dim_carretas`.
- A soma de custos agregados na base mensal reconcilia com `fato_wo`, respeitando filtros.
- `km_rodado_mes` não contém valores negativos após tratamento.
- Os alvos por km não são calculados abaixo do piso de `500 km/mês`.
- Features históricas usam informações acumuladas até o mês anterior quando representam histórico.
- A separação treino/teste respeita a ordem temporal.
- A validação temporal expansiva evita KFold aleatório em dados de painel.
- Métricas do modelo recomendado são calculadas no teste temporal completo.

Resultados de validação mais recentes:

- Base mensal: `749.664` linhas e `64` colunas.
- Base deflacionada: `749.664` linhas e `76` colunas.
- Observações com alvo preventivo válido: `352.066`.
- Observações `MAINT` usadas na modelagem principal: `332.756`.
- Share de meses modelados com custo preventivo zero: `79,8%`.
- OS com linha preventiva que também possuem linhas não preventivas: `85,3%`.
- Custo interno total reconciliado: `78.996.520,64`.
- Custo preventivo identificado: `24.833.687,14`.
- Validação antileakage: `meses_desde_ultima_os_zero = 0` e `km_acumulado` defasado com `591.923` valores válidos.
- Modelo recomendado: `Random Forest`.
- Alvo do modelo: `custo_manutencao_preventiva_por_km_deflacionado`.
- População do modelo: `tipo_manutencao = MAINT` e `km_rodado_mes >= 500`.
- Métricas no teste temporal: `R2 = 0,063`, `RMSE = 0,0962`, `MAE = 0,0464`.
- Modelo hurdle: `ROC AUC = 0,680`, `average precision = 0,333` e `RMSE = 0,1013` na previsão esperada, abaixo da Random Forest direta.
- Alvo-espelho de mão de obra preventiva: `R2 = 0,082` contra `R2 = 0,063` do alvo preventivo total (`delta R2 = 0,019`), indicando ganho apenas marginal. `RMSE = 0,0218` e `MAE = 0,0122` são reportados apenas como contexto, pois o alvo de mão de obra tem escala menor que o alvo total com peças.
- Hipótese de histórico de manutenção: reclassificada como `parcialmente suportada` ao considerar múltiplos proxies históricos, não apenas `custo_preventivo_acum`.

## Premissas e limitações

- O idioma principal dos notebooks é português do Brasil.
- A manutenção preventiva é uma aproximação operacional, não uma classificação perfeita de negócio.
- Linhas de mão de obra preventivas são identificadas por VMRS `PM` / `PREVENTIVE MAINTENANCE`.
- Peças preventivas são alocadas no nível da OS, pois o CSV de peças não preserva diretamente o vínculo analítico com a linha de mão de obra.
- A mão de obra preventiva é a parcela mais limpa do alvo; o teste espelho mostrou `R2` apenas marginalmente melhor quando o alvo exclui peças alocadas no nível da OS. Essa evidência é sugestiva, não conclusiva. A diferença de `RMSE` não deve ser interpretada proporcionalmente por causa da diferença de escala entre os alvos.
- A maioria dos meses modelados tem custo preventivo zero; portanto, a previsão combina um problema de ocorrência com um problema de magnitude.
- A remoção de vazamento temporal reduziu as métricas preditivas, como esperado; os resultados atuais são metodologicamente mais defensáveis.
- O ranking de fatores da Random Forest deve ser lido dentro da população `MAINT`, não como ranking global da frota.
- A razão por `tipo_manutencao` na base completa é tratada como caveat estrutural de `NET`/`MIX`, não como tamanho de efeito contratual.
- `km_rodado_mes` é usado como denominador do alvo por km e como feature operacional; por isso, sua interpretação exige cautela e a hipótese de quilometragem também foi avaliada contra custo absoluto.
- `prop_pecas_garantia` foi mantida como diagnóstico, mas retirada da modelagem principal porque a base quase não registra peças em garantia.
- `custo_manutencao_interno_por_km` permanece como sensibilidade, mas não é o alvo principal do projeto.
- `NET` e `MIX` não devem ser misturados de forma acrítica com `MAINT` nas conclusões de modelagem.
- GPS é usado apenas como referência limitada, pois sua cobertura está concentrada entre setembro e dezembro de 2025.
- `regiao_operacao` é derivada de `provincia_estado` ou `cod_local_os`, não de cluster geoespacial de GPS.
- O mês-base da deflação é `2025-12`.
- A modelagem é mensal por carreta, pois esse grão equilibra custo, quilometragem, contrato e histórico operacional.
- MERF ou modelos hierárquicos são recomendados como evolução futura para representar explicitamente efeitos específicos por carreta.
