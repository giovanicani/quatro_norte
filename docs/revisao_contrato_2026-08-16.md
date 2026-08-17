# Revisão 2026-08-16 — Reinclusão do contrato no escopo

> **Documento autoritativo desta rodada.** Supersede
> [`revisao_anual_2026-07-07.md`](revisao_anual_2026-07-07.md) apenas nos pontos aqui
> tratados (escopo de contrato, inventário da base e números de população). Todo o
> restante daquela revisão — grão carreta × ano, alvo `custo_ano_real`, deflação pelo
> CPI do Canadá, split temporal, anti-vazamento — **continua valendo**.

> 📖 **Narrativa e rubrica:** a trajetória das reformulações da pergunta, o mapa dos 16
> itens da entrega acadêmica e as implicações para a apresentação estão em
> [`narrativa_do_projeto.md`](narrativa_do_projeto.md).

> ✅ **Pipeline reexecutado em 2026-08-16** (`00`→`06`, `08` e o novo `09`). Os números
> de `reports/`, do `README.md` e do `GUIA_DO_PROJETO.md` refletem a base reextraída.
> Resultados desta rodada em §9.

---

## 1. O que mudou

A empresa disponibilizou os dados de contrato **dentro da própria base consolidada**.
Não há tabela nova, não há join novo: o princípio de **fonte única** permanece
intacto — o CSV `data/raw/fato_wo_ml_2020-01-01_to_2025-12-31.csv` passou de **25 para
29 colunas**.

| Campo novo | Definição (conforme `dicionario_de_dados.md`) |
|---|---|
| `tempo_contrato_meses_ate_reparo` | Meses entre o início do contrato ativo e a `data_os`, com duas casas decimais (`start_date` → `data_os`, ÷ 30,4375) |
| `cod_cliente` | Código do cliente faturado no contrato vigente da carreta no momento do reparo |
| `tipo_manutencao` | Tipo de manutenção do contrato vigente: `MAINT`, `NET` ou `MIX` |
| `franquia_km_mensal_contrato` | Franquia mensal de km prevista no contrato vigente |

**Consequência de escopo:** as hipóteses de contrato, marcadas como *fora de escopo*
desde a revisão de 2026-07-07 por ausência dos dados, **voltam ao escopo** e passam a
ser testáveis a partir da fonte única.

---

## 2. A base foi regenerada — os números vigentes estão defasados

O CSV não recebeu apenas colunas: ele foi **reextraído**. A população mudou.

| Métrica | Documentado (2026-07-07) | CSV atual (2026-08-16) | Δ |
|---|---|---|---|
| Colunas | 25 | **29** | +4 |
| Linhas (OS) | 223.590 | **217.217** | −6.373 (−2,9%) |
| Carretas | 9.859 | **9.585** | −274 (−2,8%) |
| Custo interno nominal | CAD 77,18 mi | **CAD 74,48 mi** | −2,70 mi (−3,5%) |
| Linhas com custo negativo (estornos) | — | 172 | a excluir, como antes |
| OS fora da janela 2020–2025 | 3 (excluídas) | 5 (com `data_os` em 2026) | **excluir**, como antes — ver nota |

`id_os` é único nas 217.217 linhas (sem duplicidade de chave).

**Nota sobre as 5 OS de 2026 — provável artefato de fuso horário.** Todas caem em
`2026-01-01`, entre **00:22 e 03:11**, somando CAD 2.398,58 (0,003% do custo total) e
todas com `tipo_manutencao = MAINT`. O horário sugere OS de **31/12/2025** convertidas
para UTC (00:23 UTC = 17:23 MST em Calgary), não reparos de madrugada de Ano-Novo.

**Decisão: excluir**, mantendo o tratamento da revisão anterior — a série do CPI termina
em dez/2025 e não há deflator para 2026. O rigor mandaria reatribuí-las a 2025, mas o
efeito é nulo e confirmar a convenção de fuso da extração não se paga. **Descrever a
exclusão como deslocamento de fuso, não como erro de dados**, ao documentar a curadoria.

**Consequência:** toda métrica anterior (49.248 linhas carreta × ano, CAD 82,43 mi reais,
média CAD 1.673,72/ano, R² 0,429 preditivo / 0,572 explicativo) referia-se à base antiga
e **foi recalculada** — ver §9. Não é erro de ninguém: é a consequência esperada de uma
reextração, e o motivo pelo qual a rodada precisou de um baseline (config A) para separar
o efeito da nova extração do efeito das variáveis novas.

