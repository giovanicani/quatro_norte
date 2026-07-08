# Revisão Metodológica — Custo ANUAL por carreta (2026-07-07)

> **Documento autoritativo desta revisão.** Registra a mudança de abordagem, as
> decisões tomadas, uma inconsistência de dados sinalizada e resolvida, a nova
> metodologia e os resultados reais gerados pelos notebooks. Em caso de conflito com
> documentos anteriores, **vale este documento + os notebooks vigentes + as tabelas em
> `reports/`**.

## 1. O que mudou

O projeto deixou de prever o **custo interno por quilômetro** (CAD/km, grão carreta ×
mês) e passou a **analisar e modelar o custo anual de manutenção por carreta**
(CAD/ano, grão carreta × ano), em valores **reais** corrigidos pela inflação
canadense (CPI).

| Dimensão | Antes | Agora |
|---|---|---|
| Variável resposta (Y) | `custo_manutencao_interno_por_km_deflacionado` | `custo_ano_real` — custo anual por carreta (CAD/ano, real dez/2025) |
| Grão | carreta × mês | **carreta × ano** |
| Fonte de dados | 7 tabelas do modelo estrela (joins + feature engineering) | **fonte única**: `data/raw/fato_wo_ml_2020-01-01_to_2025-12-31.csv` |
| Deflator | CPI Canadá (mantido) | CPI Canadá (mantido) |
| Zero-inflação | ~67% dos meses | **~3,2%** dos carreta-anos |

## 2. Decisões tomadas nesta revisão

1. **Fonte única (Single Source of Truth).** Toda a análise parte exclusivamente do
   CSV consolidado `fato_wo_ml`. A extração SQL, o modelo estrela, os *joins* e o
   *feature engineering* são tratados como **etapa anterior de preparação** — não são
   reexecutados. Os notebooks que liam as 7 tabelas foram movidos para
   `notebooks/historico/`.
2. **Escopo de variáveis reduzido e honesto.** Ver seção 3.
3. **Sem filtro `MAINT`.** O filtro histórico por `tipo_manutencao = MAINT` dependia de
   `fato_contratos`, ausente da fonte única. Analisa-se **todo o custo interno**.
4. **CPI real obtido da fonte oficial.** A série do CPI (que não estava mais no disco)
   foi baixada da **Statistics Canada** (WDS, vetor **v41690973**, all-items Canada,
   base 2002=100) e salva em `data/raw/cpi_canada_statcan_2020_2025.csv`. Valores
   publicados, não estimados.
5. **Remoção de resíduos de IPCA.** O notebook obsoleto de deflação por IPCA foi
   removido; nenhuma referência ao IPCA brasileiro permanece nos artefatos vigentes.

## 3. Inconsistência sinalizada e resolvida (fonte × 46 variáveis)

A revisão presumia que o CSV consolidado já continha as **46 variáveis** candidatas.
Na verificação, o arquivo tem **25 colunas no grão de OS** (1 linha = 1 ordem de
serviço), com custos **nominais** e **sem** dados de contrato, mão de obra, peças ou
leituras de odômetro dedicadas. Cerca de **metade** das 46 variáveis do desenho
original vem de **outras tabelas** e não existe fisicamente nesta fonte.

**Resolução (decisão do responsável):** aderir literalmente à fonte única e **reduzir
o escopo**. O universo de variáveis candidatas passa a **~25 variáveis** deriváveis do
CSV. Ficam **fora de escopo** (exigiriam outras tabelas): variáveis de **contrato**
(`tipo_contrato`, `tipo_manutencao`, `franquia_km_mensal`, duração), **km rodado por
leitura** e densidades por 10k km, **mão de obra** (`sistema_vmrs`,
`flag_terceirizado`) e **peças** (`flag_garantia`, `prop_pecas_garantia`), além de
`cod_modelo`/`classe`/`grupo_manutencao` (apenas `descricao_carreta` aproxima o tipo).

Universo candidato (25): atributos do ativo (`cod_montadora`, `ano_modelo`, `eixos`,
`comprimento`, `flag_refrigerado`, `unit_subtype`, `tire_size`, `suspension_type`,
`new_used_indicator`, `descricao_carreta`), `idade_carreta`, geografia
(`regiao_operacao`, `provincia_estado`), exposição (`km_acumulado_fim_ano`,
`km_rodado_ano`), operação do ano (`n_os_ano`, `n_sistemas_vmrs_distintos_ano`,
`share_pm_ano`, `vmrs_predominante_ano`, `custo_medio_por_os_ano`) e histórico defasado
(`n_os_ano_anterior`, `custo_ano_anterior`, `n_os_acum_ate_ano_anterior`,
`custo_acum_ate_ano_anterior`, `anos_ativo_ate_ano_anterior`).

