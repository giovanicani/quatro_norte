# Revisão Pós-Base Nova — 2026-07-07

Revisão feita após atualização dos CSVs em `data/raw/`, reconstrução das bases
processadas e geração de novos resultados em `reports/`.

## Resultado da Revisão

O projeto está coerente na trilha principal (`notebooks/02 → 04 → 03b/03c/03d
→ 05 → 06 → 08`) e os principais números foram atualizados para a nova base:

- Base mensal: **749.592** linhas carreta × mês.
- Alvo válido: **351.956** observações com `km_rodado_mes >= 500`.
- Custo interno total: **CAD 77,0 mi nominal** / **CAD 82,3 mi deflacionado**.
- Modelo recomendado: **Random Forest**.
- Desempenho teste temporal: **R² = 0,085**, **RMSE = 0,2426**, **MAE = 0,1305**.
- `id_carreta = 8441` deixou de inflar os extremos: `n_os_acum` máximo caiu de
  15.006 para 147.
- `unit_subtype` entrou como variável categórica mais relevante:
  - eta = **0,128** na EDA;
  - 2º fator na importância por permutação do Random Forest.

## Correções Aplicadas Nesta Revisão

- `reports/tables/06_hipoteses_final.csv`: H5 atualizada para refletir
  `unit_subtype` como principal variável categórica, em vez de montadora.
- `reports/sumario_executivo.md`: ranking de fatores e H5 atualizados com
  `unit_subtype`.
- `docs/GUIA_DO_PROJETO.md`: removida indicação antiga de placeholders no
  README e adicionada pendência explícita para reexecutar 00/01.
- `docs/curadoria_2026-07-07.md`: pendências atualizadas para refletir que a
  nova base já foi reexecutada e que ainda faltam features candidatas
  adicionais e reexecução de 00/01.

## Achados de Atenção

### 1. Inventário e qualidade — RESOLVIDO

As tabelas `reports/tables/00_*` e `reports/tables/01_*` **foram reexecutadas**
sobre a nova extração dos CSVs (notebooks 00 e 01, exit 0): inventário,
integridade de chaves, valores ausentes, diagnóstico de custos, odômetro e
consistência temporal estão atualizados. Isso foi possível porque neste
ambiente o interpretador `py` está disponível.

### 2. Features candidatas ainda não foram todas implementadas

As 5 novas variáveis de ativo foram integradas:

```text
tailgate_flag
unit_subtype
tire_size
suspension_type
new_used_indicator
```

Mas ainda faltam as features de recência e exposição planejadas no dicionário:

```text
custo_acum_12m
n_os_12m
n_os_3m
meses_com_os_12m
flag_os_mes_anterior
custo_mes_anterior
custo_por_km_media_6m
km_rodado_mes_lag_1m
km_rodado_media_3m
densidade_os_por_10k_km
custo_acum_por_10k_km
n_sistemas_distintos_12m
flag_reincidencia_sistema_3m
idade_x_km_acumulado
reefer_x_idade
```

### 3. HTML v2 pode estar defasado

`docs/entregas/Apresentacao_QuatroNorte_v2.html` ainda é válido na abordagem,
mas deve ser regenerado ou revisado se for circular como entrega, pois a última
rodada trouxe R² = 0,085 e `unit_subtype` como fator relevante.

### 4. Resultados grandes ainda precisam de decisão

`reports/tables/02_os_preventivas_mistas.csv` é grande para um repositório
acadêmico. Não contém necessariamente dados brutos completos, mas deve ser
avaliado antes de qualquer publicação externa.

## Próximos Passos Recomendados

1. ~~Reexecutar `notebooks/00_contexto_inventario_dados.ipynb`.~~ **Feito.**
2. ~~Reexecutar `notebooks/01_qualidade_integridade_dados.ipynb`.~~ **Feito.**
3. ~~Reexecutar `02 → 04 → 03b → 03c → 03d → 05 → 06 → 08`.~~ **Feito** (deck
   regenerado com R² 0,085 e `unit_subtype`).
4. (Opcional) Implementar o pacote de features candidatas de recência/exposição
   — não melhorou a métrica com as 5 de ativo; avaliar custo/benefício.
5. (Opcional, maior potencial) Testar agregação do alvo em grão mais grosso
   (trimestral/anual) para reduzir a zero-inflação.
6. Revisar visualmente o deck gerado.
7. Atualizar `docs/entregas/Apresentacao_QuatroNorte_v2.html` ou marcá-lo como
   histórico se não for mais usado.
