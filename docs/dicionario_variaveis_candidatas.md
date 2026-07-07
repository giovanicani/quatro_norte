# Dicionário Metodológico das Variáveis Candidatas

Projeto Quatro Norte / MBA — previsão de custo de manutenção interno por km.

Este documento especifica o universo conceitual de **46 variáveis explicativas
candidatas (X)** a serem avaliadas na base analítica mensal, além da
variável-alvo principal:

```text
custo_manutencao_interno_por_km_deflacionado
```

O grão final da modelagem é **carreta × mês**. Algumas variáveis nascem no grão
de OS, peça, leitura de odômetro ou contrato e precisam ser agregadas,
defasadas ou transformadas antes de entrar na base mensal.

## Regras metodológicas

- Toda variável histórica deve usar apenas informação disponível **antes do mês
  previsto**.
- Variáveis calculadas com janelas móveis devem ser fechadas em `t-1`.
  Exemplo: para prever julho/2025, a janela pode usar dados até junho/2025.
- Variáveis contemporâneas ao mês previsto só devem ser usadas quando forem
  conhecidas no momento da previsão ou quando o objetivo for análise
  explicativa, não previsão operacional futura.
- Variáveis com origem em OS devem ser agregadas para `id_carreta × mes`.
- Variáveis quase constantes, muito ausentes, altamente colineares ou com risco
  de vazamento devem ser removidas ou avaliadas em cenários separados.
- `custo_deflacionado_cpi` não é X: é transformação monetária dos custos e do
  alvo para valor real em CAD.

## Variável-alvo

| Variável | Papel | Grão final | Definição | Observação |
| --- | --- | --- | --- | --- |
| `custo_manutencao_interno_por_km_deflacionado` | Y principal | carreta × mês | Custo interno total mensal deflacionado pelo CPI Canadá dividido pelo km rodado no mês. | Alvo oficial do projeto; inclui manutenção preventiva e corretiva internalizada. |

## 1. Variáveis Quantitativas Naturais

| Variável | Origem | Grão original | Grão final | Fórmula / transformação | Defasagem | Risco de vazamento | Hipótese | Objetivo analítico |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `ano_modelo` | `dim_carretas` / `fato_wo_ml` | carreta | carreta × mês | Atributo estático replicado por mês. | Não se aplica. | Baixo. | H2 | Representar geração tecnológica e idade aproximada do ativo. |
| `eixos` | `dim_carretas` / `fato_wo_ml` | carreta | carreta × mês | Atributo estático replicado por mês. | Não se aplica. | Baixo. | H5 | Capturar configuração estrutural associada a carga, desgaste e custo. |
| `comprimento` | `dim_carretas` / `fato_wo_ml` | carreta | carreta × mês | Atributo estático replicado por mês. | Não se aplica. | Baixo. | H5 | Representar porte físico da carreta e perfil operacional. |
| `km_acumulado_data_os` | `fato_wo_ml` | OS | mensal | Usar como insumo para derivar `km_acumulado` mensal; não deve entrar diretamente se o dataset final for mensal. | Deve ser convertido para valor disponível até `t-1`. | Médio se usar OS do próprio mês previsto. | H3 | Medir exposição acumulada ao uso. |
| `delta_km_desde_ultima_os` | `fato_wo_ml` | OS | mensal | Agregar estatísticas mensais ou substituir por variáveis mensais de uso/intervalo. | Deve considerar apenas OS anteriores ao mês previsto. | Médio se calculada com OS futuras ou do mês previsto. | H3/H4 | Medir distância rodada entre eventos de manutenção. |
| `franquia_km_mensal` | `fato_contratos` | contrato | carreta × mês | Contrato vigente no mês; replicar para meses dentro da vigência. | Não se aplica se contrato já era conhecido. | Baixo, salvo contratos corrigidos retroativamente. | H1/H5 | Medir intensidade de uso prevista contratualmente. |

## 2. Variáveis Qualitativas Naturais

