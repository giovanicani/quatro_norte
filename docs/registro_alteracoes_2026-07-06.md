# Registro de alterações — 2026-07-06

Documentação da revisão metodológica e da geração da apresentação acadêmica
(entrega das Aulas 2–5 do MBA, perguntas 1–11 da agenda da disciplina).

## 1. Decisões tomadas

| Decisão | Antes | Depois |
| --- | --- | --- |
| Variável-alvo (Y) | `custo_manutencao_preventiva_por_km_deflacionado` (alvo primário desde a revisão anterior) | **`custo_manutencao_interno_por_km_deflacionado`** — custo interno total (`charge_flag='I'`, preventiva + corretiva) por km, conforme objetivo formal do projeto |
| Índice de deflação | IPCA/BCB série 433 (índice de inflação **brasileiro**) | **CPI all-items Canada** (StatCan, vetor v41690973, base 2002=100) — os custos da operação são em dólares canadenses (CAD) |
| Mês-base da deflação | dez/2025 | dez/2025 (mantido) |
| População de modelagem | `tipo_manutencao = MAINT`, `km_rodado_mes >= 500` | mantida |

### Por que a troca do deflator era obrigatória

A operação é canadense (províncias ON/QC etc., inspeção MTO, unidades Thermo
King/Carrier) e os custos estão em CAD. Aplicar IPCA (inflação do Brasil, em
BRL) distorcia todos os valores reais: a inflação canadense acumulada
2020→2025 é ≈ 20%, muito menor que a brasileira no mesmo período. Todos os
números "deflacionados" anteriores (inclusive as métricas de modelo) estavam
contaminados por esse erro.

### Observação sobre o arquivo de IPCA

O arquivo `data/raw/ipca_mensal_bcb_2020_2025.csv` não existia mais no
repositório — o notebook 04 antigo estava quebrado (e, por cascata, 05 e 06).
A nova série CPI foi baixada diretamente da API Web Data Service do StatCan e
versionada em `data/raw/cpi_canada_statcan_2020_2025.csv`.

## 2. Pipeline reprocessado

Como o Jupyter não estava disponível no ambiente, o código dos notebooks foi
extraído para scripts executáveis em `src/` (mesma lógica, mesmas saídas):

| Script | Origem / função |
| --- | --- |
| `src/run_02_base_mensal.py` | extração do notebook 02 — reconstrói `data/processed/base_mensal_carreta.csv` (749.664 linhas carreta × mês) |
| `src/run_04_deflacao_cpi.py` | **novo** — substitui o notebook 04: deflação por CPI Canadá; gera `base_mensal_carreta_deflacionada.csv`, `04_cpi_fatores.csv`, `04_validacao_deflacao.csv`, `04_comparacao_nominal_deflacionado.csv` e a figura `04_nominal_vs_deflacionado.png` |
| `src/run_03b_eda_variaveis.py` | **novo** — EDA variável-a-variável (protocolo acadêmico) com o novo Y |
| `src/run_03c_stats_ppt.py` | **novo** — estatísticas complementares do Y para o deck |
| `src/run_05b_modelagem_interno.py` | notebook 05 com o alvo trocado para `custo_manutencao_interno_por_km_deflacionado` |
| `src/build_ppt.py` | **novo** — gera `docs/Apresentacao_QuatroNorte.pptx` a partir das tabelas/figuras de `reports/` |

O notebook `04_deflacao_custos_ipca.ipynb` foi renomeado para
`_obsoleto_04_deflacao_custos_ipca.ipynb` e substituído por
`04_deflacao_custos_cpi_canada.ipynb` (mesmo código do script novo).

Para regenerar tudo do zero:

```powershell
py src\run_02_base_mensal.py
py src\run_04_deflacao_cpi.py
py src\run_03b_eda_variaveis.py
py src\run_03c_stats_ppt.py
py src\run_05b_modelagem_interno.py
py src\build_ppt.py
```

## 3. EDA variável-a-variável (nova)

O notebook 03 original era orientado a hipóteses e não cumpria o protocolo
da disciplina (pergunta 8). A nova EDA (`run_03b`) gera, sobre as 352.038
observações com Y válido:

- **Y e 18 quantitativas**: histograma + boxplot (`reports/figures/eda/quant_*.png`)
  e estatísticas N/média/DP/min/Q1/mediana/Q3/max (`03b_estatisticas_descritivas.csv`);
- **7 qualitativas**: boxplot de Y por categoria (`quali_*.png`), tabela de
  frequência (`03b_frequencia_categorias.csv`) e stats de Y por categoria
  (`03b_y_por_categoria.csv`);
- correlação Pearson/Spearman de cada X com Y (`03b_correlacao_com_y.csv`),
  eta para categóricas (`03b_eta_categoricas.csv`), matriz de Spearman entre
  X, VIF (`03b_vif.csv`), ranking de associação e evolução anual do Y.

## 4. Resultados novos (substituem os anteriores)

**Números antigos que NÃO valem mais**: R² = 0,242 / 0,19 / AUC = 0,938
(vazamento temporal, já corrigido) e R² = 0,063 (alvo preventivo + IPCA).

