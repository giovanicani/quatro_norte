# Status dos Arquivos de Entrega

## ⚠️ Atenção: Versões Desatualizadas

Os arquivos listados abaixo **não foram atualizados** para a metodologia anual vigente (revisão 2026-07-07):

### `Apresentacao_QuatroNorte_v2.pptx`
- **Estado:** Desatualizado (fase anterior: custo por km, grão mensal)
- **Métodos obsoletos:** IPCA/Brasil, grão carreta × mês, R² 0,085
- **Motivo:** Criação manual (sem gerador automático)
- **Uso:** Apenas referência histórica de evolução metodológica

### `Apresentacao_QuatroNorte_v2.html`
- **Estado:** Desatualizado (fase anterior: custo por km, grão mensal)
- **Métodos obsoletos:** Alvo por km, população MAINT, ~67% zero-inflação
- **Motivo:** Edição manual (sem gerador automático)
- **Uso:** Apenas referência histórica de evolução metodológica

---

## ✅ Arquivos Vigentes

### `Apresentacao_QuatroNorte.pptx` (23 slides)
- **Estado:** Vigente e atualizado
- **Metodologia:** Custo anual por carreta, CPI Canadá, fonte única
- **Números reais:** R² 0,43 (preditivo) / 0,57 (explicativo)
- **Reprodutível:** Gerado automaticamente por `notebooks/08_build_apresentacao.ipynb`
- **Atualização:** Automática a cada execução do pipeline

---

## Como Atualizar

Para gerar um novo deck vigente:
```bash
jupyter notebook notebooks/08_build_apresentacao.ipynb
```

O arquivo `Apresentacao_QuatroNorte.pptx` será regenerado automaticamente com os números e figuras mais recentes de `reports/`.

---

**Última atualização:** 2026-07-07  
**Metodologia vigente:** Custo anual por carreta (fonte única, grão carreta × ano)