| Variável | Origem | Grão original | Grão final | Fórmula / transformação | Defasagem | Risco de vazamento | Hipótese | Objetivo analítico |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cod_montadora` | `dim_carretas` / `fato_wo_ml` | carreta | carreta × mês | Atributo estático; codificar para modelagem. | Não se aplica. | Baixo. | H5 | Comparar padrões de custo entre fabricantes. |
| `cod_modelo` | `dim_carretas` / `fato_wo_ml` | carreta | carreta × mês | Atributo estático; codificar para modelagem. | Não se aplica. | Baixo. | H5 | Capturar diferenças específicas de projeto/modelo. |
| `flag_refrigerado` | `dim_carretas` / `fato_wo_ml` | carreta | carreta × mês | Indicador binário de carreta reefer. | Não se aplica. | Baixo. | H5 | Identificar maior complexidade técnica e custo potencial. |
| `tailgate_flag` | `dim_carretas` / `fato_wo_ml` | carreta | carreta × mês | Indicador binário de plataforma elevatória. | Não se aplica. | Baixo. | H5 | Avaliar efeito de componente adicional sujeito a manutenção. |
| `unit_subtype` | `dim_carretas` / `fato_wo_ml` | carreta | carreta × mês | Categoria do subtipo da unidade; codificar para modelagem. | Não se aplica. | Baixo. | H5 | Segmentar perfis operacionais distintos. |
| `tire_size` | `dim_carretas` / `fato_wo_ml` | carreta | carreta × mês | Categoria/tamanho de pneu; codificar para modelagem. | Não se aplica. | Baixo. | H5 | Testar associação entre configuração de pneus e custo/desgaste. |
| `suspension_type` | `dim_carretas` / `fato_wo_ml` | carreta | carreta × mês | Categoria do tipo de suspensão; codificar para modelagem. | Não se aplica. | Baixo. | H5 | Capturar diferenças técnicas que influenciam manutenção. |
| `new_used_indicator` | `dim_carretas` / `fato_wo_ml` | carreta | carreta × mês | Indicador/categoria de ativo novo ou usado. | Não se aplica. | Baixo. | H2/H5 | Diferenciar ativos com possível histórico prévio de desgaste. |
| `provincia_estado` | `fato_wo_ml` | OS | mensal | Usar região predominante ou última região conhecida antes do mês previsto. | Preferencialmente defasada. | Médio se usar OS do mês previsto. | H5 | Proxy geográfica de operação e ambiente. |
| `vmrs` | `fato_wo` / `fato_wo_ml` | OS | mensal | Agregar por frequência/custo por sistema; não usar OS futura. | Sim, para previsão. | Médio se usar VMRS do mês previsto. | H4/H5 | Classificar sistema/componente da manutenção. |
| `classe` / `grupo_manutencao` | `dim_carretas` | carreta | carreta × mês | Atributo estático; codificar para modelagem. | Não se aplica. | Baixo. | H5 | Agrupar ativos por perfil técnico de manutenção. |
| `tipo_contrato` | `fato_contratos` | contrato | carreta × mês | Contrato vigente no mês. | Não se aplica se conhecido no início do contrato. | Baixo. | H1/H5 | Testar diferença entre rental/lease e custo interno. |
| `tipo_manutencao` | `fato_contratos` | contrato | carreta × mês | Regime vigente no mês; pode ser filtro ou segmentação. | Não se aplica se conhecido no contrato. | Baixo. | H5 | Evitar misturar populações econômicas diferentes. |
| `sistema_vmrs` | `fato_wo_labour` | linha de mão de obra | mensal | Agregar por sistema, frequência, custo ou diversidade até `t-1`. | Sim. | Médio se usar linhas do mês previsto. | H4/H5 | Identificar sistemas críticos que concentram custos. |
| `flag_terceirizado` | `fato_wo_labour` / `fato_wo_parts` | linha de custo | mensal | Proporção ou indicador de custos terceirizados até `t-1`. | Sim. | Médio se usar eventos do mês previsto. | H5 | Capturar diferenças de estrutura de custo. |
| `flag_garantia` | `fato_wo_parts` | linha de peça | mensal | Proporção de peças em garantia até `t-1`. | Sim. | Médio se usar eventos do mês previsto. | H5 | Avaliar impacto de garantia sobre custo interno. |

## 3. Features Derivadas Planejadas

| Variável | Origem | Grão original | Grão final | Fórmula / transformação | Defasagem | Risco de vazamento | Hipótese | Objetivo analítico |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `idade_carreta` | `dim_carretas` | carreta | carreta × mês | Diferença entre mês de referência e data de entrada em serviço/fabricação. | Não se aplica, desde que calculada no mês. | Baixo. | H2 | Medir envelhecimento do ativo. |
| `km_por_mes` | `fato_readings` | leitura | carreta × mês | Média mensal histórica de quilometragem rodada. | Preferencialmente até `t-1`. | Médio se usar km do mês previsto para previsão futura. | H3 | Representar intensidade média de uso. |
| `custo_acum_manutencao` | custos de OS | OS/linha de custo | carreta × mês | Soma acumulada de custo interno até o fim de `t-1`. | Sim. | Alto se incluir custo do mês previsto. | H4 | Capturar histórico acumulado de custo. |
| `n_os_corretivas` | `fato_wo` / `fato_wo_ml` | OS | carreta × mês | Contagem acumulada ou em janela de OS não preventivas até `t-1`. | Sim. | Alto se incluir OS do mês previsto. | H4 | Medir frequência de falhas/intervenções não programadas. |
| `intervalo_medio_os` | `fato_wo` / `fato_wo_ml` | OS | carreta × mês | Média de dias/meses entre OS anteriores ao mês previsto. | Sim. | Alto se usar OS futura. | H4 | Identificar recorrência de manutenção. |
| `prop_pecas_garantia` | `fato_wo_parts` | linha de peça | carreta × mês | Peças em garantia / total de peças, acumulado ou em janela até `t-1`. | Sim. | Médio. | H5 | Medir participação de garantia no histórico de manutenção. |
| `custo_por_componente` | `fato_wo_labour` / `fato_wo_parts` | linha de custo | carreta × mês | Custo acumulado ou em janela por `sistema_vmrs`. | Sim. | Alto se incluir mês previsto. | H4/H5 | Identificar sistemas que explicam custo total. |
| `km_desde_ult_troca` | OS/peças/readings | peça/OS/leitura | carreta × mês | Km acumulado no mês menos km da última troca relevante anterior. | Sim. | Alto se a última troca for no mês previsto ou posterior. | H3/H4 | Aproximar desgaste desde intervenção relevante. |
| `regiao_operacao` | GPS, local da OS ou província | GPS/OS | carreta × mês | Cluster/região predominante conhecida até `t-1`. | Sim para previsão. | Médio se usar local de OS do mês previsto. | H5 | Capturar diferenças regionais de operação. |

## 4. Novas Features Candidatas

| Variável | Origem | Grão original | Grão final | Fórmula / transformação | Defasagem | Risco de vazamento | Hipótese | Objetivo analítico |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `custo_acum_12m` | custos de OS | OS/linha de custo | carreta × mês | Soma do custo interno entre `t-12` e `t-1`. | Sim. | Alto se incluir `t`. | H4 | Medir condição recente do ativo. |
| `n_os_12m` | `fato_wo` / `fato_wo_ml` | OS | carreta × mês | Contagem de OS entre `t-12` e `t-1`. | Sim. | Alto se incluir `t`. | H4 | Medir frequência anual recente de manutenção. |
| `n_os_3m` | `fato_wo` / `fato_wo_ml` | OS | carreta × mês | Contagem de OS entre `t-3` e `t-1`. | Sim. | Alto se incluir `t`. | H4 | Capturar deterioração ou recorrência muito recente. |
| `meses_com_os_12m` | `fato_wo` / `fato_wo_ml` | OS | carreta × mês | Número de meses com ao menos uma OS entre `t-12` e `t-1`. | Sim. | Alto se incluir `t`. | H4 | Diferenciar eventos concentrados de problemas persistentes. |
| `flag_os_mes_anterior` | `fato_wo` / `fato_wo_ml` | OS | carreta × mês | 1 se houve OS em `t-1`, senão 0. | Sim. | Baixo se restrita a `t-1`. | H4 | Capturar sinal de curto prazo. |
| `custo_mes_anterior` | custos de OS | OS/linha de custo | carreta × mês | Custo interno total em `t-1`. | Sim. | Baixo se restrita a `t-1`. | H4 | Medir intensidade recente de manutenção. |
| `custo_por_km_media_6m` | alvo mensal histórico | carreta × mês | carreta × mês | Média do custo por km entre `t-6` e `t-1`. | Sim. | Médio: válido, mas pode dominar como persistência do Y. | H4 | Medir persistência recente do indicador-alvo. |
| `km_rodado_mes_lag_1m` | `fato_readings` / base mensal | leitura/mensal | carreta × mês | Km rodado em `t-1`. | Sim. | Baixo se restrita a `t-1`. | H3 | Representar uso recente sem depender do mês previsto. |
| `km_rodado_media_3m` | `fato_readings` / base mensal | leitura/mensal | carreta × mês | Média de km rodado entre `t-3` e `t-1`. | Sim. | Baixo se restrita ao passado. | H3 | Capturar intensidade recente de operação. |
| `densidade_os_por_10k_km` | OS + readings | OS/leitura | carreta × mês | `n_os_acum / km_rodado_acum * 10000`, usando acumulados até `t-1`. | Sim. | Alto se acumulados incluírem `t`. | H3/H4 | Medir frequência de OS ajustada pela exposição ao uso. |
| `custo_acum_por_10k_km` | custos + readings | OS/leitura | carreta × mês | `custo_acum_manutencao / km_rodado_acum * 10000`, até `t-1`. | Sim. | Alto se acumulados incluírem `t`. | H3/H4 | Medir histórico de custo ajustado pela quilometragem. |
| `n_sistemas_distintos_12m` | `sistema_vmrs` / `vmrs` | OS/linha de mão de obra | carreta × mês | Número de sistemas distintos com OS entre `t-12` e `t-1`. | Sim. | Alto se incluir `t`. | H4/H5 | Medir diversidade de problemas recentes. |
| `flag_reincidencia_sistema_3m` | `sistema_vmrs` / `vmrs` | OS/linha de mão de obra | carreta × mês | 1 se o mesmo sistema aparecer mais de uma vez entre `t-3` e `t-1`. | Sim. | Alto se incluir `t`. | H4 | Capturar falha recorrente ou manutenção incompleta. |
| `idade_x_km_acumulado` | `idade_carreta` + `km_acumulado` | mensal | carreta × mês | `idade_carreta * km_acumulado`, com km disponível até `t-1` quando usado para previsão. | Sim para `km_acumulado`. | Médio se usar km contemporâneo. | H2/H3 | Testar efeito conjunto de idade e uso acumulado. |
| `reefer_x_idade` | `flag_refrigerado` + `idade_carreta` | mensal | carreta × mês | `flag_refrigerado * idade_carreta`. | Não se aplica para flag; idade calculada no mês. | Baixo. | H2/H5 | Testar se envelhecimento pesa mais em carretas refrigeradas. |

## Cenários de Avaliação Recomendados

Para separar poder explicativo real de simples persistência do alvo, recomenda-se
avaliar pelo menos três matrizes de features:

| Cenário | Inclui | Exclui | Objetivo |
| --- | --- | --- | --- |
| A — Base explicativa | Atributos do ativo, contrato, região, uso defasado e histórico de OS/custos. | Médias defasadas do próprio Y, como `custo_por_km_media_6m`. | Medir quais fatores de negócio explicam o custo. |
| B — Base preditiva completa | Todas as variáveis aprovadas, incluindo persistência do Y. | Variáveis com vazamento, baixa variância ou colinearidade excessiva. | Maximizar desempenho preditivo com validação temporal. |
| C — Sensibilidade sem colinearidade forte | Uma variável por família altamente correlacionada. | Duplicatas conceituais, como acumulado total e janela 12m quando competirem entre si. | Avaliar estabilidade de interpretação. |

## Critérios de Seleção

- Remover variáveis com disponibilidade insuficiente ou muitos nulos sem regra
  defensável de imputação.
- Remover variáveis quase constantes, como ocorreu com `prop_pecas_garantia` na
  rodada anterior.
- Avaliar correlação de Pearson e Spearman para quantitativas.
- Avaliar associação por eta/ANOVA ou comparação de distribuição para
  qualitativas.
- Avaliar multicolinearidade (`|r| > 0,7`, VIF > 5 como atenção e VIF > 10 como
  problema relevante).
- Preservar interpretação de negócio: uma feature só deve ser mantida se fizer
  sentido para decisão de manutenção, orçamento ou precificação.
- Comparar desempenho em teste temporal com `R²`, `RMSE` e `MAE`.
