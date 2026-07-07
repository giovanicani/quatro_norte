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
- **Modelo recomendado:** **Random Forest** — R² = 0,086 · RMSE = 0,242 ·
  MAE = 0,132 (teste temporal 2025).

---

## 2. Mapa de documentos — o que ler e o status de cada um

Leia nesta ordem. A coluna **Status** é o mais importante: vários arquivos
descrevem uma versão **antiga** do projeto e não devem ser usados como verdade.

| # | Documento | Para quê serve | Status |
|---|---|---|---|
| 1 | **`docs/GUIA_DO_PROJETO.md`** (este) | Ponto de entrada e mapa geral | ✅ Vigente |
| 2 | `reports/sumario_executivo.md` | Resposta ao problema, resultados e recomendações (1 página) | ✅ Vigente |
| 3 | `docs/registro_alteracoes_2026-07-06.md` | **Log da revisão**: o que mudou, por quê, e como reprocessar | ✅ Vigente |
| 4 | `README.md` | Especificação completa (contexto, dados, hipóteses, técnicas) | ⚠️ Vigente na maior parte, mas as seções 10.2/10.3/10.5 têm placeholders `✏️` (ver resultados reais no §6 deste guia) |
| 5 | `data/dicionario_de_dados.md` | Schema, tipos e origem de cada campo das 7 bases | ✅ Vigente |
| 6 | `Plano_Analises.md` | Plano de análises (alvo e resultados vigentes; números antigos mantidos como rastreio) | ✅ Vigente |
| 7 | `reports/revisao_feedback.md` | Feedback de revisão anterior | 🕓 Histórico |
| 8 | `AGENTS.md` | Guia de estilo/escopo p/ assistentes de IA | ⚠️ **Desatualizado** no alvo: ainda cita `custo_manutencao_preventiva_por_km` e deflação por IPCA |
| 9 | `notebooks/03_*`, `05_*`, `06_*` | Notebooks originais de EDA/modelagem | ⚠️ **Desatualizados**: ainda referenciam o **alvo preventivo**. O fluxo vigente está nos scripts `src/run_*` |
| 10 | `docs/PrevCustManut_jeison.html` | Relatório visual (site) preliminar | ❌ **Obsoleto**: usa **R$/IPCA** (Brasil), grão **por OS** e R² antigo (0,192) |

**Regra de ouro:** em caso de conflito, vale **sumário executivo + registro de
alterações + scripts `src/` + tabelas `reports/`**. Notebooks e AGENTS.md podem
estar defasados.

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

> ⚠️ **Ponto de atenção ainda aberto:** o **deck v2** e os scripts `src/run_05b`
> usam o alvo **interno total**. Alguns **notebooks** (03/05/06) ainda trazem, no
> texto e nas saídas, o alvo **preventivo**. Se alguém abrir os notebooks vai ver
> números diferentes (ex.: ~80% de zeros, R² ~0,063). **Os números válidos são os
> do alvo interno total** (§6). Sincronizar os notebooks é uma pendência (§8).

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

- **Dicionário completo:** `data/dicionario_de_dados.md`.
- **VMRS** ("CID da oficina"): código padronizado do sistema reparado (PM,
  04 Freios, 09 Pneus, 10 Reefer…). Usado como **dimensão de análise**, não como
  filtro do alvo. Tabela de códigos no README §9.3.
- **Bases processadas** (`data/processed/`): `base_mensal_carreta.csv`
  (749.664 linhas carreta × mês) e `base_mensal_carreta_deflacionada.csv`
  (com custos em CAD reais, dez/2025). **352.038** observações têm alvo válido
  (km ≥ 500/mês).

---

## 5. Pipeline reprodutível

O código vive em **`src/`** (extraído dos notebooks, porque o ambiente não tinha
Jupyter). Cada script corresponde a uma etapa; as saídas caem em `reports/`
(tabelas `.csv` e figuras `.png`) e em `data/processed/`.

| Ordem | Script | Faz |
|---|---|---|
| 1 | `src/run_02_base_mensal.py` | monta a base mensal carreta × mês (749.664 linhas) |
| 2 | `src/run_04_deflacao_cpi.py` | deflaciona custos (CAD) pelo CPI Canadá → base deflacionada |
| 3 | `src/run_03b_eda_variaveis.py` | EDA variável-a-variável (protocolo acadêmico, pergunta 8) |
| 4 | `src/run_03c_stats_ppt.py` | estatísticas complementares do Y para o deck |
| 5 | `src/run_03d_outliers.py` | diagnóstico de outliers por variável |
| 6 | `src/run_05b_modelagem_interno.py` | modelagem (split temporal, 9 modelos + hurdle, métricas, importâncias) |
| 7 | `src/run_06_resultados_interno.py` | tabelas de resultado (`reports/tables/06_*`) |
| 8 | `src/build_ppt.py` | gera `docs/Apresentacao_QuatroNorte.pptx` a partir de `reports/` |