---

## 3. Perfil de qualidade dos quatro campos novos

Medido diretamente sobre as 217.217 linhas do CSV atual.

| Campo | Ausentes | Perfil dos preenchidos |
|---|---|---|
| `tempo_contrato_meses_ate_reparo` | 16.250 (**7,5%**) | mín 0 · p25 16,9 · mediana **35,1** · p75 57,0 · p95 105,3 · máx 209,5 meses · média 40,9 · **nenhum negativo** |
| `tipo_manutencao` | 16.250 (**7,5%**) | `MAINT` 194.918 (**89,7%**) · `MIX` 3.582 (1,6%) · `NET` 2.467 (1,1%) |
| `cod_cliente` | 49.429 (**22,8%**) | **597** clientes distintos |
| `franquia_km_mensal_contrato` | 61.642 (**28,4%**) | **99,8% dos preenchidos são zero**; máx 1.667 |

Leitura crítica de cada um:

- **`tempo_contrato_meses_ate_reparo` — o mais promissor.** Boa cobertura, sem valores
  negativos (nenhuma OS antes do início do contrato), distribuição ampla e com sentido
  de negócio direto: mede maturidade da relação contratual no momento do reparo. É a
  variável que efetivamente permite testar "duração de contrato ⇒ custo".
  ⚠️ Correlaciona-se estruturalmente com `idade_carreta` e com o histórico acumulado —
  exigirá checagem de VIF e de redundância antes de entrar em modelo linear.

- **`tipo_manutencao` — utilizável, mas desbalanceado.** Com 89,7% em `MAINT`, as
  categorias `NET` e `MIX` somam 2,7% das OS. Comparações entre níveis terão baixa
  potência; η (eta) tende a ser pequeno por desbalanceamento, não necessariamente por
  ausência de efeito. Recomenda-se reportar também custo médio por nível com intervalo
  de confiança, não apenas η.

- **`cod_cliente` — alta cardinalidade e risco de vazamento conceitual.** 597
  categorias com 22,8% de ausência. Como *feature* bruta em árvore, tende a memorizar o
  cliente em vez de explicar o custo, e o modelo perde utilidade para carretas de
  clientes novos. Uso recomendado: **não entrar como categórica bruta**; usar como
  eixo de análise descritiva (concentração de custo por cliente) e, se entrar em modelo,
  apenas via redução — top-N clientes + `OUTROS`, ou uma variável derivada de porte da
  frota do cliente.

- **`franquia_km_mensal_contrato` — degenerada.** Com 99,8% de zeros entre os
  preenchidos, a variável tem variância praticamente nula e **não sustenta hipótese
  alguma**. Mesmo tratamento dado a `tailgate_flag`: **remover**, documentando o motivo.
  Se o zero significar "sem franquia contratada" em vez de "ausente", o correto é uma
  flag binária `tem_franquia_km` (0,2% de positivos) — que ainda assim é rara demais
  para modelagem, mas honesta na EDA.

**Instabilidade dentro da carreta:** 4.933 das 9.585 carretas (**51,5%**) apresentam mais
de um `tipo_manutencao` ao longo do período. Contrato **não é atributo estático da
carreta** — muda ao longo do tempo. No grão carreta × ano isso obriga uma regra de
agregação explícita (§5).

**Evolução por ano** (`tipo_manutencao`, contagem de OS):

| Ano | MAINT | MIX | NET | sem contrato |
|---|---|---|---|---|
| 2020 | 23.023 | 130 | 104 | 3.463 |
| 2021 | 25.639 | 261 | 131 | 2.001 |
| 2022 | 31.222 | 421 | 439 | 1.379 |
| 2023 | 36.255 | 604 | 626 | 2.421 |
| 2024 | 39.288 | 915 | 612 | 4.060 |
| 2025 | 39.486 | 1.251 | 555 | 2.926 |

`MIX` e `NET` crescem de forma consistente no período — a composição contratual da
frota está mudando, o que reforça o valor de incluir a variável.

---

## 4. Decisões desta revisão

