# Guia do projeto — Previsão de Custos de Manutenção de Carretas

> **Comece por aqui.** Este é o ponto de entrada para entender o que foi feito.
> Ele resume o projeto, diz **o que ler e em que ordem**, marca o que é
> **vigente** vs. **histórico/desatualizado**, e explica como reproduzir os
> resultados. Os documentos detalhados continuam onde estão — aqui a gente só
> costura tudo.
>
> Projeto aplicado do MBA (FGV) para a **Quatro Norte Consulting** · Grupo 01 ·
> Marlon Wenzel, Jeison Lima, Rodrigo Queiroz, Giovani Cani ·
> última consolidação: **2026-07-07 (revisão para custo ANUAL por carreta)**.
>
> 📌 **Leia primeiro** [`docs/revisao_anual_2026-07-07.md`](revisao_anual_2026-07-07.md):
> documento autoritativo da revisão que migrou o projeto de *custo por km (mensal)*
> para **custo anual por carreta** a partir de uma **fonte única** de dados.

---

## 1. O projeto em 60 segundos

- **Cliente / operação:** empresa de leasing/rental de carretas no **Canadá**
  (secas e refrigeradas de até 53′, ON/QC e outras províncias). A manutenção é
  **própria** (oficinas registram ordens de serviço com mão de obra e peças).
- **Pergunta:** *quais fatores mais influenciam o **custo anual de manutenção** das
  carretas — e como estimá-lo a partir de suas características operacionais,
  históricas e estruturais?*
- **Custo interno** = a parte absorvida pela empresa (`charge_flag = 'I'`), **não**
  faturada ao cliente. Inclui **preventiva E corretiva** — "interno" ≠ "preventivo".
- **Fonte única:** `data/raw/fato_wo_ml_2020-01-01_to_2025-12-31.csv`; construção da
  base/joins/feature engineering = etapa anterior de preparação.
- **Variável-alvo (Y):** `custo_ano_real` — custo **anual** de manutenção por carreta,
  no grão **carreta × ano**, em **CAD** deflacionado pelo **CPI do Canadá** (dez/2025).
- **Resposta curta:** o **custo anual real por carreta** subiu +52% (2020→2025, já sem
  inflação). Os maiores determinantes são **refrigeração**, **histórico de manutenção**
  (OS/custo de anos anteriores) e **uso/quilometragem**; idade isolada pesa pouco. O
  grão anual **quase elimina a zero-inflação** (~3,2%).
- **Modelo recomendado:** **Random Forest** (cenário preditivo, sem vazamento) —
  R² = 0,43 · RMSE = 2.026 · MAE = 1.064 CAD/ano (teste temporal 2025). No cenário
  explicativo, **Gradient Boosting** atinge R² = 0,57.

---

## 2. Mapa de documentos — o que ler e o status de cada um

Leia nesta ordem. A coluna **Status** é o mais importante: vários arquivos
descrevem uma versão **antiga** do projeto e não devem ser usados como verdade.

| # | Documento | Para quê serve | Status |
|---|---|---|---|
| 1 | **`docs/GUIA_DO_PROJETO.md`** (este) | Ponto de entrada e mapa geral | ✅ Vigente |
| 1b | **`docs/revisao_anual_2026-07-07.md`** | Revisão para custo ANUAL por carreta (fonte única) — decisões e resultados | ✅ **Autoritativo** |
| 2 | `reports/sumario_executivo.md` | Resposta ao problema, resultados e recomendações (1 página) | ✅ Vigente |
| 3 | `docs/curadoria_2026-07-07.md` | Curadoria estrutural: o que foi organizado, validado e o que falta ajustar | ✅ Vigente |
| 4 | `docs/revisao_pos_base_nova_2026-07-07.md` | Revisão da fase **mensal/por km** (superada pela revisão anual) | 🕓 Histórico (mensal) |
| 5 | `docs/registro_alteracoes_2026-07-06.md` | Log histórico da revisão alvo interno/CPI (fase mensal) | 🕓 Histórico metodológico |
| 6 | `README.md` | Especificação completa (contexto, dados, hipóteses, técnicas) | ✅ Vigente |
| 7 | `docs/dicionario_de_dados.md` | Schema, tipos e origem de cada campo das 7 bases | ✅ Vigente |
| 8 | `docs/dicionario_variaveis_candidatas.md` | Especificação metodológica das 46 X candidatas: grão, fórmula, defasagem, vazamento e hipótese | ✅ Vigente |
| 9 | `docs/historico/Plano_Analises.md` | Plano de análises original, mantido para rastreio metodológico | 🕓 Histórico |
| 10 | `docs/historico/revisao_feedback.md` | Feedback de revisão anterior | 🕓 Histórico |
| 11 | `AGENTS.md` | Guia de estilo/escopo p/ assistentes de IA | ✅ Vigente |
| 12 | `notebooks/` (00 → 08, ordem em `notebooks/README.md`) | Pipeline reprodutível célula a célula — **fonte única do projeto** | ✅ Ponto de entrada operacional |
| 13 | `notebooks/07_painel_resultados.ipynb` | Painel visual que lê as saídas de `reports/` sem reexecutar tudo | ✅ Recomendado para inspeção rápida |
| 14 | `docs/historico/PrevCustManut_jeison.html` | Relatório visual (site) preliminar | ❌ **Obsoleto**: usa **R$/IPCA** (Brasil), grão **por OS** e R² antigo (0,192) |

