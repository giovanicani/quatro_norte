# Plano da Fase 2 — o que falta fazer, pergunta por pergunta

> ✅ **CONCLUÍDO EM 2026-08-16.** Pipeline rodado ponta a ponta (`00`→`06`, `08`),
> experimentos `10` e `11`, e apresentação consolidada sobre o PowerPoint apresentado
> (`Apresentacao_QuatroNorte_Fase2.pptx`, 46 slides: os 34 de agosto intactos + 12 da
> Fase 2, na ordem das perguntas da disciplina).
>
> **Itens 12 a 16 da rubrica: entregues.** Resultados em duas tentativas e um final;
> implicações gerenciais; limitações; projetos futuros; conclusões.
>
> Dois resultados negativos, ambos obtidos por teste: contrato com efeito fraco
> (+0,0033 de R²) e divisão por refrigeração descartada por não se sustentar entre anos.
> Detalhamento na revisão 2026-08-16, §9 a §13.

> **Ponto de partida:** [`docs/entregas/Apresentacao_QuatroNorte.pdf`](entregas/Apresentacao_QuatroNorte.pdf)
> — 28 páginas, apresentado em **2026-08-05**. Ele cobre os **itens 1 a 11** da rubrica
> e declara explicitamente o que ficou para depois: modelagem e avaliação estão marcadas
> com `*Fase 2` no fluxograma (p. 6), e o slide de Gates (p. 28) mostra o **Gate 4 em
> aberto**.
>
> **Este plano é a Fase 2.** Ele não refaz a apresentação: continua de onde ela parou.
>
> **Destravador:** os dados de contrato chegaram à base única em **2026-08-16**, o que
> torna **H6** — já declarada na p. 5 — finalmente testável.

---

## Quadro geral

| Pergunta | O que é | Estado |
|---|---|---|
| 1–5 | Contexto, problema, objetivos, hipóteses, artigos | ✅ apresentado |
| 6–7 | Base de dados e feature engineering | 🟡 apresentado, **precisa atualização** (29 colunas, contrato) |
| 8–9 | EDA e técnicas | 🟡 apresentado, **precisa reexecução** |
| 10–11 | Referencial e metodologia | ✅ apresentado |
| **12a** | **Resultados preliminares — 1ª tentativa** | 🔴 **a produzir** |
| **12b** | **Resultados preliminares — 2ª tentativa** | 🔴 **a produzir** |
| **12c** | **Resultados finais** | 🔴 **a produzir** |
| **13** | **Implicações gerenciais** | 🔴 **a produzir** |
| **14** | **Limitações** | 🟡 existe na p. 27, **a reescrever** |
| **15** | **Recomendações para projetos futuros** | 🔴 **a produzir** |
| **16** | **Conclusões** | 🔴 **a produzir** |

---

## Bloco A — atualizar o que já foi apresentado (itens 6, 7, 8, 9, 14)

Nada aqui é refação: é **atualização de números e inclusão do contrato**.

### Item 6 — Base de dados

| O quê | Onde muda |
|---|---|
| 25 → **29 colunas** | p. 6 e p. 9 do deck |
| 223.590 → **217.217 OS**; 9.859 → **9.585 carretas** | p. 2, p. 6, p. 26 |
| Trocar "fonte **inicial**" por fonte única consolidada — o adjetivo já não se aplica | p. 2, p. 6, p. 9, p. 27 |
| Acrescentar os 4 campos de contrato ao dicionário | p. 9, p. 10 |
| ⚠️ Corrigir divergência: a p. 26 diz **47.666** linhas carreta × ano; `reports/` registra **49.248** | p. 26 |

Fonte automática: `reports/tables/00_perfil_colunas.csv` passa a listar 29 linhas
sozinho após rodar o notebook `00`.

### Item 7 — Feature engineering

Acrescentar o bloco de contrato às variáveis derivadas: `tipo_manutencao_ano`,
`share_maint_ano`, `tempo_contrato_meses_fim_ano` / `_inicio_ano`,
`trocou_contrato_ano`, `n_clientes_ano`. Regras de agregação em
[`dicionario_variaveis_candidatas.md`](dicionario_variaveis_candidatas.md) §4.

Registrar as duas exclusões: **`franquia_km_mensal_contrato` removida** (99,8% zeros) e
**`cod_cliente` fora do modelo** como categórica bruta (597 categorias).

### Itens 8 e 9 — EDA e técnicas

A EDA precisa ser **reexecutada** (base nova) e **ampliada** (contrato):

