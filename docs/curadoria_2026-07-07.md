# Curadoria do Repositório — 2026-07-07

Este documento registra a curadoria estrutural e metodológica feita após a
conversão do projeto para uma trilha **notebook-first**.

## 1. Decisão de Organização

A trilha vigente do projeto passa a ser:

```text
notebooks/  = execução célula a célula e visualização dos resultados
data/       = dados brutos locais e bases processadas geradas
reports/    = tabelas e figuras produzidas pelos notebooks
docs/       = documentação, entregas, diagramas e histórico
```

Os scripts `.py` foram removidos da trilha operacional. A lógica antes
consolidada em `src/` foi convertida para notebooks, pois o projeto acadêmico
precisa permitir inspeção visual de cada etapa, tabela, gráfico e resultado.

## 2. Estrutura Atual Recomendada

```text
.
├── AGENTS.md
├── README.md
├── data/
│   ├── extract_custo_interno_km.sql
│   ├── raw/
│   ├── interim/
│   └── processed/
├── docs/
│   ├── diagramas/
│   ├── entregas/
│   ├── historico/
│   ├── curadoria_2026-07-07.md
│   ├── dicionario_de_dados.md
│   ├── dicionario_variaveis_candidatas.md
│   ├── GUIA_DO_PROJETO.md
│   └── registro_alteracoes_2026-07-06.md
├── notebooks/
│   ├── 00_contexto_inventario_dados.ipynb
│   ├── 01_qualidade_integridade_dados.ipynb
│   ├── 02_base_analitica_mensal.ipynb
│   ├── 04_deflacao_custos_cpi_canada.ipynb
│   ├── 03b_eda_variaveis.ipynb
│   ├── 03c_estatisticas_resumo.ipynb
│   ├── 03d_diagnostico_outliers.ipynb
│   ├── 05_modelagem_preditiva.ipynb
│   ├── 06_resultados_recomendacoes.ipynb
│   ├── 07_painel_resultados.ipynb
│   ├── 08_build_apresentacao.ipynb
│   └── README.md
└── reports/
    ├── figures/
    ├── tables/
    └── sumario_executivo.md
```

## 3. Correções Aplicadas

- `AGENTS.md` foi atualizado para o alvo vigente
  `custo_manutencao_interno_por_km_deflacionado` e deflação por CPI Canadá.
- `docs/GUIA_DO_PROJETO.md` foi ajustado para tratar os notebooks como fonte
  operacional vigente.
- `docs/registro_alteracoes_2026-07-06.md` foi marcado como registro histórico
  da rodada em que ainda havia `src/*.py`.
- `docs/historico/Plano_Analises.md` recebeu aviso de arquivo histórico.
- `notebooks/07_painel_resultados.ipynb` foi ajustado para apontar para a
  sequência de notebooks, não para `src/`.
- Notebooks com condição antiga `PROJECT_ROOT.name in ("notebooks", "src")`
  foram simplificados para `PROJECT_ROOT.name == "notebooks"`.
- Os CSVs brutos reais de `data/raw/` foram removidos do índice do git com
  `git rm --cached`, permanecendo no disco local. A série pública de CPI segue
  versionada.
- `.gitignore` passou a ignorar `.cache/`.
- O diagrama antigo foi movido para `docs/diagramas/`.
- Entregas foram concentradas em `docs/entregas/`.
- Materiais substituídos foram concentrados em `docs/historico/`.

## 4. Validações Feitas

- Todos os notebooks em `notebooks/*.ipynb` foram validados como JSON válido.
- `git ls-files data/raw data/processed` agora lista apenas:
  - `data/raw/.gitkeep`
  - `data/raw/cpi_canada_statcan_2020_2025.csv`
  - `data/processed/.gitkeep`
- Referências vivas para caminhos antigos foram reduzidas. As menções a `src/`
  remanescentes estão em contexto explicativo ou histórico.

## 5. Pontos Que Ainda Precisam de Decisão

1. **Implementar as 46 variáveis candidatas**

   O dicionário metodológico existe, mas a base nova ainda precisa incorporar
   todas as features de recência, janelas móveis, densidade por km,
   reincidência por sistema e interações. As 5 variáveis novas do ativo
   (`tailgate_flag`, `unit_subtype`, `tire_size`, `suspension_type`,
   `new_used_indicator`) já foram integradas.

2. **Recalcular EDA, correlação, VIF e modelagem após cada novo pacote de features**

   A reexecução da base atual já foi feita com a exclusão da `8441` e as 5
   variáveis novas do ativo. Ao incorporar o próximo pacote de features,
   atualizar novamente:
   - atualizar `03b_estatisticas_descritivas.csv`;
   - atualizar `03b_correlacao_com_y.csv`;
   - atualizar `03b_eta_categoricas.csv`;
   - atualizar VIF;
   - atualizar métricas de modelos;
   - atualizar importância de variáveis.

3. **Manter o papel do `07_painel_resultados.ipynb`**

   Ele é útil para leitura rápida, mas não substitui a execução da sequência
   completa. Manter como painel executivo.

4. **Avaliar versionamento de resultados grandes**

   `reports/tables/02_os_preventivas_mistas.csv` tem tamanho relevante. Não é
   tão crítico quanto dados brutos, mas pode ser reavaliado se o repositório
   ficar pesado.

5. **Verificar consistência do deck vigente**

   O deck foi regenerado, mas ainda deve ser conferido visualmente contra os
   novos números, especialmente `unit_subtype` como novo fator relevante.