| # | Decisão | Estado |
|---|---|---|
| D1 | Contrato **volta ao escopo**, derivado exclusivamente da fonte única | ✅ Firmada |
| D2 | **Fonte única mantida**: nenhum join com `fato_contratos` ou qualquer outra tabela | ✅ Firmada |
| D3 | `franquia_km_mensal_contrato` **removida** por variância quase nula (99,8% zeros), com registro na tabela de curadoria | ✅ Firmada |
| D4 | `cod_cliente` **não entra como categórica bruta**; uso descritivo e, se modelado, via top-N + `OUTROS` | ✅ Firmada |
| D5 | Pipeline precisa ser **reexecutado ponta a ponta** por causa da reextração da base (§2) | ✅ Firmada |
| D6 | **População: `tipo_manutencao = 'MAINT'`** — retomada do critério original do projeto, implementada como **flag** na base anual (não como exclusão de linhas), seguindo o precedente da fase mensal | ✅ **Firmada pelo Grupo (2026-08-16)** |

### Sobre D6 — filtro `MAINT` (decisão firmada)

**Não é um critério novo: é a retomada do critério original do projeto.** A fase mensal
já modelava só `MAINT` — o filtro foi perdido na virada para o grão anual porque a
coluna não existia na fonte única, não porque tenha sido abandonado. Com o dado de
volta, o critério volta.

A base **não chega filtrada**: verificado em `data/extract_custo_interno_km.sql`, onde
`lra.maint_type` aparece apenas como coluna projetada (linha 328); os únicos filtros da
extração são `charge_flag = 'I'`, `cus_id_owner = 4` e `void_date IS NULL`. Os quatro
regimes convivem no CSV. **O filtro passa a ser aplicado na construção da base analítica
(notebook `02`).**

#### Como implementar: flag, não exclusão

O notebook mensal `02` não deletava linhas — marcava a população:

```python
base["populacao_modelagem_principal_flag"] = (
    base["tipo_manutencao"].eq("MAINT")
    & base["km_valido_modelagem_flag"].eq(1)
    & base["custo_manutencao_preventiva_por_km"].notna()
).astype(int)
```

**Replicar esse padrão no grão anual**, com uma flag `populacao_maint_flag` derivada de
`tipo_manutencao_ano == 'MAINT'`. A base anual guarda todas as carreta-anos; a modelagem
filtra pela flag.

Três vantagens, todas relevantes aqui:

- **O baseline sai de graça.** Rodar com e sem a flag é uma linha de código, não uma
  execução paralela do pipeline — o que resolve a exigência de isolar o efeito da
  reextração (§8, risco 1).
- **A EDA continua completa.** O boxplot de custo por `tipo_manutencao_ano` — a evidência
  visual de H6b — só existe se `NET` e `MIX` estiverem na base.
- **É auditável.** A tabela de curadoria registra quantas carreta-anos ficaram de fora,
  em vez de elas simplesmente desaparecerem.

**Impacto medido sobre o CSV atual:**

| Métrica | Sem filtro | Com `MAINT` | Perda |
|---|---|---|---|
| Ordens de serviço | 217.217 | **194.918** | −22.299 (−10,3%) |
| Carretas | 9.585 | **8.670** | −915 (−9,5%) |
| Pares carreta-ano com OS | 46.234 | **41.765** | −4.469 (−9,7%) |
| Custo interno nominal | CAD 74,48 mi | **CAD 66,95 mi** | −7,53 mi (−10,1%) |

**Três consequências a assumir explicitamente:**

1. **H6b sai do modelo, mas sobrevive na EDA.** Dentro da população `MAINT`,
   `tipo_manutencao` é **constante** — variância nula, o mesmo motivo da remoção de
   `tailgate_flag`. Não se mede o efeito de um regime usado para definir a amostra.
   Com a implementação por flag, porém, `NET` e `MIX` continuam na base: **H6b é testada
   descritivamente** (η, custo médio por regime, boxplot) sobre a base completa, e
   apenas não entra como *feature* do modelo. **H6a (duração) permanece plenamente
   testável** e é a hipótese de contrato que entra na modelagem.
2. **Y muda de definição.** Passa a ser "custo interno anual **das carretas sob contrato
   com manutenção inclusa**". Todos os números da revisão de 2026-07-07 e da
   apresentação de 2026-08-05 deixam de ser comparáveis — a diferença de resultado
   passa a ter três causas sobrepostas (reextração + filtro + contrato).
3. **As 915 carretas e 4.469 carreta-anos descartados incluem os 7,5% de OS sem contrato
   identificado**, que não são necessariamente "sem contrato de manutenção" — podem ser
   lacunas de cadastro. Além disso, como 51,5% das carretas mudam de regime ao longo do
   período, o filtro remove **anos isolados** de carretas que permanecem na amostra em
   outros anos, criando descontinuidade nas séries defasadas que sustentam H3.