- descritivas e histogramas dos campos de contrato;
- boxplot de `custo_ano_real` por `tipo_manutencao_ano` — o gráfico que responde H6b
  visualmente;
- η de `tipo_manutencao_ano` **com ressalva de desbalanceamento** (MAINT 89,7%): reportar
  também custo médio por nível com intervalo de confiança, porque η baixo aqui pode ser
  artefato de desbalanceamento, não ausência de efeito;
- Spearman de `tempo_contrato_meses_fim_ano` com Y — responde H6a;
- VIF incluindo `tempo_contrato_*`, que compete com `idade_carreta` e
  `anos_ativo_ate_ano_anterior` (todas medem maturidade).

Técnicas (item 9) não mudam. Nota: a p. 25 lista 6 modelos e omite **KNN**, que consta
do pipeline — alinhar.

### Item 14 — Limitações

Três linhas da p. 27 **invertem de sentido** e precisam ser reescritas:

| Hoje diz | Passa a dizer |
|---|---|
| "Fonte inicial: **sem dados de contrato**..." | contrato **incluído**; seguem fora mão de obra, peças e `tipo_contrato` (RENTAL/LEASE) |
| "Sem filtro por tipo de manutenção" | conforme decisão D6 — e agora é **escolha metodológica**, não imposição dos dados |
| — | **novas:** franquia degenerada (99,8% zeros); `NET`/`MIX` com 2,7% das OS limitam conclusões sobre esses regimes; `cod_cliente` não modelado por risco de memorização |

---

## Bloco B — produzir o que não existe (itens 12, 13, 15, 16)

### Item 12 — Resultados, em três rodadas

A rubrica pede 1ª tentativa, 2ª tentativa e finais. As três correm **dentro do grão
anual** — o grão mensal está encerrado e não conta como tentativa.

**12a — 1ª tentativa: baseline (população completa, sem contrato)**

Pipeline na base reextraída, **sem** a flag `MAINT` e **sem** as variáveis de contrato.

- *Por que primeiro:* isola o efeito da **reextração**. Sem isso, a variação de R² nas
  rodadas seguintes fica ambígua entre três causas (base nova, filtro `MAINT`, contrato).
- *Comparação:* contra R² 0,429 preditivo / 0,572 explicativo da base anterior.
- *Bônus:* é a única rodada em que `NET` e `MIX` existem — **onde H6b é testável**.
- *Entregável:* `reports/tables/05_metricas_modelos_baseline.csv`.

**12b — 2ª tentativa: população `MAINT` (D6) + contrato**

Aplicar a flag `populacao_maint_flag` e incluir as variáveis de contrato — principalmente
`tempo_contrato_meses_*`, que responde **H6a**. `tipo_manutencao_ano` **não entra** como
*feature*: é constante dentro da população filtrada.

- *Pergunta:* a duração de contrato acrescenta poder explicativo ao que já se sabe
  (refrigeração + histórico + uso)?
- *Métricas de decisão:* **Δ R² sobre 12a**, decomposto entre efeito do filtro e efeito
  do contrato (rodar `MAINT` sem contrato como passo intermediário — uma linha de código
  a mais, já que a flag não deleta nada).
- *Entregáveis:* métricas, importância por permutação, tabela comparativa das três
  configurações.

**12c — Resultados finais**

Modelo escolhido, com justificativa, e os vereditos de **H1 a H6**.

- Se Δ R² de `tempo_contrato_*` for desprezível: **H6a não suportada** é resultado
  legítimo e deve ser reportado como tal. Não insistir na variável.
- **H6b é respondida pela EDA do baseline**, não pelo modelo — deixar isso explícito na
  redação, para não parecer omissão.
- Cuidado de interpretação: diferenças de custo entre regimes contratuais podem refletir
  **quem paga o reparo**, não quanto ele custa. É a leitura mais delicada da Fase 2.
- Fechar o **Gate 4** do slide de entregas.

### Item 13 — Implicações gerenciais

Traduzir os fatores em decisão. Ancorar em três eixos, todos já sinalizados pela EDA
anterior e a confirmar na nova:

1. **Orçamento por perfil de ativo** — refrigeradas custam mais e com muito mais
   dispersão: provisionar por classe, não pela média da frota.
2. **Priorização por histórico** — carretas com histórico alto no ano anterior são as
   candidatas naturais a inspeção preventiva. É o preditor mais forte sem vazamento.
