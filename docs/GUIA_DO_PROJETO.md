# Guia do projeto — Previsão de Custos de Manutenção de Carretas

> **Comece por aqui.** Este é o ponto de entrada para entender o que foi feito.
> Ele resume o projeto, diz **o que ler e em que ordem**, marca o que é
> **vigente** vs. **histórico/desatualizado**, e explica como reproduzir os
> resultados. Os documentos detalhados continuam onde estão — aqui a gente só
> costura tudo.
>
> Projeto aplicado do MBA (FGV) para a **Quatro Norte Consulting** · Grupo 01 ·
> Marlon Wenzel, Jeison Lima, Rodrigo Queiroz, Giovani Cani ·
> última consolidação: **2026-07-06**.

---

## 1. O projeto em 60 segundos

- **Cliente / operação:** empresa de leasing/rental de carretas no **Canadá**
  (secas e refrigeradas de até 53′, ON/QC e outras províncias). A manutenção é
  **própria** (oficinas registram ordens de serviço com mão de obra e peças).
- **Pergunta:** *quais fatores mais influenciam o custo de manutenção **interno**
  das carretas — e como prever esse custo por km futuro a partir do histórico?*
- **Custo interno** = a parte absorvida pela empresa (`charge_flag = 'I'`), **não**
  faturada ao cliente. Inclui **preventiva E corretiva** — "interno" ≠ "preventivo".
- **Variável-alvo (Y):** `custo_manutencao_interno_por_km_deflacionado`, no grão
  **carreta × mês**, em **CAD** deflacionado pelo **CPI do Canadá** (base dez/2025).
- **Resposta curta:** o **histórico operacional da carreta** domina (nº de OS
  acumuladas, custo acumulado, intervalo entre OS). Atributos fixos (ano, eixos)
  e contrato pesam pouco. O problema é **zero-inflado** (67% dos meses sem custo);
  o modelo serve para **priorizar frota e apoiar orçamento**, não para previsão
  pontual precisa.
- **Modelo recomendado:** **Random Forest** — R² = 0,085 · RMSE = 0,243 ·
  MAE = 0,131 (teste temporal 2025).

---

## 2. Mapa de documentos — o que ler e o status de cada um

Leia nesta ordem. A coluna **Status** é o mais importante: vários arquivos
descrevem uma versão **antiga** do projeto e não devem ser usados como verdade.

| # | Documento | Para quê serve | Status |
|---|---|---|---|
| 1 | **`docs/GUIA_DO_PROJETO.md`** (este) | Ponto de entrada e mapa geral | ✅ Vigente |
| 2 | `reports/sumario_executivo.md` | Resposta ao problema, resultados e recomendações (1 página) | ✅ Vigente |
| 3 | `docs/curadoria_2026-07-07.md` | Curadoria estrutural: o que foi organizado, validado e o que falta ajustar | ✅ Vigente |
| 4 | `docs/revisao_pos_base_nova_2026-07-07.md` | Revisão após nova extração, novos resultados e pontos ainda pendentes | ✅ Vigente |
| 5 | `docs/registro_alteracoes_2026-07-06.md` | Log histórico da revisão alvo interno/CPI; não é o passo a passo operacional atual | 🕓 Histórico metodológico |
| 6 | `README.md` | Especificação completa (contexto, dados, hipóteses, técnicas) | ✅ Vigente |
| 7 | `docs/dicionario_de_dados.md` | Schema, tipos e origem de cada campo das 7 bases | ✅ Vigente |
| 8 | `docs/dicionario_variaveis_candidatas.md` | Especificação metodológica das 46 X candidatas: grão, fórmula, defasagem, vazamento e hipótese | ✅ Vigente |
| 9 | `docs/historico/Plano_Analises.md` | Plano de análises original, mantido para rastreio metodológico | 🕓 Histórico |
| 10 | `docs/historico/revisao_feedback.md` | Feedback de revisão anterior | 🕓 Histórico |
| 11 | `AGENTS.md` | Guia de estilo/escopo p/ assistentes de IA | ✅ Vigente |
| 12 | `notebooks/` (00 → 08, ordem em `notebooks/README.md`) | Pipeline reprodutível célula a célula — **fonte única do projeto** | ✅ Ponto de entrada operacional |
| 13 | `notebooks/07_painel_resultados.ipynb` | Painel visual que lê as saídas de `reports/` sem reexecutar tudo | ✅ Recomendado para inspeção rápida |
| 14 | `docs/historico/PrevCustManut_jeison.html` | Relatório visual (site) preliminar | ❌ **Obsoleto**: usa **R$/IPCA** (Brasil), grão **por OS** e R² antigo (0,192) |