6. **Reexecutar inventário e qualidade (00/01)** — ✅ **Feito.**

   As tabelas `reports/tables/00_*` e `reports/tables/01_*` foram reexecutadas
   sobre a nova extração (notebooks 00 e 01, exit 0). Inventário, integridade de
   chaves, valores ausentes, custos, odômetro e consistência temporal atualizados.

## 6. Recomendação de Uso

Para trabalhar no projeto:

1. Abrir `docs/GUIA_DO_PROJETO.md`.
2. Abrir `notebooks/README.md`.
3. Executar os notebooks na ordem:

```text
00 → 01 → 02 → 04 → 03b → 03c → 03d → 05 → 06 → 08
```

4. Usar `notebooks/07_painel_resultados.ipynb` apenas para consulta rápida.
5. Atualizar `README.md`, `reports/sumario_executivo.md` e o deck depois da
   reexecução final.

## 7. Verificação de consistência (2026-07-07)

Passagem de auditoria após a conversão notebook-first, executando o pipeline
convertido de ponta a ponta (`02 → 04 → 03b/03c/03d → 05 → 06`, exit 0) e
cruzando números e referências entre documentos.

**Confirmado (sem ação):**

- Pipeline convertido roda inteiro sobre os dados reais; cada célula de código
  compila isolada (a divisão em células não quebrou nenhuma instrução).
- `git ls-files data/raw data/processed` lista apenas `.gitkeep` (×2) e
  `cpi_canada_statcan_2020_2025.csv` — CSVs brutos fora do versionamento.
- Nenhuma referência viva a caminhos mortos (`src/run_*`, `build_ppt.py`,
  `00_pipeline_vigente.ipynb`, `03_analise_exploratoria_hipoteses.ipynb`,
  `create_analysis_notebooks.py`) em README, guia, curadoria, sumário e
  `notebooks/README.md`.
- Métrica do modelo **nesta primeira passagem** (antes de integrar as 5 colunas
  novas): Random Forest R² = 0,086 · RMSE = 0,2424 · MAE = 0,1317 — coerente com
  guia e sumário à época. (Após a integração, ver a atualização no fim de §5.)

**Corrigido nesta passagem:**

- `README.md` §16 dizia R² = 0,088 (valor pré-antivazamento); ajustado para
  **0,086** para bater com guia, sumário e as tabelas regeneradas.
- `docs/GUIA_DO_PROJETO.md` (mapa de documentos) dizia que o README tinha
  placeholders; corrigido após a reexecução: **§10.2, §10.3, §10.4 e §10.5
  estão preenchidos**.

**Preparação para a base nova (feita em `notebooks/02_base_analitica_mensal.ipynb`):**

Como as regras novas estavam só na documentação (não no código) e a
reexecução com a base nova rodaria "verde" ignorando-as em silêncio, foi
adicionada uma célula de curadoria logo após o carregamento das bases:

- **Exclusão da `id_carreta = 8441`** de todas as bases (`dim`, `wo`, `labour`,
  `parts`, `readings`, `contracts`) antes de qualquer agregação — regra
  determinística, aplicada já.
- **Check ruidoso das 5 colunas novas esperadas** (`tailgate_flag`,
  `unit_subtype`, `tire_size`, `suspension_type`, `new_used_indicator`): lista
  presentes/ausentes em `dim_carretas` e alerta quando ausentes, para que um
  nome divergente na base nova apareça de forma visível.

**Atualização — as 5 colunas novas foram integradas e o projeto reexecutado:**

Descobriu-se que as 5 colunas vivem em `fato_wo_ml` (grão OS), não em
`dim_carretas`. Portanto:

- `notebooks/02` passou a carregar `fato_wo_ml`, derivar os 5 atributos por
  `id_carreta` (primeiro valor não-nulo) e juntá-los na base mensal; o check
  agora aponta para `fato_wo_ml`.
- `notebooks/05` (`categorical_features`) e `notebooks/03b` (EDA) incluem as 5.
- Pipeline reexecutado (02 → 04 → 03b/03c/03d → 05 → 06, exit 0). Resultados:
  **351.956** obs; **Random Forest R² = 0,085 · RMSE = 0,243 · MAE = 0,131**;
  `unit_subtype` é a categórica mais forte (η = 0,128) e 2º fator na importância
  por permutação. A `id_carreta = 8441` já não existe na extração atual (filtro
  removeu 0 linhas — segue como guard).
- README (§9.2, §10.2–10.5, §16), `GUIA_DO_PROJETO.md` e `sumario_executivo.md`
  atualizados para refletir esses números.

Nota operacional: a nova extração dos CSVs removeu o `cpi_canada_statcan_2020_2025.csv`
do disco; ele foi restaurado do git (é versionado). Reexecuções futuras que
substituam `data/raw/` devem preservar esse arquivo.

**Pendências de consistência ainda abertas**:

- Implementar e testar as features candidatas adicionais que ainda não entraram
  na base mensal, especialmente janelas 3/6/12 meses, densidade por 10 mil km,
  reincidência por sistema e interações.
- Conferir visualmente o deck em `docs/entregas/Apresentacao_QuatroNorte.pptx`
  contra os novos números, especialmente `unit_subtype` como novo fator
  relevante.
- `docs/registro_alteracoes_2026-07-06.md` cita R² = 0,088 como resultado; é
  documento **histórico** (registra a transição 0,088 → 0,086), então foi
  mantido como está.