3. **Contrato** *(novo, condicionado ao resultado)* — se H6 for suportada, há implicação
   direta em precificação de renovação e em desenho de contrato por regime.

Saída: `reports/tables/06_recomendacoes_negocio.csv`, hoje já existente e a atualizar.

### Item 15 — Recomendações para projetos futuros

**Contrato sai desta lista** — deixou de ser trabalho futuro e virou resultado. Restam:

- integrar mão de obra e peças (decompor custo por origem);
- `tipo_contrato` (RENTAL/LEASE), único campo de contrato ainda ausente;
- efeitos mistos por grupo de ativo (MERF), sugerido pelo referencial (Katreddi 2023);
- telemetria/GPS e quilometragem planejada como exposição;
- modelar a **cauda**: assimetria 3,79 é o limite estrutural do R² atual.

### Item 16 — Conclusões

Só se escreve depois de 12c. Deve responder à pergunta da p. 3 em uma frase, declarar o
veredito de cada hipótese e dizer o que o modelo serve para decidir — com o erro médio
(MAE em CAD/ano) explícito, que é o que dá ou tira credibilidade de uso orçamentário.

---

## Ordem de execução

| # | Ação | Depende de |
|---|---|---|
| 0 | Restaurar `data/raw/cpi_canada_statcan_2020_2025.csv` (reconstruível de `reports/tables/04_cpi_fatores.csv`) | — |
| 0 | ~~Recuperar o `.pptx` de origem~~ — ✅ resolvido: `Apresentacao_QuatroNorte_agosto.pptx` | — |
| 1 | Notebooks `00` → `01` (inventário e qualidade, 29 colunas) | — |
| 2 | Notebook `02`: agregações de contrato **+ flag `populacao_maint_flag`** — **maior mudança de código** | 1 |
| 3 | Notebook `04` (deflação) | 2 + CPI |
| 4 | Notebooks `03b/03c/03d` (EDA + contrato, **sobre a base completa**) → **itens 8, 14, H6b** | 3 |
| 5 | Notebook `05` sem flag, sem contrato → **item 12a (baseline)** | 3 |
| 6 | Notebook `05` com flag `MAINT`, sem contrato → decompõe o efeito do filtro | 5 |
| 7 | Notebook `05` com flag `MAINT` + contrato → **item 12b** | 6 |
| 8 | Notebook `06` (vereditos H1–H6, recomendações) → **itens 12c, 13** | 7 |
| 9 | Redação dos itens **15 e 16** | 8 |
| 10 | Atualização da apresentação | 4–9 |

> D6 está **firmada**: população `MAINT`, implementada como flag. Não há mais decisão
> bloqueando o início.

---

## Como isso entra na apresentação

✅ **Resolvido.** O PowerPoint de origem (`Apresentacao_QuatroNorte_agosto.pptx`) foi
disponibilizado e o script `notebooks/09_atualiza_apresentacao_fase2.py` consolida a
Fase 2 diretamente sobre ele — sem modificá-lo.

Achado decisivo: o arquivo tinha **34 slides, 6 ocultos**, e o PDF exportou os 28
visíveis. Três dos ocultos (27, 28, 29) já eram os slides de modelagem — construídos e
escondidos porque a Fase 2 não existia. Foram atualizados e reexibidos.

O notebook `08_build_apresentacao.ipynb` produz uma peça **paralela**, de 23 slides e
estrutura diferente. Continua útil apenas como gerador reprodutível de tabelas e
figuras, não como apresentação.

Três limites de truncamento silencioso nesse notebook, se for usado para gerar as
tabelas ( `table()` faz `df.head(maxrows)` sem avisar):

| Slide | Chamada | Hoje | Depois | Efeito |
|---|---|---|---|---|
| 5 | `maxrows=7` | 6 linhas | 8 com H6a/H6b | 2 hipóteses somem |
| 10 | `maxrows=14` (2ª tabela) | 26 linhas | ~32 | 4 variáveis de contrato somem |
| 19 | `maxrows=14` | 14 (cheio) | 21 com baseline | 7 modelos somem |

---

**Data:** 2026-08-16 · Grupo 01 — Marlon Wenzel, Jeison Lima, Rodrigo Queiroz, Giovani Cani
**Referências:** [`revisao_contrato_2026-08-16.md`](revisao_contrato_2026-08-16.md) ·
[`narrativa_do_projeto.md`](narrativa_do_projeto.md) ·
[`dicionario_variaveis_candidatas.md`](dicionario_variaveis_candidatas.md)