**Regra de ouro:** em caso de conflito, vale **sumário executivo + registro de
alterações + notebooks vigentes + tabelas `reports/`**.

---

## 3. Decisões canônicas vigentes (e o que mudou)

Estas quatro decisões definem a análise atual. Detalhe completo no
`registro_alteracoes_2026-07-06.md`.

| Decisão | Vigente | Era antes | Por quê mudou |
|---|---|---|---|
| **Variável-alvo** | `custo_manutencao_interno_por_km_deflacionado` (interno **total**: prev. + corretiva) | alvo **preventivo** por km | Alinhar ao objetivo formal: prever o custo que a empresa **absorve**, não só o preventivo |
| **Deflator** | **CPI Canadá** (StatCan, vetor v41690973, base dez/2025) | **IPCA/BCB** (Brasil) | Os custos são em **CAD**; IPCA distorcia todos os valores reais (inflação BR ≫ CA) |
| **População de modelagem** | `tipo_manutencao = MAINT` · `km_rodado_mes ≥ 500` | mantida | Isola o efeito do tipo de contrato e evita razão custo/km explosiva |
| **Anti-vazamento** | features históricas **defasadas** + split **temporal** (teste = 2025) + `regiao_operacao` defasada 1 mês | havia vazamento temporal | Métricas antigas eram infladas por "colar" informação do futuro |

> ⚠️ **Decisão de organização:** os **notebooks em `notebooks/` são a fonte
> única e reprodutível** — a lógica antes em `src/*.py` foi convertida célula a
> célula e os scripts `.py` foram removidos. Execute na ordem de
> `notebooks/README.md` para ver resultado a resultado. Para inspeção rápida sem
> reexecutar tudo, use `notebooks/07_painel_resultados.ipynb`. **Os números
> válidos são os do alvo interno total** (§6).

---

## 4. Dados

- **Origem:** extração SQL única em `data/extract_custo_interno_km.sql`, janela
  **2020-01-01 → 2025-12-31**, frota própria (`cus_id_owner = 4`, ativas, com
  leitura de KM válida). Gera os CSVs em `data/raw/` (**não versionados** —
  confidenciais; exceção: a série pública de CPI).
- **Modelo estrela — 1 dimensão + 6 fatos** (ligados por `id_carreta`; OS/mão de
  obra/peças por `id_os`):

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
- **Bases processadas** (`data/processed/`): `base_mensal_carreta.csv`
  (749.592 linhas carreta × mês) e `base_mensal_carreta_deflacionada.csv`
  (com custos em CAD reais, dez/2025). **351.956** observações têm alvo válido
  (km ≥ 500/mês), após excluir a `id_carreta = 8441`.

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
| 1 | `notebooks/02_base_analitica_mensal.ipynb` | monta a base mensal carreta × mês (749.592 linhas; exclui a 8441) |
| 2 | `notebooks/04_deflacao_custos_cpi_canada.ipynb` | deflaciona custos (CAD) pelo CPI Canadá → base deflacionada |
| 3 | `notebooks/03b_eda_variaveis.ipynb` | EDA variável-a-variável (protocolo acadêmico, pergunta 8) |
| 4 | `notebooks/03c_estatisticas_resumo.ipynb` | estatísticas complementares do Y para o deck |
| 5 | `notebooks/03d_diagnostico_outliers.ipynb` | diagnóstico de outliers por variável |
| 6 | `notebooks/05_modelagem_preditiva.ipynb` | modelagem (split temporal, 9 modelos + hurdle, métricas, importâncias) |
| 7 | `notebooks/06_resultados_recomendacoes.ipynb` | tabelas de resultado (`reports/tables/06_*`) |
| 8 | `notebooks/08_build_apresentacao.ipynb` | gera `docs/entregas/Apresentacao_QuatroNorte.pptx` a partir de `reports/` (requer `python-pptx`) |