**Rodar tudo do zero** (Windows / PowerShell, com os CSVs em `data/raw/`):

```powershell
py src\run_02_base_mensal.py
py src\run_04_deflacao_cpi.py
py src\run_03b_eda_variaveis.py
py src\run_03c_stats_ppt.py
py src\run_03d_outliers.py
py src\run_05b_modelagem_interno.py
py src\run_06_resultados_interno.py
py src\build_ppt.py
```

> Scripts obsoletos (alvo preventivo / IPCA) foram movidos para `src/_obsoleto/`
> e `notebooks/_obsoleto/`. Não usar.

---

## 6. Resultados (números vigentes)

Fonte canônica: `reports/tables/` + `reports/sumario_executivo.md`.

### EDA
- **Distribuição do Y:** zero-inflada (67,1% dos meses sem custo) e de cauda
  longa (assimetria ≈ 14,4). Média CAD 0,091/km; mediana condicional aos meses
  com custo CAD 0,101/km. → pede `log1p`, perda robusta e leitura em duas partes
  (ocorrência × magnitude).
- **Evolução real:** custo médio por km subiu **+71%** em termos reais
  (0,074 → 0,126 CAD/km, 2020→2025) — tendência genuína, já **sem** inflação.
- **Preditores mais fortes (Spearman com Y):** `n_os_acum` +0,22 ·
  `custo_acum_manutencao` +0,20 · `n_os_preventivas_acum` +0,19 ·
  `intervalo_medio_os` −0,19 · `km_acumulado` +0,16. **Nenhuma variável isolada
  passa de ρ ≈ 0,22** → o ganho vem de interações (favorece árvores).
- **Categóricas (η):** `regiao_operacao` 0,084 (a mais forte) · `cod_montadora`
  0,068 · `flag_refrigerado` 0,063 — fracas isoladamente.
- **Colinearidade:** VIF alto em `custo_acum` (33,9) e `n_os_acum` (25,4);
  mantidos porque o modelo final é de árvore (robusto a colinearidade).

### Modelagem (teste temporal 2025, população MAINT)

| Modelo | R² | RMSE | MAE |
|---|---|---|---|
| **Random Forest** ◀ recomendado | **0,086** | **0,242** | **0,132** |
| Gradient Boosting | 0,077 | 0,244 | 0,133 |
| Hurdle (ocorrência × magnitude) | 0,071 | 0,245 | 0,145 |
| Lineares (ridge, múltipla, polinomial) | 0,036–0,041 | 0,248 | 0,137 |
| KNN (benchmark amostral) | 0,005 | — | — |

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
| `docs/Apresentacao_QuatroNorte_v2.pptx` | Deck de apresentação (56 slides), versão mais recente, revisada | ✅ **Deck vigente** |
| `docs/Apresentacao_QuatroNorte.pptx` | Deck gerado por `src/build_ppt.py` a partir de `reports/` | ✅ Base reprodutível (regenerável) |
| `docs/Apresentacao_QuatroNorte_v2.html` | Relatório web (página única) espelhando o deck v2 — CAD/CPI, grão mensal, R² 0,086 | ✅ **Relatório web vigente** |
| `docs/PrevCustManut_jeison.html` | Relatório web preliminar — R$/IPCA, grão por OS, R² 0,192 | ❌ **Obsoleto** (não circular como resultado) |

Os dois HTMLs compartilham o **mesmo design** (papel creme sobre fundo escuro,
Archivo + IBM Plex, acentos laranja/azul), mas só o **v2** reflete a análise
correta. O antigo do Jeison é útil apenas como material exploratório histórico.

---

## 8. Pendências conhecidas

- **Sincronizar os notebooks 03/05/06** com o alvo interno total (hoje o fluxo
  vigente está nos scripts `src/run_*`).
- **Atualizar `AGENTS.md`** (ainda cita alvo preventivo + IPCA).
- **Preencher os placeholders `✏️`** do README (§10.2, 10.3, 10.5) com os
  números reais desta consolidação.
- `PrevCustManut_jeison.html`: portar para o grão mensal + CAD/CPI, ou aposentar.
- **Limitações metodológicas** a comunicar: `km_rodado_mes` é denominador do Y
  **e** feature; cap de outliers (p99,5) calculado antes do split; duração de
  contratos vigentes censurada em 2025-12; GPS parcial (região derivada da OS);
  custos negativos (estornos) excluídos.
- **Anomalia de dado a investigar na fonte:** `n_os_acum` com máx ~15.006
  (195× o p99) em pouquíssimas carretas — provável erro de cadastro.

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