**Regra de ouro:** em caso de conflito, vale **`docs/revisao_anual_2026-07-07.md` +
notebooks vigentes + tabelas `reports/` + sumário executivo**.

---

## 3. Decisões canônicas vigentes (e o que mudou)

Estas quatro decisões definem a análise atual. Detalhe completo no
`registro_alteracoes_2026-07-06.md`.

| Decisão | Vigente | Era antes | Por quê mudou |
|---|---|---|---|
| **Variável-alvo** | `custo_ano_real` — custo **anual** por carreta (CAD/ano, real) | custo interno **por km** (mensal) | Nova unidade de análise: custo anual por ativo, mais próximo do orçamento e sem a razão custo/km |
| **Grão** | **carreta × ano** | carreta × mês | Reduz a zero-inflação (67% → ~3%) e revela associações mais fortes |
| **Fonte de dados** | **única**: `fato_wo_ml` (CSV consolidado) | 7 tabelas do modelo estrela | Single Source of Truth; joins/FE = etapa anterior |
| **Deflator** | **CPI Canadá** (StatCan, vetor v41690973, base dez/2025) | **IPCA/BCB** (Brasil), depois CPI | Custos em CAD; deflator canadense |
| **População** | todo o custo interno (sem filtro MAINT) | `tipo_manutencao = MAINT` | Dados de contrato ausentes na fonte única |
| **Anti-vazamento** | histórico **defasado** (ano anterior) + split **temporal** (teste = 2025) | havia vazamento | Cenário preditivo usa apenas informação conhecida no início do ano |

> ⚠️ **Decisão de organização:** os **notebooks em `notebooks/` são a fonte
> única e reprodutível** e partem **exclusivamente** do CSV consolidado `fato_wo_ml`.
> Execute na ordem de `notebooks/README.md` (00 → 01 → 02 → 04 → 03b/03c/03d → 05 →
> 06 → 08). Para inspeção rápida, use `07_painel_resultados.ipynb`. A versão mensal/por
> km está em `notebooks/historico/`. **Os números válidos são os do custo anual real
> por carreta** (§6).

---

## 4. Dados

- **Fonte única do estudo:** `data/raw/fato_wo_ml_2020-01-01_to_2025-12-31.csv`
  (223.590 OS · 9.859 carretas; janela 2020-2025). É o **único** insumo da análise. A
  série pública de CPI (`cpi_canada_statcan_2020_2025.csv`) é o único dado externo.
- **Etapa anterior (contexto, não reexecutada):** a extração SQL
  (`data/extract_custo_interno_km.sql`), o **modelo estrela** e o *feature engineering*
  produziram o CSV consolidado. O modelo estrela — 1 dimensão + 6 fatos (ligados por
  `id_carreta`; OS/mão de obra/peças por `id_os`) — é apenas **contexto da construção
  da base**, não fonte ativa de análise:

  | Tabela | 1 linha = | Papel |
  |---|---|---|
  | `dim_carretas` | uma carreta | atributos do ativo (montadora, ano, eixos, reefer, classe) |
  | `fato_readings` | uma leitura de odômetro | km acumulado por data |
  | `fato_wo` / `fato_wo_ml` | uma ordem de serviço | cabeçalho + totais internos; `_ml` = enriquecida p/ modelagem |
  | `fato_wo_labour` | uma linha de mão de obra | custo interno + sistema VMRS |
  | `fato_wo_parts` | uma linha de peça | custo interno + flag de garantia |
  | `fato_contratos` | uma carreta-contrato | tipo, franquia de km, vigência |
  | `fato_gps` | uma posição/dia | telemetria lat/long (cobertura parcial) |

- **Dicionário completo:** `docs/dicionario_de_dados.md`.
- **VMRS** ("CID da oficina"): código padronizado do sistema reparado (PM,
  04 Freios, 09 Pneus, 10 Reefer…). Usado como **dimensão de análise**, não como
  filtro do alvo. Tabela de códigos no README §9.3.
