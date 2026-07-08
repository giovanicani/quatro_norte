# Entregas — Apresentações Acadêmicas

## Deck Vigente

**`Apresentacao_QuatroNorte.pptx`** (23 slides)

- Grão: **carreta × ano**
- Alvo: **custo anual de manutenção** (CAD/ano, real dez/2025)
- Metodologia: fonte única `fato_wo_ml`, CPI Canadá, split temporal
- **Reprodutível:** gerado automaticamente por `notebooks/08_build_apresentacao.ipynb` a partir de tabelas e figuras em `reports/`
- Desempenho: RF preditivo R² 0,43; GB explicativo R² 0,57
- Atualizado: 2026-07-07

> Para regenerar: execute `notebooks/08_build_apresentacao.ipynb`

---

## Arquivos Históricos

### `Apresentacao_QuatroNorte_v2.pptx`

- Grão: carreta × mês (fase anterior)
- Alvo: custo por km
- **Não é reprodutível** (criado manualmente)
- Desempenho histórico: RF R² 0,085
- Referência: evolução metodológica

### `Apresentacao_QuatroNorte_v2.html`

- Relatório web (fase anterior, por km)
- **Não é reprodutível** (edição manual)
- Referência: visualização da fase mensal
- Atualizado in-place em 2026-07-07 para a metodologia anual (teste — não é a trilha oficial)

---

## Convenção

- Use `Apresentacao_QuatroNorte.pptx` para apresentações finais
- `v2.*` são referências históricas de evolução metodológica