**Mitigação (embutida na implementação por flag):** rodar também o cenário sem filtro
como **baseline de comparação** (item 12a do plano). Isso permite (a) medir quanto o
recorte alterou Y e as métricas; (b) testar H6b no baseline, onde os quatro regimes
coexistem; (c) manter a ponte de comparabilidade com a apresentação já entregue. Sem
esse baseline, o efeito do filtro fica indistinguível do efeito da reextração.

---

## 5. Variáveis de contrato propostas no grão carreta × ano

A fonte é grão de OS; o modelo é grão carreta × ano. Regras de agregação propostas
para o notebook `02`:

| Variável (carreta × ano) | Derivação | Tipo | Cenário | Hipótese |
|---|---|---|---|---|
| `tipo_manutencao_ano` | modo (categoria predominante) das OS do ano; ausente → `SEM_CONTRATO` | categórica | ambos | H6b |
| `share_maint_ano` | fração das OS do ano com `tipo_manutencao='MAINT'` | quantitativa | ambos | H6b |
| `tempo_contrato_meses_fim_ano` | maior `tempo_contrato_meses_ate_reparo` observado no ano | quantitativa | explicativo | H6a |
| `tempo_contrato_meses_inicio_ano` | valor de fim do ano t−1 (defasado) | quantitativa | preditivo | H6a |
| `trocou_contrato_ano` | 1 se houve mais de um `tipo_manutencao` ou queda em `tempo_contrato` no ano (indício de novo contrato) | binária | ambos | H6 |
| `n_clientes_ano` | nº de `cod_cliente` distintos no ano | quantitativa | ambos | H6b |
| `cod_cliente_predominante_ano` | cliente com mais OS no ano — **uso descritivo**, ver D4 | categórica | descritivo | — |
| ~~`franquia_km_mensal_contrato`~~ | **removida** — D3 | — | — | — |

Notas metodológicas:

- **Defasagem.** `tempo_contrato_meses_fim_ano` é contemporâneo ao ano e, portanto,
  válido no cenário explicativo. Para o preditivo, usa-se a versão de início de ano —
  mesmo tratamento já aplicado a `km_acumulado_inicio_ano`.
- **Ausência.** `SEM_CONTRATO` é categoria informativa, não imputação: significa que a
  OS não caiu no intervalo de nenhum contrato. Deve ser preservada como nível, não
  descartada.
- **Colinearidade a vigiar.** `tempo_contrato_*` × `idade_carreta` ×
  `anos_ativo_ate_ano_anterior` medem coisas correlacionadas (maturidade). Se VIF > 10,
  manter uma por família nos modelos lineares; árvores toleram.

---

## 6. Hipóteses — versão atualizada

As cinco hipóteses vigentes permanecem. Duas voltam ao conjunto testável:

| | Hipótese | Estado |
|---|---|---|
| H1 | Idade ⇒ custo anual | a reavaliar na base nova (era ❌ não suportada) |
| H2 | Uso/quilometragem ⇒ custo | a reavaliar (era ✅ suportada) |
| H3 | Histórico ⇒ custo futuro | a reavaliar (era ✅ suportada) |
| H4 | Características do ativo ⇒ custo | a reavaliar (era ✅ suportada) |
| H5 | Região/operação ⇒ custo | a reavaliar (era ➖ parcial) |
| **H6** | **O tipo de manutenção contratual (`MAINT`/`NET`/`MIX`) influencia o custo anual absorvido pela empresa** | 🆕 **testável** |
| **H7** | **O tempo de contrato até o reparo influencia o custo anual** (relação contratual mais madura ⇒ perfil de custo distinto) | 🆕 **testável** |

Fica **fora de escopo** apenas o que continua ausente da fonte única: `tipo_contrato`
(RENTAL/LEASE), mão de obra detalhada, peças e leituras dedicadas de odômetro.

---

## 7. Plano de execução (quando autorizado)

Pré-requisito: `data/raw/cpi_canada_statcan_2020_2025.csv` **não está presente** em
`data/raw/` (só o `fato_wo_ml`), e o notebook `04` depende dele. A série é
reconstruível a partir de [`reports/tables/04_cpi_fatores.csv`](../reports/tables/04_cpi_fatores.csv),
que contém `ano_mes` e `indice_cpi` para todos os meses de 2020–2025. Restaurar o
arquivo antes de rodar o `04`.

