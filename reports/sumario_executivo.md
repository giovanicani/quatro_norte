# Sumário executivo — Projeto Quatro Norte

## Resposta ao problema

A partir da base consolidada única de ordens de serviço (`fato_wo_ml`), modelou-se o
**custo anual de manutenção por carreta** (CAD/ano), em valores **reais** corrigidos
pelo CPI do Canadá (base dez/2025), no grão **carreta × ano**. O grão anual praticamente
elimina a zero-inflação do grão mensal (de ~67% para ~3,2% de observações com custo
zero) e revela associações muito mais fortes entre as variáveis e o custo.

O custo anual real por carreta cresceu de forma consistente entre 2020 e 2025 (+52% em
termos reais, já sem inflação), e é explicado principalmente por **refrigeração**,
**histórico de manutenção** (número e custo de OS de anos anteriores) e **uso
acumulado/quilometragem**. A idade isolada tem efeito direto fraco.

## Desempenho preditivo

Split **temporal**: treino 2020–2024, teste 2025. Dois cenários de variáveis:

| Cenário | Modelo recomendado | R² | RMSE | MAE |
|---|---|---|---|---|
| Explicativo (inclui uso do ano) | Gradient Boosting | 0,572 | 1.753 | 895 |
| **Preditivo** (só atributos + histórico defasado) | **Random Forest** | **0,429** | **2.026** | **1.064** |

- Métricas em **CAD/ano** (valores reais).
- Modelos de árvore/ensemble superam claramente os lineares (que têm R² < 0 no teste,
  por causa das caudas extremas do custo). Coerente com a literatura de estimativa de
  custo de manutenção em veículos pesados.
- **O cenário preditivo é o recomendado para orçamento anual:** usa apenas informação
  conhecida no **início do ano** (atributos do ativo + histórico de anos anteriores).
  Exclui variáveis do ano em progresso (`km_rodado_ano`, `n_sistemas_vmrs_distintos_ano`,
  `share_pm_ano`, `vmrs_predominante_ano`) para evitar vazamento temporal. O cenário
  explicativo mede o **teto** de associação ao incluir o uso do ano — útil para
  compreensão, mas não para previsão operacional.

## Principais fatores do modelo

Importância por permutação (cenário preditivo, Random Forest, teste 2025):

- `flag_refrigerado`: 0,221 (dominante)
- `n_os_ano_anterior`: 0,115
- `km_acumulado_inicio_ano`: 0,072
- `custo_ano_anterior`: 0,066
- `custo_acum_ate_ano_anterior`: 0,065
- `n_os_acum_ate_ano_anterior`: 0,059
- `idade_carreta`: 0,032
- `unit_subtype`: 0,031

## Hipóteses avaliadas

- **H1 — Idade eleva o custo anual:** não suportada (Spearman `idade_carreta` = 0,018;
  efeito direto fraco).
- **H2 — Uso/quilometragem eleva o custo:** suportada (`km_rodado_ano` ρ = 0,530;
  `km_acumulado_fim_ano` ρ = 0,428).
- **H3 — Histórico prevê o custo futuro:** suportada (`n_os_ano_anterior` ρ = 0,540;
  `custo_ano_anterior` ρ = 0,536).
- **H4 — Características do ativo influenciam o custo:** suportada (`unit_subtype`
  eta = 0,55; `flag_refrigerado` eta = 0,43; `cod_montadora` eta = 0,24).
- **H5 — Região/operação influencia o custo:** parcial (efeito fraco; província
  eta = 0,14; região eta = 0,08).
- **Contrato:** fora de escopo — variáveis de contrato ausentes na fonte única.

## Recomendações

- **Orçamento:** usar o custo anual real por carreta como base; projetar o próximo ano
  com o modelo preditivo, comunicando o desempenho (R² ≈ 0,43) como apoio à decisão.
- **Priorização de frota:** priorizar carretas com maior histórico de manutenção (OS e
  custo de anos anteriores) e refrigeradas, que concentram custos anuais mais altos.
- **Perfil de ativo:** monitorar subtipos e montadoras com maior custo anual observado.
- **Uso:** incorporar quilometragem esperada ao planejamento — uso é dos maiores
  associados ao custo anual.
- **Dados:** integrar contrato, mão de obra e peças em etapa futura para ampliar o
  conjunto explicativo além da fonte única atual.
- **Modelagem futura:** avaliar Mixed-Effects Random Forest para representar
  explicitamente o efeito de grupos de ativos (montadora/subtipo).

## Limitações

- **Fonte única:** sem dados de contrato, mão de obra detalhada e peças — reduz o
  conjunto explicativo e coloca hipóteses de contrato fora de escopo.
- **Sem filtro por tipo de manutenção (MAINT):** analisa-se todo o custo interno.
- `n_os_ano` e `custo_medio_por_os_ano` são componentes aritméticos de Y e foram
  excluídos como explicadores.
- **Quilometragem** derivada do odômetro nas OS; resets/ruído tratados por regra, com
  aproximação.
- **Província** parcial (~54%); região usada como proxy geográfica.
- **Estornos** (custos negativos) excluídos; o span ativo assume presença da carreta
  entre a primeira e a última OS.
- O modelo é apoio à decisão, não substituto de validação operacional.