> Antes de rodar 00–01 (contexto/qualidade) e 02, é preciso ter os CSVs em
> `data/raw/`. A EDA (03b/03c/03d) roda **depois** da deflação (04), pois usa o
> alvo deflacionado. Execute cada notebook na ordem acima e veja o resultado
> célula a célula.

> Versões obsoletas (alvo preventivo / IPCA) foram removidas junto com os
> scripts `.py`; o histórico permanece no controle de versão (git).

---

## 6. Resultados (números vigentes)

Fonte canônica: `reports/tables/` + `reports/sumario_executivo.md`.

### EDA
- **Distribuição do Y:** zero-inflada (67,1% dos meses sem custo) e de cauda
  longa (assimetria ≈ 14,4). Média CAD 0,091/km; mediana condicional aos meses
  com custo CAD 0,101/km. → pede `log1p`, perda robusta e leitura em duas partes
  (ocorrência × magnitude).
- **Evolução real:** custo médio por km subiu **+69%** em termos reais
  (0,074 → 0,125 CAD/km, 2020→2025) — tendência genuína, já **sem** inflação.
- **Preditores mais fortes (Spearman com Y):** `n_os_acum` +0,22 ·
  `custo_acum_manutencao` +0,20 · `n_os_preventivas_acum` +0,19 ·
  `intervalo_medio_os` −0,19 · `km_acumulado` +0,16. **Nenhuma variável isolada
  passa de ρ ≈ 0,22** → o ganho vem de interações (favorece árvores).
- **Categóricas (η):** `unit_subtype` 0,128 (a mais forte) · `regiao_operacao`
  0,084 · `flag_refrigerado` 0,064 — as demais fracas isoladamente.
- **Colinearidade:** VIF acima de 10 apenas em `n_os_acum` (11,2) e
  `custo_acum_manutencao` (11,1); mantidos porque o modelo final é de árvore
  (robusto a colinearidade).

### Modelagem (teste temporal 2025, população MAINT)

| Modelo | R² | RMSE | MAE |
|---|---|---|---|
| **Random Forest** ◀ recomendado | **0,085** | **0,243** | **0,131** |
| Gradient Boosting | 0,079 | 0,243 | 0,132 |
| Hurdle (ocorrência × magnitude) | 0,072 | 0,244 | 0,138 |
| Lineares (ridge, múltipla, polinomial) | 0,036–0,044 | 0,248 | 0,134 |
| KNN (benchmark amostral) | 0,014 | — | — |

- **R² ≈ 9%**: modesto, mas suficiente para **ordenar carretas** por risco e
  apoiar orçamento. Não é previsão pontual precisa.
- **Permutation importance:** `km_rodado_mes` (⚠️ é também o **denominador** do Y
  — relação em parte mecânica), `custo_acum_manutencao`,
  `custo_preventivo_medio_movel_3m`, `flag_refrigerado`, `intervalo_medio_os`.

### Hipóteses × evidências
| | Hipótese | Veredito |
|---|---|---|
| H1 | Duração de contrato ⇒ custo | ❌ Não suportada (ρ ≈ 0,02) |
| H2 | Idade ⇒ custo | ➖ Parcial (efeito direto fraco; opera via histórico) |
| H3 | Quilometragem ⇒ custo | ➖ Parcial (km_acumulado +0,16; km mensal é denominador) |
| H4 | Histórico prevê custo futuro | ✅ Suportada (bloco preditivo dominante) |
| H5 | Operação/contrato influenciam | ➖ Parcial (região desloca; contrato fraco) |