| Etapa | Notebook | O que muda |
|---|---|---|
| 1 | `00_contexto_inventario_dados` | inventário para 29 colunas / 217.217 OS / 9.585 carretas; perfilar os 4 campos novos |
| 2 | `01_qualidade_integridade_dados` | ausência e cardinalidade dos campos de contrato; tratar as 5 OS de 2026; manter exclusão dos 172 estornos |
| 3 | `02_base_analitica_anual` | **maior mudança**: implementar as agregações de contrato da §5; registrar D3 (franquia removida) na curadoria; recontar as linhas carreta × ano |
| 4 | `04_deflacao_custos_cpi_canada` | sem mudança de lógica; recalcular sobre a base nova |
| 5 | `03b/03c/03d` | incluir contrato na descritiva, na relação X↔Y, no ranking e no VIF; η de `tipo_manutencao_ano` com ressalva de desbalanceamento |
| 6 | `05_modelagem_preditiva` | contrato entra na seleção; reavaliar VIF de `tempo_contrato_*`; rodar os dois cenários; comparar com o baseline sem contrato para isolar o ganho |
| 7 | `06_resultados_recomendacoes` | vereditos de H1–H6; recomendações de negócio por tipo de contrato |
| 8 | `08_build_apresentacao` | regenerar o deck (passa a ter slide de contrato; conferir se a tabela de hipóteses comporta H6a/H6b) |

**Medida de sucesso da rodada:** o ganho de R² do cenário preditivo com contrato
frente ao mesmo modelo sem contrato. Se o ganho for desprezível, esse é um resultado
legítimo e deve ser reportado como tal — H6 não suportada —, não motivo para
insistir nas variáveis.

---

## 8. Riscos

1. **Comparação contaminada.** Base regenerada + contrato mudam ao mesmo tempo. Sem um
   baseline da base nova *sem* contrato, não há como separar o efeito da reextração do
   efeito das variáveis novas. O baseline da etapa 6 é obrigatório, não opcional.
2. **`cod_cliente` como atalho.** Se entrar bruto, o modelo pode subir de R² memorizando
   clientes e piorar em produção. Ver D4.
3. **Desbalanceamento de `tipo_manutencao`.** Conclusões sobre `NET`/`MIX` apoiadas em
   ~2,7% das OS pedem cautela explícita no texto da entrega.
4. **Entrega desatualizada em circulação.** A apresentação atual traz números da base
   antiga. Está marcada como defasada em `docs/entregas/`, mas o arquivo continua
   utilizável — atenção antes de compartilhar.

---

**Autoria:** Grupo 01 — Marlon Wenzel, Jeison Lima, Rodrigo Queiroz, Giovani Cani.
**Data:** 2026-08-16 · **Natureza:** revisão de escopo e plano (sem reexecução de código).

---

## 9. Resultados da rodada (executada em 2026-08-16)

**Base analítica.** 47.715 carreta-anos · 9.585 carretas · custo interno CAD 74,62 mi
nominal / **79,65 mi real** (dez/2025). Y: média 1.669, mediana 812, assimetria 3,82,
3,1% de zeros. População `MAINT`: **41.739 carreta-anos (87,5%)**; `SEM_CONTRATO` 2.779;
`NET` 1.064; `MIX` 647; anos ativos sem OS 1.486.

**Decomposição do ganho** (melhor modelo por configuração, teste 2025):

| Cenário | A: todos, sem contrato | B: MAINT, sem contrato | C: MAINT + contrato | Efeito do filtro | **Efeito do contrato** |
|---|---|---|---|---|---|
| Preditivo | 0,4323 | 0,4516 | **0,4549** | +0,0193 | **+0,0033** |
| Explicativo | 0,5700 | 0,5878 | 0,5854 | +0,0178 | **−0,0024** |

**Modelo recomendado:** Gradient Boosting nos dois cenários — preditivo R² 0,4549 ·
RMSE 2.002,4 · MAE 1.092,7 CAD/ano; explicativo R² 0,5854.

**Vereditos.** H2, H3, H4 suportadas; H1 não suportada (ρ 0,032); H5 parcial;
**H6a parcial/fraca** (ρ 0,140; ganho de R² +0,0033) e **H6b parcial/fraca**
(η 0,183 sobre a base completa).

### Leitura crítica

1. **O contrato não acrescenta poder preditivo.** `tempo_contrato_meses_inicio_ano` ficou
   em último lugar na importância por permutação (0,0064, desvio 0,0028 — dentro do
   ruído). A hipótese foi **testada e não confirmada**, que era exatamente o desfecho
   previsto como legítimo em §7.
