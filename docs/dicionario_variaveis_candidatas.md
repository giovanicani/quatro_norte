# Dicionário Metodológico das Variáveis Candidatas

Projeto Quatro Norte / MBA — **custo anual de manutenção por carreta**.

Este documento especifica o universo de **variáveis explicativas candidatas** deriváveis
da **fonte única** `data/raw/fato_wo_ml_2020-01-01_to_2025-12-31.csv`, além da variável
resposta:

> 🆕 **Atualizado em 2026-08-16.** A fonte única foi reextraída (25 → **29 colunas**) e
> passou a conter **dados de contrato**. O bloco de contrato saiu de *fora de escopo* e
> ganhou a seção **§4**; `franquia_km_mensal_contrato` foi **removida** por variância
> quase nula. Contexto e perfil de qualidade em
> [`revisao_contrato_2026-08-16.md`](revisao_contrato_2026-08-16.md).

```text
custo_ano_real  —  custo anual de manutenção por carreta (CAD/ano, real dez/2025)
```

O grão da modelagem é **carreta × ano**. Como a fonte é uma base de OS
(1 linha = 1 ordem de serviço), as variáveis são **agregadas por carreta × ano** na
construção da base analítica (notebook 02) e as monetárias são deflacionadas pelo CPI
(notebook 04).

## Regras metodológicas

- Variáveis de **histórico** usam apenas informação de anos **anteriores** ao ano de
  referência (defasadas), evitando vazamento temporal.
- Variáveis **contemporâneas** ao ano (uso, diversidade de sistemas) são válidas no
  **cenário explicativo**; no **cenário preditivo** usam-se apenas atributos estáticos
  e histórico defasado.
- Variáveis **quase constantes** são removidas (ex.: `tailgate_flag`, constante).
- **Componentes aritméticos de Y** (`n_os_ano`, `custo_medio_por_os_ano`) são exibidos
  na EDA, mas não competem como explicadores (Y = n_os × custo médio por OS).
- `custo_ano_real` deflacionado não é X: é a própria resposta em valor real.

## Variável-alvo

| Variável | Papel | Grão | Definição |
| --- | --- | --- | --- |
| `custo_ano_real` | Y | carreta × ano | Soma do custo interno das OS da carreta no ano, deflacionada pelo CPI Canadá (dez/2025). Inclui preventiva e corretiva. |

## 1. Atributos do ativo (estáticos por carreta)

| Variável | Tipo | Grão original → final | Transformação | Vazamento | Hipótese | Objetivo |
| --- | --- | --- | --- | --- | --- | --- |
| `cod_montadora` | categórica | carreta → carreta×ano | primeiro valor não nulo; codificar | baixo | H4 | comparar padrões entre fabricantes |
| `ano_modelo` | quantitativa | carreta → carreta×ano | mediana por carreta | baixo | H1 | geração tecnológica do ativo |
| `eixos` | quantitativa | carreta → carreta×ano | mediana | baixo | H4 | configuração estrutural |
| `comprimento` | quantitativa | carreta → carreta×ano | mediana | baixo | H4 | porte físico |
| `flag_refrigerado` | categórica | carreta → carreta×ano | indicador reefer | baixo | H4 | maior complexidade/custo |
| `unit_subtype` | categórica | carreta → carreta×ano | codificar | baixo | H4 | perfis operacionais distintos |
| `tire_size` | categórica | carreta → carreta×ano | codificar | baixo | H4 | configuração de pneus |
| `suspension_type` | categórica | carreta → carreta×ano | codificar | baixo | H4 | diferenças técnicas |
| `new_used_indicator` | categórica | carreta → carreta×ano | novo/usado | baixo | H1/H4 | histórico prévio |
| `descricao_carreta` | categórica | carreta → carreta×ano | proxy de modelo/classe (253 categorias) | baixo | H4 | tipo da unidade |
| `tailgate_flag` | — | — | **REMOVIDA**: constante (variância nula) | — | — | sem informação |

## 2. Derivadas e operacionais (carreta × ano)