- **Bases processadas** (`data/processed/`): `base_anual_carreta.csv` e
  `base_anual_carreta_deflacionada.csv` (**49.248 linhas carreta × ano**, custos em CAD
  reais dez/2025). Y = `custo_ano_real` (custo anual de manutenção por carreta).

---

## 5. Pipeline reprodutível

O código vigente vive inteiramente em **`notebooks/`**. A lógica que antes
estava em scripts `.py` em `src/` foi convertida célula a célula em notebooks,
para que o pipeline seja executado e auditado passo a passo. **Não há mais
scripts `.py`.** Cada notebook corresponde a uma etapa; as saídas caem em
`reports/` (tabelas `.csv` e figuras `.png`) e em `data/processed/`.

Ordem e função documentadas em [`notebooks/README.md`](../notebooks/README.md).
Para apenas consultar resultados já gerados, use
`notebooks/07_painel_resultados.ipynb`.

| Ordem | Notebook | Faz |
|---|---|---|
| 1 | `notebooks/00_contexto_inventario_dados.ipynb` | inventário da base consolidada única |
| 2 | `notebooks/01_qualidade_integridade_dados.ipynb` | qualidade/integridade da base consolidada |
| 3 | `notebooks/02_base_analitica_anual.ipynb` | monta a base carreta × ano (49.248 linhas) |
| 4 | `notebooks/04_deflacao_custos_cpi_canada.ipynb` | deflaciona custos (CAD) pelo CPI Canadá → `custo_ano_real` (Y) |
| 5 | `notebooks/03b_eda_variaveis.ipynb` | EDA variável-a-variável, relação X↔Y, ranking, VIF |
| 6 | `notebooks/03c_estatisticas_resumo.ipynb` | estatísticas-resumo do Y anual |
| 7 | `notebooks/03d_diagnostico_outliers.ipynb` | diagnóstico de outliers por variável |
| 8 | `notebooks/05_modelagem_preditiva.ipynb` | seleção de variáveis + modelagem (2 cenários, split temporal, importâncias) |
| 9 | `notebooks/06_resultados_recomendacoes.ipynb` | tabelas de resultado (`reports/tables/06_*`) |
| 10 | `notebooks/08_build_apresentacao.ipynb` | gera `docs/entregas/Apresentacao_QuatroNorte.pptx` a partir de `reports/` (requer `python-pptx`) |

> É preciso ter em `data/raw/` a base única `fato_wo_ml` e a série de CPI
> (`cpi_canada_statcan_2020_2025.csv`). A EDA (03b/03c/03d) roda **depois** da
> deflação (04), pois usa o alvo real `custo_ano_real`.

> A versão mensal/por km (alvo preventivo/CAD-km) está em `notebooks/historico/`; o
> histórico completo permanece no controle de versão (git).

---

## 6. Resultados (números vigentes)

Fonte canônica: `reports/tables/` + `reports/sumario_executivo.md`.

### EDA
- **Distribuição do Y (custo anual real por carreta):** média **CAD 1.673,72/ano**,
  mediana **812,55**, assimetria **3,76**, **apenas 3,2%** de carreta-anos com custo
  zero — o grão anual praticamente elimina a zero-inflação.
- **Evolução real:** custo médio por carreta subiu de **CAD 1.334 (2020) para 2.026
  (2025), +52%** em termos reais (já sem inflação; CPI +20,6% no período).
- **Associação com Y (Spearman | eta), explicativas:** `n_os_ano_anterior` 0,540 ·
  `custo_ano_anterior` 0,536 · `km_rodado_ano` 0,530 · histórico acumulado ~0,45 ·
  `km_acumulado_fim_ano` 0,428 · `idade_carreta` 0,018 (fraca). Categóricas:
  `unit_subtype` eta 0,55 · `flag_refrigerado` **0,43** · `cod_montadora` 0,24.
- **Colinearidade:** VIF > 10 em `idade_carreta` (13,5), `n_os_acum` (12,9) e
  `ano_modelo` (12,2) — colinearidades esperadas (idade↔ano; acumulados). Árvores são
  robustas; em modelos lineares mantém-se uma de cada família.

### Modelagem (teste temporal 2025, sem filtro MAINT)

| Cenário | Modelo | R² | RMSE | MAE |
|---|---|---|---|---|
| Explicativo | **Gradient Boosting** | **0,572** | 1.753 | 895 |
| Explicativo | Random Forest | 0,571 | 1.755 | 888 |
| **Preditivo** | **Random Forest** ◀ recomendado | **0,429** | **2.026** | **1.064** |
| Preditivo | KNN / Árvore | 0,42 | ~2.040 | ~1.090 |
| Preditivo | Lineares (múltipla, ridge) | < 0 | — | — |