2. **O ganho do filtro `MAINT` não é melhora de previsão.** As 5.976 carreta-anos
   excluídas têm custo médio de CAD 689 contra 1.689 das `MAINT`, e muitas têm custo
   zero. Remover observações fáceis-de-prever-como-zero eleva o R² sem que o modelo
   preveja melhor. Apresentar o +0,019 como avanço seria enganoso.
3. **O papel real do contrato foi definir a população**, não explicar o custo. Essa é a
   contribuição honesta do dado novo.
4. **Refrigeração segue dominante** (importância 0,169), seguida de histórico defasado e
   exposição acumulada — o mesmo quadro da rodada anterior, agora sobre base reextraída.

---

## 10. Registro de execução (2026-08-16)

### Alterações de código

| Arquivo | Alteração |
|---|---|
| `notebooks/02_base_analitica_anual.ipynb` | parsing dos 4 campos; 6 agregações de contrato no grão anual; `tempo_contrato_meses_inicio_ano` (defasada); `trocou_contrato_ano`; **flag `populacao_maint_flag`**; dicionário e curadoria ampliados |
| `notebooks/03b_eda_variaveis.ipynb` | contrato incluído em `QUANT` e `QUALI` (descritivas, ranking, VIF, η) |
| `notebooks/05_modelagem_preditiva.ipynb` | **três configurações** (A/B/C) com decomposição do ganho; decisões de contrato na tabela de seleção; novas saídas `05_metricas_por_configuracao.csv` e `05_comparacao_configuracoes.csv` |
| `notebooks/06_resultados_recomendacoes.ipynb` | vereditos H1–H6a/H6b calculados dos dados; recomendações com contrato; **textos acentuados** |
| `notebooks/08_build_apresentacao.ipynb` | correção de 3 truncamentos silenciosos (`maxrows`) e dos textos que afirmavam contrato fora de escopo |
| `notebooks/09_atualiza_apresentacao_fase2.py` | **novo** — consolida a apresentação da Fase 2 sobre o PowerPoint apresentado |
| `data/raw/cpi_canada_statcan_2020_2025.csv` | **restaurado** a partir de `reports/tables/04_cpi_fatores.csv` (estava ausente e o notebook `04` depende dele) |

### Execução

Pipeline rodado na ordem `00` → `01` → `02` → `04` → `03b/03c/03d` → `05` → `06` → `08`,
mais o script `09`. Todas as tabelas de `reports/tables/` e figuras de `reports/figures/`
foram regeneradas sobre a base reextraída.

### Apresentação

O PowerPoint de origem do PDF (`Apresentacao_QuatroNorte_agosto.pptx`) foi disponibilizado
durante esta rodada. Achado que orientou a consolidação: **34 slides, 6 ocultos** — o PDF
exportou os 28 visíveis, e três dos ocultos (27, 28, 29) já eram *Comparação dos modelos*,
*Variáveis mais importantes* e *O que dizem os dados*, escondidos porque a Fase 2 ainda
não existia.

A entrega `Apresentacao_QuatroNorte_Fase2.pptx` é esse mesmo deck continuado: **46
slides — os 34 de agosto contíguos e na ordem original, seguidos de 12 slides da Fase 2**
na sequência das perguntas da disciplina (itens 12 a 16). Além dos slides novos: trechos
de texto atualizados, 7 tabelas reconstruídas e 3 slides de modelagem reexibidos. O
arquivo de origem **não é modificado** pelo script, e a contiguidade do bloco de agosto é
verificada a cada execução.

### Defeitos corrigidos no caminho

1. **Truncamento silencioso no gerador do deck** (`08`): `table()` aplica
   `df.head(maxrows)` sem aviso. Com as variáveis novas, três tabelas perderiam linhas
   em silêncio — hipóteses (2 linhas), dicionário (4) e métricas (7).
2. **Tabela de seleção partida** no `08`: a segunda metade começava em `.iloc[18:]`
   enquanto a primeira ia até 14, descartando 4 variáveis.
3. **CSV do CPI ausente**, quebrando o notebook `04`.
4. **Acentuação** nos CSVs do `06`, que destoava do deck acentuado.

### O que permanece em aberto

- Numeração de seções do deck: o `_agosto` já trazia "11 ·", "12 ·" e "13 · REFERENCIAL
  TEÓRICO" convivendo. Os slides novos usam 16 e 17 para não colidir; uma renumeração
  manual do conjunto resolveria.