Com Y = custo interno total/km, deflação CPI Canadá, população MAINT e
split temporal (teste = últimos 12 meses):

- Zero-inflação: **67,1%** dos meses carreta × mês sem custo interno.
- Y: média CAD 0,091/km; mediana condicional aos positivos CAD 0,101/km.
- Em valores **reais**, o custo médio por km cresceu ≈ **+71%** (2020: 0,074 →
  2025: 0,126 CAD/km) — tendência genuína, não inflação.
- Preditores individuais mais fortes: `n_os_acum` (ρ = +0,22),
  `custo_acum_manutencao` (ρ = +0,20), `intervalo_medio_os` (ρ = −0,19) —
  o histórico da carreta é o bloco preditivo dominante (H4 suportada).
- Categóricas fracas isoladamente (máx: `regiao_operacao`, eta = 0,084).
- **Modelo recomendado: Random Forest — R² = 0,088, RMSE = 0,242,
  MAE = 0,132** no teste temporal (menor RMSE entre os elegíveis; KNN é
  benchmark amostral). Permutation importance: `km_rodado_mes`,
  `custo_acum_manutencao`, `flag_refrigerado`, `intervalo_medio_os`.
- Reconciliação: CAD 79,0 mi nominais = CAD 84,3 mi em valores de dez/2025.

## 5. Apresentação gerada

`docs/Apresentacao_QuatroNorte.pptx` — **66 slides**, 16:9, cobrindo as
perguntas 1–11 da agenda:

1. Capa + apresentação da Quatro Norte Consulting + agenda;
2. Bloco 1 — contexto, pergunta do problema, objetivo geral/específicos,
   hipóteses, 4 artigos científicos (1 slide cada);
3. Bloco 2 — modelo estrela (7 tabelas), definição do custo interno, VMRS,
   programas de PM, variável Y, correção CAD/CPI, base desnormalizada,
   feature engineering, **dicionário das variáveis do modelo** (3 slides:
   numéricas 1/2 e 2/2 + categóricas, cada variável marcada como Natural ou
   FE com a composição), protocolo de EDA, **25 slides de EDA** (1 por
   variável, com figura + estatísticas + correlação + leitura), ranking de
   associação, colinearidade/VIF, síntese da EDA;
4. Técnicas estatísticas/ML, comparação de modelos, importância de
   variáveis, hipóteses × evidências;
5. Bloco 3 — referencial teórico (síntese), metodologia (pipeline dos 7
   notebooks), limitações, encerramento.

Para editar textos/comentários dos slides: dicionários `quant_coment` /
`quali_coment` e blocos correspondentes em `src/build_ppt.py`; depois rodar
`py src\build_ppt.py`.

## 5b. Segunda rodada de limpeza (mesma data, após revisão externa)

- `regiao_operacao` defasada em 1 mês por carreta na modelagem
  (anti-vazamento); métricas praticamente inalteradas (R² 0,088 → 0,086).
- Scripts obsoletos movidos para `src/_obsoleto/` (IPCA, alvo preventivo:
  `run_03_eda.py`, `run_04_deflacao.py`, `run_05_modelagem.py`,
  `run_06_resultados.py`) e `notebooks/_obsoleto/`.
- `.gitignore` passou a ignorar `data/raw/*.csv` (dados confidenciais),
  com exceção da série pública de CPI.
- `reports/sumario_executivo.md` reescrito para a trilha vigente;
  `reports/revisao_feedback.md` marcado como histórico;
  `Plano_Analises.md` atualizado (alvo e resultados vigentes, com os
  números antigos preservados como rastreabilidade).
- Tabelas `06_*` regeneradas para o alvo interno
  (`src/run_06_resultados_interno.py`); descrição corrigida em
  `05_alvo_espelho_mao_obra.csv`; colunas renomeadas
  (`share_zero_preventivo` → `share_zero_alvo` /
  `share_zero_custo_preventivo`).
- Diagnóstico de outliers por variável adicionado
  (`src/run_03d_outliers.py` → `03d_diagnostico_outliers.csv` + slide);
  achado relevante: `n_os_acum` máx 15.006 (195× o p99) — anomalia de
  cadastro a investigar na fonte.
- Pergunta da pesquisa fixada na redação oficial ("custo de manutenção
  interno") no README e no PPT.

## 6. Pendências conhecidas

- Adicionar os nomes da equipe na capa do PPT.
- Notebooks 03/05/06 originais ainda referem o alvo preventivo — a versão
  vigente do fluxo com o alvo interno total está nos scripts `src/run_03b`,
  `src/run_05b` (os notebooks podem ser sincronizados depois, se necessário).
- `docs/PrevCustManut_jeison.html` está **desatualizado** (alvo preventivo,
  IPCA, R² antigos) — tratar como versão preliminar/histórica.
- Limitações metodológicas registradas no deck: `km_rodado_mes` é
  denominador do Y e feature; cap de outliers p99,5 calculado antes do
  split; duração de contratos vigentes censurada em 2025-12.