---

## 7. Entregáveis — o que é o quê

| Arquivo | O que é | Status |
|---|---|---|
| `docs/entregas/Apresentacao_QuatroNorte_v2.pptx` | Deck de apresentação (56 slides), versão mais recente, revisada | ✅ **Deck vigente** |
| `docs/entregas/Apresentacao_QuatroNorte.pptx` | Deck gerado por `notebooks/08_build_apresentacao.ipynb` a partir de `reports/` | ✅ Base reprodutível (regenerável) |
| `docs/entregas/Apresentacao_QuatroNorte_v2.html` | Relatório web (página única) espelhando o deck v2 — CAD/CPI, grão mensal | ⚠️ **Vigente na abordagem, mas com números da rodada anterior (R² 0,086)**: regerar após a última reexecução (R² 0,085 + `unit_subtype`) |
| `docs/historico/PrevCustManut_jeison.html` | Relatório web preliminar — R$/IPCA, grão por OS, R² 0,192 | ❌ **Obsoleto** (não circular como resultado) |

Os dois HTMLs compartilham o **mesmo design** (papel creme sobre fundo escuro,
Archivo + IBM Plex, acentos laranja/azul), mas só o **v2** reflete a análise
correta. O antigo do Jeison é útil apenas como material exploratório histórico.

---

## 8. Pendências conhecidas

- Os notebooks vigentes (02, 03b/03c/03d, 04, 05, 06) já refletem o alvo
  interno total + CPI Canadá; são a fonte oficial de resultados.
- **Inventário e qualidade atualizados:** os notebooks 00 e 01 foram
  reexecutados sobre a nova extração; as tabelas `reports/tables/00_*` e
  `reports/tables/01_*` estão atualizadas e coerentes com os CSVs vigentes.
- **Implementar e testar as features candidatas adicionais** do
  `docs/dicionario_variaveis_candidatas.md` que ainda não entraram na base
  mensal: janelas 3/6/12 meses, densidade por 10 mil km, reincidência por
  sistema e interações.
- **Avaliar versionamento de artefatos grandes** em `reports/tables/`,
  especialmente `02_os_preventivas_mistas.csv`.
- `docs/historico/PrevCustManut_jeison.html`: portar para o grão mensal +
  CAD/CPI, ou manter apenas como histórico.
- **Limitações metodológicas** a comunicar: `km_rodado_mes` é denominador do Y
  **e** feature; cap de outliers (p99,5) calculado antes do split; duração de
  contratos vigentes censurada em 2025-12; GPS parcial (região derivada da OS);
  custos negativos (estornos) excluídos.
- **Anomalia 8441 resolvida na base analítica:** o máximo de `n_os_acum` caiu
  de 15.006 para 147 após excluir a identificação de trabalhos genéricos de
  pátio.

---

## 9. Glossário rápido

- **Custo interno** — parcela do custo de manutenção absorvida pela empresa
  (`charge_flag='I'`), não faturada ao cliente. Preventiva + corretiva.
- **Grão carreta × mês** — cada linha da base é uma carreta em um mês.
- **Zero-inflação** — alta proporção de meses com custo = 0 (a carreta não foi à
  oficina); mantidos como informação legítima.
- **Deflação (CPI)** — trazer custos de anos diferentes a um valor comum
  (dez/2025) para não confundir "custo subindo" com "dinheiro valendo menos".
- **VMRS** — Vehicle Maintenance Reporting System: código padronizado do sistema
  reparado.
- **η (eta)** — força de separação do Y entre categorias (0 a 1).
- **VIF** — fator de inflação de variância; mede redundância entre variáveis.
- **Hurdle / duas partes** — modela separadamente *se* há custo (ocorrência) e
  *quanto* (magnitude).
- **Split temporal** — treina no passado (2020–2024), testa no futuro (2025);
  evita vazamento.
- **MAINT / NET / MIX** — tipos de cobertura de manutenção no contrato.