- O grão anual multiplica o poder explicativo frente ao modelo mensal (R² 0,085).
  Árvores/ensembles superam claramente os lineares (caudas extremas).
- **Permutation importance (preditivo):** `flag_refrigerado` **0,22** (dominante) ·
  `n_os_ano_anterior` 0,12 · `km_acumulado_inicio_ano` 0,072 · `custo_ano_anterior`
  0,066 · histórico acumulado ~0,06 · `idade_carreta` 0,032.

### Hipóteses × evidências (adaptadas à unidade anual e à fonte única)
| | Hipótese | Veredito |
|---|---|---|
| H1 | Idade ⇒ custo anual | ❌ Não suportada (efeito direto fraco, ρ ≈ 0,02) |
| H2 | Uso/quilometragem ⇒ custo | ✅ Suportada (km_rodado ρ 0,53) |
| H3 | Histórico ⇒ custo futuro | ✅ Suportada (custo/OS do ano anterior ρ ~0,54) |
| H4 | Características do ativo ⇒ custo | ✅ Suportada (reefer/subtipo/montadora) |
| H5 | Região/operação ⇒ custo | ➖ Parcial (efeito fraco) |
| — | Contrato ⇒ custo | ⛔ Fora de escopo (dados ausentes na fonte única) |

---

## 7. Entregáveis — o que é o quê

| Arquivo | O que é | Status |
|---|---|---|
| `docs/entregas/Apresentacao_QuatroNorte.pptx` | Deck (23 slides) gerado por `08_build_apresentacao.ipynb` a partir de `reports/` | ✅ **Vigente e reprodutível** (custo anual/CAD/ano) |
| `docs/entregas/Apresentacao_QuatroNorte_v2.html` | Relatório web (página única, edição manual) | 🕓 Histórico/teste (não é reprodutível) |
| `docs/entregas/Apresentacao_QuatroNorte_v2.pptx` | Deck manual (fase anterior: mensal/por km) | 🕓 Histórico |
| `docs/historico/PrevCustManut_jeison.html` | Relatório web preliminar — R$/IPCA, grão por OS | ❌ **Obsoleto** |

**Entrega vigente:** apenas `Apresentacao_QuatroNorte.pptx` (reprodutível, gerado pelo
notebook 08, todo conteúdo de `reports/`).

---

## 8. Pendências conhecidas

- Todos os notebooks vigentes (00, 01, 02, 04, 03b/03c/03d, 05, 06, 08) já refletem o
  custo **anual** por carreta a partir da **fonte única**; são a fonte oficial de
  resultados e foram executados ponta a ponta.
- **Escopo reduzido pela fonte única:** contrato, mão de obra, peças e leituras de
  odômetro dedicadas ficam **fora de escopo** (exigiriam outras tabelas). Integrá-los
  em etapa futura ampliaria o conjunto explicativo.
- **Limitações metodológicas** a comunicar: sem filtro MAINT (todo o custo interno);
  `n_os_ano`/`custo_medio_por_os_ano` são componentes de Y (excluídos como
  explicadores); km derivado do odômetro nas OS (resets tratados); província parcial
  (~54%); estornos (custos negativos) excluídos; span ativo assume presença entre a 1ª
  e a última OS.
- `docs/historico/PrevCustManut_jeison.html`: manter apenas como histórico.

---

## 9. Glossário rápido

- **Custo interno** — parcela do custo de manutenção absorvida pela empresa
  (`charge_flag='I'`), não faturada ao cliente. Preventiva + corretiva.
- **Grão carreta × ano** — cada linha da base é uma carreta em um ano.
- **Zero-inflação** — proporção de observações com custo = 0; no grão anual cai para
  ~3% (contra ~67% no grão mensal), o que favorece a modelagem.
- **Fonte única (Single Source of Truth)** — toda a análise parte só do CSV `fato_wo_ml`.
- **Deflação (CPI)** — trazer custos de anos diferentes a um valor comum
  (dez/2025) para não confundir "custo subindo" com "dinheiro valendo menos".
- **VMRS** — Vehicle Maintenance Reporting System: código padronizado do sistema
  reparado.
- **η (eta)** — força de separação do Y entre categorias (0 a 1).
- **VIF** — fator de inflação de variância; mede redundância entre variáveis.
- **Cenário explicativo × preditivo** — explicativo inclui o uso do próprio ano;
  preditivo usa apenas atributos + histórico defasado (sem vazamento).
- **Split temporal** — treina no passado (2020–2024), testa no futuro (2025);
  evita vazamento.
- **Componente de Y** — variável que é parte aritmética do alvo (ex.: `n_os_ano`);
  não entra como explicador independente.