| Variável | Tipo | Origem | Transformação | Defasagem | Vazamento | Hipótese | Objetivo |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `idade_carreta` | quantitativa | `data_entrada_servico` | ano − ano de entrada (fallback: ano−ano_modelo) | no ano | baixo | H1 | envelhecimento do ativo |
| `regiao_operacao` | categórica | `cod_local_os` | região predominante do ano (10 categorias) | contemporânea | médio | H5 | proxy geográfica |
| `provincia_estado` | categórica | `provincia_estado` | província predominante (parcial ~54%; imputa DESCONHECIDO) | contemporânea | médio | H5 | proxy geográfica |
| `km_acumulado_fim_ano` | quantitativa | `km_acumulado_data_os` | odômetro de fim de ano | contemporânea | médio | H2 | exposição acumulada |
| `km_rodado_ano` | quantitativa | `km_acumulado_data_os` | Δ odômetro no ano; deltas negativos/>250k → ausente | contemporânea | médio | H2 | uso do ano |
| `n_sistemas_vmrs_distintos_ano` | quantitativa | `vmrs` | nº de sistemas distintos com OS no ano | contemporânea | alto p/ previsão | H3/H4 | diversidade de problemas |
| `share_pm_ano` | quantitativa | `vmrs` | fração de OS preventivas (PM) | contemporânea | alto p/ previsão | H3 | perfil preventivo |
| `vmrs_predominante_ano` | categórica | `vmrs` | sistema predominante | contemporânea | alto p/ previsão | H3/H4 | sistema crítico |
| `n_os_ano` | — | `id_os` | contagem de OS no ano | contemporânea | **componente de Y** | — | não é explicador |
| `custo_medio_por_os_ano` | — | custo/OS | `custo_ano_real / n_os_ano` | contemporânea | **componente de Y** | — | não é explicador |

## 3. Histórico defasado (anti-vazamento)

Calculadas com anos **anteriores** ao de referência; disponíveis no início do ano.

| Variável | Tipo | Transformação | Hipótese | Objetivo |
| --- | --- | --- | --- | --- |
| `custo_ano_anterior` | quantitativa | custo real do ano t−1 | H3 | intensidade recente |
| `n_os_ano_anterior` | quantitativa | nº de OS em t−1 | H3 | frequência recente |
| `custo_acum_ate_ano_anterior` | quantitativa | soma do custo real até t−1 | H3 | histórico acumulado |
| `n_os_acum_ate_ano_anterior` | quantitativa | OS acumuladas até t−1 | H3 | histórico acumulado |
| `anos_ativo_ate_ano_anterior` | quantitativa | nº de anos ativos anteriores | H3 | tempo de histórico |
| `km_acumulado_inicio_ano` | quantitativa | odômetro do fim de t−1 (só cenário preditivo) | H2 | exposição no início do ano |

## 4. Contrato (carreta × ano) — reincluído em 2026-08-16

Derivado dos quatro campos de contrato que passaram a integrar a fonte única:
`tempo_contrato_meses_ate_reparo`, `cod_cliente`, `tipo_manutencao` e
`franquia_km_mensal_contrato`. Os campos são do grão de **OS** e descrevem o contrato
**vigente na data do reparo** — e contrato **não é atributo estático da carreta**:
51,5% das carretas apresentam mais de um `tipo_manutencao` no período. Daí a
necessidade de regra de agregação explícita para o grão anual.

| Variável | Tipo | Origem | Transformação | Defasagem | Vazamento | Hipótese | Objetivo |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `tipo_manutencao_ano` | categórica | `tipo_manutencao` | moda das OS do ano; ausente → `SEM_CONTRATO` (nível informativo, não imputação) | contemporânea | baixo | H6b | regime contratual de manutenção |
| `share_maint_ano` | quantitativa | `tipo_manutencao` | fração de OS do ano com `MAINT` | contemporânea | baixo | H6b | intensidade do regime MAINT |
| `tempo_contrato_meses_fim_ano` | quantitativa | `tempo_contrato_meses_ate_reparo` | máximo observado no ano | contemporânea | médio | H6a | maturidade da relação contratual |
| `tempo_contrato_meses_inicio_ano` | quantitativa | idem | valor de fim de t−1 (**só cenário preditivo**) | defasada | baixo | H6a | maturidade conhecida no início do ano |
| `trocou_contrato_ano` | binária | `tipo_manutencao` + `tempo_contrato_*` | 1 se houve mais de um tipo no ano ou queda no tempo de contrato (indício de novo contrato) | contemporânea | baixo | H6 | rotatividade contratual |
| `n_clientes_ano` | quantitativa | `cod_cliente` | nº de clientes distintos no ano | contemporânea | baixo | H6b | estabilidade do vínculo comercial |
| `cod_cliente_predominante_ano` | categórica | `cod_cliente` | cliente com mais OS no ano — **uso descritivo apenas** | contemporânea | **alto** | — | análise de concentração, não *feature* |
| `franquia_km_mensal_contrato` | — | — | **REMOVIDA**: 99,8% dos valores preenchidos são zero (variância quase nula) | — | — | — | sem informação |