`tailgate_flag` foi **removida** (variância nula: constante `N`). `n_os_ano` e
`custo_medio_por_os_ano` são **componentes aritméticos de Y** (Y = n_os × custo médio
por OS) e não competem como explicadores no modelo.

## 4. Metodologia (sequência)

Base consolidada (CSV) → validação de qualidade → definição de Y anual → correção
pelo CPI Canadá → EDA (univariada, histogramas/boxplots) → relação individual X↔Y
(Pearson/Spearman, ANOVA/eta) → multicolinearidade (matriz + VIF) → **ranking** →
**seleção das variáveis** → modelagem (estatística + ML, split temporal
treino 2020–2024 / teste 2025) → avaliação → discussão/limitações/conclusão.

## 5. Resultados reais (gerados pelos notebooks)

**Base e Y.** 49.248 linhas carreta × ano · 9.859 carretas · 2020–2025 · 223.408 OS
analíticas (após excluir 3 fora da janela e 179 estornos negativos). Custo interno
total **CAD 77,18 mi nominal / 82,43 mi real** (dez/2025). Y: média **CAD 1.673,72/ano**,
mediana **812,55**, assimetria **3,79**, **3,2%** de carreta-anos com custo zero.

**Inflação.** CPI 136,8 (2020-01) → 165,0 (2025-12), **+20,6%**. Custo real médio por
carreta subiu de **CAD 1.334 (2020) para 2.026 (2025), +51,9%** — aumento real, já
sem inflação.

**EDA — associação com Y (Spearman | eta).** Entre as explicativas:
`custo_ano_anterior` 0,536 · `n_os_ano_anterior` 0,540 · `km_rodado_ano` 0,530 ·
histórico acumulado ~0,45 · `km_acumulado_fim_ano` 0,428 · `idade_carreta` 0,018
(fraca). Categóricas: `unit_subtype` eta 0,55 · `flag_refrigerado` **0,43** ·
`cod_montadora` 0,24 (`descricao_carreta` 0,59 é inflada pela alta cardinalidade).
VIF > 10 em `idade_carreta`, `n_os_acum` e `ano_modelo` (colinearidades esperadas).

**Modelagem (teste temporal 2025).**
- Cenário **explicativo** (inclui uso do ano): melhor **Gradient Boosting R² = 0,572**
  (RMSE 1.753, MAE 895); Random Forest 0,571.
- Cenário **preditivo** (só atributos + histórico defasado, sem vazamento): melhor
  **Random Forest R² = 0,429** (RMSE 2.026, MAE 1.064). Modelos lineares têm R² < 0
  (caudas extremas) — árvores/ensembles são claramente superiores.
- **Importância (permutação, preditivo):** `flag_refrigerado` 0,22 (dominante) ·
  `n_os_ano_anterior` 0,12 · `km_acumulado_inicio_ano` 0,072 · `custo_ano_anterior`
  0,066 · histórico acumulado ~0,06 · `idade_carreta` 0,032 · `unit_subtype` 0,031.

**Hipóteses (adaptadas à unidade anual e à fonte única):** H2 (uso/km) e H3 (histórico)
**suportadas**; H4 (características do ativo) **suportada**; H1 (idade isolada) **não
suportada**; H5 (região) **parcial/fraca**. Hipóteses de **contrato** ficaram **fora
de escopo** (dados ausentes).

## 6. Reprodutibilidade notebook ↔ PowerPoint

Todos os números, tabelas e figuras da apresentação são gerados pelos notebooks e
salvos em `reports/tables/` e `reports/figures/`. O deck
`docs/entregas/Apresentacao_QuatroNorte.pptx` (**23 slides**) é montado pelo notebook
`08_build_apresentacao.ipynb` a partir desses artefatos — nenhum resultado é digitado
manualmente. O ambiente foi provisionado com `scikit-learn`, `scipy`, `python-pptx` e
`statsmodels`.

## 7. Pendências / próximos passos

- Integrar, em etapa futura, contrato/mão de obra/peças para ampliar o conjunto
  explicativo além da fonte única atual.
- `Apresentacao_QuatroNorte_v2.html`/`.pptx` (sem gerador reprodutível) atualizados
  in-place para o grão anual.
- Documentos históricos (`docs/historico/registro_alteracoes_2026-07-06.md`,
  `docs/historico/revisao_pos_base_nova_2026-07-07.md`) descrevem a fase mensal/por-km e permanecem
  marcados como históricos.