- Slides 36 e 37 (*Desenho do estudo*, *Desenho de avaliação e anti-vazamento*) seguem
  ocultos, como no original. O de anti-vazamento sustenta bem o slide das três
  configurações, se o Grupo quiser reexibi-lo.

---

## 11. Experimento complementar — modelos por grupo de refrigeração

**Motivação.** `flag_refrigerado` é a variável mais importante do modelo (0,169 por
permutação) e separa os custos de forma marcante: média CAD 3.419/ano nas refrigeradas
contra 1.067 nas secas. A pergunta é se um modelo por grupo captura dinâmicas próprias
que o modelo único dilui — exatamente a lógica do *Mixed Effects Random Forest* de
Katreddi et al. (2023), já citado no referencial teórico.

**Desenho.** (A) modelo único treinado em toda a população MAINT; (B) dois modelos
independentes, refrigeradas e secas, com as previsões reunidas. Ambos avaliados nas
**mesmas 7.789 linhas** de teste (2025), com o mesmo *cap* de outliers e a mesma
transformação do alvo — a única diferença é a estratificação. Nos modelos por grupo,
`flag_refrigerado` sai das features (constante dentro do grupo). O baseline reproduz
exatamente o notebook `05` (GB 0,4549 · RF 0,4486), o que confirma a comparabilidade.

Script: `notebooks/10_experimento_grupos_refrigeracao.py`.

### Resultado

| Cenário | Modelo | Único | Por grupo | Δ R² | IC 95% | P(ganho) |
|---|---|---|---|---|---|---|
| **Preditivo** | **Random Forest** | 0,4486 | **0,4652** | **+0,0165** | [+0,0098; +0,0242] | **100%** |
| **Preditivo** | **Gradient Boosting** | 0,4549 | **0,4673** | **+0,0124** | [+0,0040; +0,0209] | **99,6%** |
| Explicativo | Gradient Boosting | 0,5854 | 0,5918 | +0,0064 | [−0,0021; +0,0146] | 93,3% |
| Explicativo | Random Forest | 0,5734 | 0,5709 | −0,0024 | [−0,0090; +0,0036] | 20,8% |

Intervalos por *bootstrap* de 2.000 reamostragens das linhas de teste.

**Medido só em 2025, o ganho parecia real**: os intervalos de 95% excluíam o zero nos
dois modelos e o MAE caía 11 a 15 CAD/ano. No explicativo não havia efeito.

> ⚠️ **Esta leitura foi superada.** O *bootstrap* mede apenas o ruído amostral **dentro
> do ano de teste**. A validação com três anos (§12) mostra que a variação **entre anos**
> é maior que o ganho — e desfaz a conclusão. Ver §12 antes de citar estes números.

### Onde o ganho aparece

| Cenário | Modelo | Refrigeradas (Δ R²) | Secas (Δ R²) |
|---|---|---|---|
| Preditivo | Random Forest | **+0,0259** | +0,0074 |
| Preditivo | Gradient Boosting | **+0,0211** | −0,0010 |
| Explicativo | Gradient Boosting | +0,0165 | −0,0214 |

O ganho se concentra nas **refrigeradas** (2.431 carreta-anos no teste, custo médio
CAD 4.154/ano). Nas secas o efeito é nulo ou levemente negativo. Faz sentido: é o grupo
caro e heterogêneo, cuja dinâmica o modelo único dilui ao ajustar majoritariamente às
23.310 observações de carretas secas no treino.

### Leitura

1. Em 2025 o resultado era o melhor do projeto (R² 0,4673 contra 0,4549) — **mas não se
   repetiu nos outros anos**.
2. O ganho aparente era ~4× o das variáveis de contrato. **A validação em três anos
   mostrou que essa comparação não se sustenta** (§12).
3. Mesmo no melhor caso o efeito seria pequeno em termos de negócio: 15 CAD/ano de MAE
   sobre ~1.090 é ~1,4% do erro.
4. **Custo operacional**: dobraria o número de modelos a treinar, versionar e monitorar.

### Limitação

O *bootstrap* mede apenas o ruído amostral **dentro do único ano de teste (2025)**. A
validação com janelas móveis foi executada em seguida e está em **§12** — ela reverte a
conclusão desta seção.

---

## 12. Validação com janelas móveis — o ganho não se sustenta

