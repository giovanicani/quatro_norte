# Entregas — Apresentações Acadêmicas

> ⚠️ **IMPORTANTE:** Ver [`_NOTA_SOBRE_VERSOES.md`](_NOTA_SOBRE_VERSOES.md) para status de cada arquivo.

## ✅ Entrega Vigente

**`Apresentacao_QuatroNorte.pptx`** (23 slides)

- Grão: **carreta × ano**
- Alvo: **custo anual de manutenção** (CAD/ano, real dez/2025)
- Metodologia: fonte única `fato_wo_ml`, CPI Canadá, split temporal
- **Reprodutível:** gerado automaticamente por `notebooks/08_build_apresentacao.ipynb` a partir de tabelas e figuras em `reports/`
- Desempenho: RF preditivo R² 0,43; GB explicativo R² 0,57
- Atualizado: 2026-07-07

> Para regenerar: execute `notebooks/08_build_apresentacao.ipynb`

---

## 🕓 Arquivos Históricos (Desatualizados)

### `Apresentacao_QuatroNorte_v2.pptx`

- **Estado:** ❌ Desatualizado (fase anterior: custo por km, grão mensal)
- Grão: carreta × mês
- Alvo: custo por km
- Desempenho histórico: RF R² 0,085
- **Motivo:** Criação manual; não foi atualizado para a metodologia anual
- **Uso:** Referência de evolução metodológica apenas

### `Apresentacao_QuatroNorte_v2.html`

- **Estado:** ❌ Desatualizado (fase anterior: custo por km, grão mensal)
- Relatório web (página única)
- **Motivo:** Edição manual; não foi atualizado para a metodologia anual
- **Uso:** Referência de evolução metodológica apenas

---

## 📋 Recomendação

- ✅ Use **`Apresentacao_QuatroNorte.pptx`** para apresentações, entregas e compartilhamento
- 🕓 Ignore `v2.*` — são apenas referência histórica de como o projeto evoluiu

Ver [`_NOTA_SOBRE_VERSOES.md`](_NOTA_SOBRE_VERSOES.md) para detalhes completos.
