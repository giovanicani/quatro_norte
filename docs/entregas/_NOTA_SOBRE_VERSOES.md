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

## ✅ Entrega vigente

### `Apresentacao_QuatroNorte_Fase2.pptx` (46 slides)
- **Estado:** vigente — números da base reextraída, itens 12 a 16 da rubrica entregues
- **Estrutura:** slides 1–34 = apresentação de agosto intacta; 35–46 = bloco da Fase 2
- **Origem:** `Apresentacao_QuatroNorte_agosto.pptx` (preservado, não modificar)
- **Reprodutível:** `py notebooks/09_atualiza_apresentacao_fase2.py`

---

## 🔁 Deck paralelo — metodologia válida, números defasados

### `Apresentacao_QuatroNorte.pptx` (23 slides)
- **Estado:** Metodologia vigente; **números da base anterior** (gerado em 2026-07-07)
- **Metodologia:** Custo anual por carreta, CPI Canadá, fonte única
- **Números exibidos:** R² 0,43 (preditivo) / 0,57 (explicativo) — base de 223.590 OS
- **Por que defasou:** em 2026-08-16 a base única foi reextraída (**217.217 OS · 9.585
  carretas · 29 colunas**) e passou a incluir **dados de contrato**. O deck não reflete
  a nova base nem as hipóteses **H6/H7 (contrato)**
- **Reprodutível:** Gerado automaticamente por `notebooks/08_build_apresentacao.ipynb`
- **Ação pendente:** regenerar após a reexecução do pipeline
  (ver [`docs/revisao_contrato_2026-08-16.md`](../revisao_contrato_2026-08-16.md) §7)

---

## Como Atualizar

Para gerar um novo deck vigente:
```bash
jupyter notebook notebooks/08_build_apresentacao.ipynb
```

O arquivo `Apresentacao_QuatroNorte.pptx` será regenerado automaticamente com os números e figuras mais recentes de `reports/`.

---

**Última atualização:** 2026-08-16  
**Metodologia vigente:** Custo anual por carreta (fonte única, grão carreta × ano),
**com contrato no escopo** desde 2026-08-16

> 📌 Os arquivos marcados como históricos **não devem ser descartados**: eles são a
> evidência das tentativas anteriores exigidas pela rubrica (item 12 — resultados
> preliminares 1ª e 2ª tentativa). Ver
> [`docs/narrativa_do_projeto.md`](../narrativa_do_projeto.md).