**Restrições de uso registradas:**

- **`cod_cliente` não entra como categórica bruta.** São 597 categorias com 22,8% de
  ausência; em árvore, tende a memorizar o cliente em vez de explicar o custo, e o
  modelo perde utilidade para clientes novos. Se for modelado, apenas via redução
  (top-N + `OUTROS`) ou variável derivada de porte da frota do cliente.
- **`tipo_manutencao` é desbalanceado** (MAINT 89,7% · MIX 1,6% · NET 1,1% · 7,5%
  ausente). η (eta) baixo pode refletir desbalanceamento, não ausência de efeito:
  reportar também custo médio por nível com intervalo de confiança.
- **Colinearidade a vigiar:** `tempo_contrato_*`, `idade_carreta` e
  `anos_ativo_ate_ano_anterior` medem maturidade correlacionada. Se VIF > 10, manter uma
  por família nos modelos lineares; árvores toleram.

## 5. Fora de escopo (exigiriam outras tabelas)

A adesão à **fonte única** deixa de fora variáveis do desenho conceitual original que
dependiam de outras tabelas do modelo estrela:

| Bloco | Variáveis | Tabela de origem |
| --- | --- | --- |
| Contrato (resíduo) | `tipo_contrato` (RENTAL/LEASE) — os demais campos de contrato **entraram** na fonte única (§4) | `fato_contratos` |
| Leituras / km detalhado | `km_por_mes`, `km_rodado_*` mensal, densidades por 10k km | `fato_readings` |
| Mão de obra | `sistema_vmrs`, `flag_terceirizado` | `fato_wo_labour` |
| Peças | `flag_garantia`, `prop_pecas_garantia` | `fato_wo_parts` |
| Ativo (dimensão) | `cod_modelo`, `classe`, `grupo_manutencao` | `dim_carretas` (aproximados por `descricao_carreta`) |

Integrar esses blocos em etapa futura ampliaria o conjunto explicativo além da fonte
única atual.

## Cenários de avaliação

| Cenário | Inclui | Objetivo |
| --- | --- | --- |
| **Explicativo** | Atributos + geografia + uso do ano (km, diversidade, share PM) + histórico defasado + **contrato contemporâneo** | Quais fatores explicam o custo anual |
| **Preditivo** | Atributos + idade + histórico defasado + odômetro de início de ano + **contrato defasado** (`tempo_contrato_meses_inicio_ano`, tipo do ano anterior) | Estimar o custo do ano sem vazamento |

> **Baseline obrigatório.** Como a base foi reextraída **e** ganhou variáveis de
> contrato na mesma rodada, o notebook `05` deve rodar também um modelo **sem
> contrato** sobre a base nova. Sem esse baseline não é possível separar o efeito da
> reextração do efeito das variáveis novas.

## Critérios de seleção

- Remover variáveis constantes, com ausência excessiva ou risco de vazamento.
- Avaliar Pearson/Spearman (quantitativas) e ANOVA/eta (categóricas).
- Avaliar multicolinearidade (`|r| > 0,7`, VIF > 5 atenção, VIF > 10 problema).
- Preservar interpretação de negócio: a variável só é mantida se fizer sentido para
  orçamento/priorização de manutenção.
- Comparar desempenho em teste temporal (R², RMSE, MAE).
