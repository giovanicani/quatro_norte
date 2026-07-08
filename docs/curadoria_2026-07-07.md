# Curadoria do Repositório — 2026-07-07 (Histórico: Fase Mensal)

> 🕓 **ARQUIVO HISTÓRICO.** Este documento registra a curadoria da **fase mensal / por km**
> (grão carreta × mês, alvo por km, 7 tabelas do modelo estrela, IPCA→CPI).
>
> **Trilha vigente** (desde 2026-07-07): **custo anual por carreta**, fonte única
> `fato_wo_ml`, CPI Canadá, grão carreta × ano. Ver
> [`revisao_anual_2026-07-07.md`](revisao_anual_2026-07-07.md).

---

## Rastreio da fase mensal (preservado para auditoria)

### Estrutura da fase mensal

- **Grão:** carreta × mês (749.592 linhas)
- **Alvo:** `custo_manutencao_interno_por_km_deflacionado` (CAD/km)
- **Deflação:** IPCA/BCB → depois CPI Canadá
- **População:** `tipo_manutencao = MAINT`, `km_rodado_mes >= 500`
- **Zero-inflação:** 67,1% de meses sem custo
- **Desempenho:** Random Forest R² = 0,085 (teste 2025)
- **Variáveis:** ~46 candidatas; 5 novas de ativo integradas

### Artefatos gerados (fase mensal)

- Tabelas em `reports/tables/` (prefixos 00–06, grão mensal)
- Figuras EDA em `reports/figures/` (boxplots, distribuições, correlações)
- Deck `.pptx` versão mensal (R² 0,085)
- HTML manual `v2` (sem gerador reprodutível)

### Documentação da fase mensal (preservada)

Arquivos históricos movidos:
- `docs/historico/Plano_Analises.md` — plano original
- `docs/historico/revisao_feedback.md`, `revisao_pos_base_nova_2026-07-07.md`
- `notebooks/historico/02_base_analitica_mensal.ipynb`, `03_analise_exploratoria_hipoteses.ipynb`

Raiz:
- `Plano_Analises.md` — marcado como histórico (banner)

---

## Passagem para fase anual (2026-07-07)

Decisão: migrar para **custo anual por carreta** (carreta × ano), **fonte única** (`fato_wo_ml`),
**~25 variáveis deriváveis**.

**Ganhos:**
- Zero-inflação: 67% → 3,2%
- Sinal preditivo: R² 0,085 → 0,43–0,57
- Clareza: 46 variáveis (muitas exigiam outras tabelas) → 25 deriváveis + lista explícita do fora de escopo

**Trilha vigente:**
- Fonte única, CPI Canadá real
- Grão carreta × ano
- 49.248 linhas, 9.859 carretas
- Y = `custo_ano_real` (CAD/ano, dez/2025)
- Notebooks 00→08 (repositório principal)

---

## Governança de dados (atualizado 2026-07-07)

- `data/raw/fato_wo_ml...csv` removido do índice git (mantido localmente, confidencial)
- `data/raw/cpi_canada_statcan_2020_2025.csv` versionado (público, Statistics Canada)
- `.gitignore` atualizado para ignorar `data/raw/*.csv` com exceção do CPI
- `data/processed/` ignorado (regenerado pelos notebooks)

---

## Referência para continuidade

Ver [`docs/revisao_anual_2026-07-07.md`](revisao_anual_2026-07-07.md) para metodologia vigente.