O experimento da §11 apoiava-se em um único ano de teste. Repetimos o mesmo confronto
com **três anos** (2023, 2024 e 2025), cada um treinado apenas com os anos anteriores.

Script: `notebooks/11_validacao_janelas_moveis.py`.

| Ano de teste | Treino | GB único | GB dividido | Δ | RF único | RF dividido | Δ |
|---|---|---|---|---|---|---|---|
| 2023 | 2020–2022 | 0,4941 | 0,4748 | **−0,0193** | 0,4745 | 0,4780 | +0,0035 |
| 2024 | 2020–2023 | 0,4821 | 0,4968 | +0,0147 | 0,4779 | 0,4808 | +0,0029 |
| 2025 | 2020–2024 | 0,4549 | 0,4673 | +0,0124 | 0,4486 | 0,4652 | +0,0165 |
| **Média** | | | | **+0,0026** | | | **+0,0076** |

**No Gradient Boosting o ganho inverte de sinal em 2023.** No Random Forest é consistente
nos três anos, mas cai para ~+0,003 em dois deles.

### Decisão

**Mantém-se o modelo único** — Gradient Boosting, R² 0,4549 · RMSE 2.002 · MAE 1.093
CAD/ano. Dividir por refrigeração não entrega ganho confiável e dobraria o número de
modelos a manter. As variáveis de contrato permanecem no modelo: o efeito é pequeno, mas
documentam o teste de H6 e não custam nada.

### A lição metodológica

O *bootstrap* da §11 dava **99,6% de probabilidade de ganho** — e estava certo sobre o que
media: o ruído **dentro** de 2025. A variação **entre anos** é de outra ordem, e é ela que
importa para decidir qual modelo manter. É o resultado mais transferível desta rodada:
**intervalo de confiança dentro de um ano não é evidência de estabilidade no tempo.**

Efeito colateral útil: o R² do modelo único varia de 0,4941 (2023) a 0,4549 (2025). O
número de 2025 não é uma constante do modelo — é o resultado daquele ano, e o mais
conservador dos três.

---

## 13. Revisão de conteúdo da apresentação

Uma revisão da apresentação apontou dezesseis imprecisões, todas corrigidas no script
`09_atualiza_apresentacao_fase2.py` (e, portanto, reproduzíveis).

**Contradições e dados superados:** afirmação de que agrupar por refrigeração "melhora a
previsão" (contradizia §12); slide oculto de metodologia com "sem filtro MAINT" e "25
candidatas"; custos descritos em **R$** em vez de CAD, misturando o corte do eixo do
gráfico (~12.000) com o máximo real (62.231); KNN ausente da lista de técnicas;
duplicidade de numeração no referencial; Gates sem status coerente; "eliminou a
zero-inflação" (restam 3,13%).

**Imprecisões conceituais:**

| Tema | Correção |
|---|---|
| População | separa **escopo do custo** (todo o interno) de **população de modelagem** (MAINT: 41.739 de 47.715) |
| Janela temporal | 6 anos de dados, **5 modeláveis** — 2020 não tem ano anterior para as defasadas |
| Importância por permutação | **embaralhar** ≠ **remover**: mede a dependência do modelo ajustado, não o efeito de retreinar sem a variável |
| MAE | é erro **médio**, não limite; equivale a **~51%** do custo médio do ano de teste |
| Idade | a mediação por histórico/uso **não foi testada** — é hipótese, não resultado |
| Aplicação | serve para **priorizar** e **provisionar no agregado**, não para estimar o valor de um ativo isolado; deployment é etapa futura |
| Gates | Gate 4 concluído; **Gate 5 parcial** (validação feita, robustez pendente) |
| Literatura | o R² de 97% de Katreddi **não é comparável**; Sun é "consistente com", não "confirma" |

### Dois defeitos de código encontrados na revisão

1. **Substituição por *run*.** O PowerPoint divide um parágrafo em vários *runs*; comparar
   *run* a *run* fazia substituições falharem **em silêncio**. Passou a operar no
   parágrafo inteiro.
2. **Slide de Gates localizado por posição.** Com o bloco da Fase 2 anexado ao final, o
   código que editava "o último slide" passou a editar o de conclusões — e as correções
   dos Gates não rodaram, sem erro. Passou a localizar o slide **pelo conteúdo**.

Ambos são da mesma família do truncamento silencioso do notebook `08`: código que erra
sem reclamar. Onde possível, as buscas passaram a ser por conteúdo e com asserção.

