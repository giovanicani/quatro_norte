# Revisao do feedback metodologico

Data da revisao: 2026-06-28

## Veredito

Os pontos de `Ajustes.md` fazem sentido e foram incorporados. A principal
mudanca foi remover vazamento temporal em `meses_desde_ultima_os` e defasar
`km_acumulado`. Com isso, os numeros antigos (`R2 = 0,242` e `AUC = 0,938`)
devem ser descartados: eles estavam inflados por informacao do proprio mes
previsto.

## Pontos ja implementados e mantidos

1. **Alvo preventivo vs. custo interno total**  
   O alvo principal e `custo_manutencao_preventiva_por_km`, aproximado por
   linhas de mao de obra com VMRS `PM`/`PREVENTIVE` e pecas de OS com linha
   preventiva. O custo interno total permanece como alvo secundario.

2. **`tipo_manutencao` como confundidor**  
   `MAINT` continua sendo a populacao principal de modelagem. `NET`/`MIX`
   permanecem em diagnosticos, EDA comparativa e caveats.

3. **Meses com custo zero**  
   Meses com km valido e custo preventivo zero foram mantidos porque representam
   custo esperado mensal para orcamento. A proporcao de zeros e reportada.

4. **Piso de quilometragem**  
   Foi mantido o piso de `500 km/mes` para calcular alvos por km e evitar
   explosoes artificiais de custo/km.

5. **Features contratuais e operacionais**  
   `duracao_contrato_meses`, `idade_contrato_meses_no_mes` e `regiao_operacao`
   foram mantidas. `prop_pecas_garantia` segue como diagnostico, mas foi
   removida da modelagem principal por quase nao haver registros de garantia.

6. **Validacao temporal e modelos**  
   O Notebook 05 mantem split temporal, validacao temporal expansiva, modelos
   diretos, benchmark KNN amostral, modelo hurdle e alvo-espelho de mao de obra.

7. **MERF / modelos hierarquicos**  
   Mixed-Effects Random Forest permanece como extensao futura recomendada, nao
   como modelo executavel desta versao.

## Ajustes criticos implementados de `Ajustes.md`

1. **C1 - Vazamento em `meses_desde_ultima_os`**  
   Corrigido no Notebook 02. A feature agora considera apenas OS anteriores ao
   mes previsto; a validacao da base mostra `meses_desde_ultima_os_zero = 0`.
   Isso removeu o atalho que identificava meses com custo preventivo positivo.

2. **C1 relacionado - `km_acumulado` contemporaneo**  
   Corrigido no Notebook 02. `km_acumulado` passou a ser defasado para refletir
   informacao disponivel ate o mes anterior. `km_acumulado_fim_mes` foi mantido
   como coluna de auditoria, nao como feature principal.

3. **C2 - Hipoteses sobre alvo zero-inflado**  
   Corrigido no Notebook 03. A EDA agora separa ocorrencia de custo e magnitude
   condicional nos meses positivos, evitando concluir ausencia de relacao apenas
   porque cerca de 80% dos meses tem custo zero.

4. **C3 - Populacao da EDA desalinhada com a modelagem**  
   Corrigido no Notebook 03. A EDA principal usa `MAINT`, alinhada ao Notebook
   05. A comparacao por `tipo_manutencao` e preservada como analise separada da
   base completa.

5. **I1 - Contradicao entre recomendacoes e hipoteses**  
   Corrigido no Notebook 06 e no sumario executivo. As recomendacoes agora
   diferenciam achados suportados, parcialmente suportados e nao suportados.

6. **I2 - Ranking de fatores**  
   Corrigido no Notebook 05/06. O ranking final prioriza permutation importance
   calculada no teste temporal. A importancia impurity-based da Random Forest
   continua salva como diagnostico secundario.

7. **I3 - `prop_pecas_garantia` quase constante**  
   Corrigido no Notebook 05. A feature foi removida da modelagem principal e
   registrada em `reports/tables/05_features_removidas_modelagem.csv`; apenas
   `0,029%` dos meses de modelagem tinham alguma peca em garantia.

8. **I4 - Bug latente no melhor modelo quando o hurdle vence**  
   Corrigido no Notebook 05. A selecao do modelo recomendado agora trata o caso
   em que o melhor resultado venha de uma entrada que nao esta no dicionario de
   pipelines diretos.

9. **M1 - Contratos iniciados apos 2025**  
   Corrigido no Notebook 02. Contratos sem sobreposicao com a janela analitica
   sao filtrados, em vez de serem clipados para dezembro de 2025.

10. **M2 - Medianas coladas no zero**  
    Corrigido no Notebook 03. As series temporais e tabelas de segmento passam
    a incluir media e mediana condicional ao positivo.

## Resultados apos a correcao

- Base mensal: `749.664` linhas, `64` colunas.
- Base deflacionada: `749.664` linhas, `76` colunas.
- Observacoes com alvo preventivo valido: `352.066`.
- Observacoes `MAINT` usadas na modelagem principal: `332.756`.
- Share de meses modelados com custo preventivo zero: `79,8%`.
- OS preventivas mistas: `85,3%` das OS com linha preventiva tambem possuem
  linhas nao preventivas.
- Custo interno reconciliado: `78.996.520,64`.
- Custo preventivo identificado: `24.833.687,14`.
- Modelo recomendado: Random Forest.
- Metricas do teste temporal: `R2 = 0,063`, `RMSE = 0,0962`, `MAE = 0,0464`.
- Hurdle: `ROC AUC = 0,680`, `average precision = 0,333`, `RMSE esperado = 0,1013`.
- Alvo-espelho de mao de obra preventiva: `R2 = 0,082`, contra `R2 = 0,063`
  no alvo preventivo total (`delta R2 = 0,019`).

## Segunda revisao de `Ajustes.md`

Os novos achados N1, N2 e N3 tambem foram incorporados.

1. **N1 - Alvo-espelho com ganho marginal**  
   Corrigido no Notebook 06. O sumario executivo agora trata o alvo de mao de
   obra como apenas marginalmente mais previsivel (`delta R2 = 0,019`), uma
   evidencia sugestiva, nao conclusiva, de ruido adicional nas pecas.

2. **N2 - Historico de manutencoes**  
   Corrigido no Notebook 03. A hipotese deixou de depender apenas de
   `custo_preventivo_acum` e passou a avaliar multiplos proxies historicos.
   Com isso, a hipotese foi reclassificada como `parcialmente suportada`. A nova
   tabela `reports/tables/03_historico_manutencao_proxies.csv` documenta as
   correlacoes por proxy.

3. **N3 - Razao por `tipo_manutencao`**  
   Corrigido no Notebook 03 e no sumario. A razao da base completa deixou de ser
   interpretada como tamanho de efeito; agora aparece apenas como caveat
   estrutural de `NET`/`MIX`.

4. **I4 - Guarda do melhor modelo**  
   Confirmado e corrigido no Notebook 05. `05_modelo_recomendado.csv` agora
   registra `pipeline_direto_disponivel`, evitando assumir que todo modelo
   elegivel esta no dicionario de pipelines diretos.

## Leitura metodologica atual

Depois da remocao do vazamento, a capacidade preditiva ficou menor, mas mais
honesta. A entrega deve enfatizar que o modelo apoia planejamento e priorizacao,
nao previsao pontual precisa de custo por km.

O hurdle continua util, mas como decomposicao do problema: ha sinal moderado
para ocorrencia de custo; a magnitude continua ruidosa, especialmente porque as
pecas preventivas sao alocadas no nivel da OS.

O alvo-espelho de mao de obra mostra ganho de `R2` pequeno (`+0,019`), portanto
deve ser lido como evidencia sugestiva, nao conclusiva, de ruido de medicao nas
pecas. `RMSE` e `MAE` devem ser tratados apenas como contexto porque o alvo de
mao de obra tem escala menor que o alvo total com pecas.

## Caveats principais

- A classificacao preventiva e uma aproximacao operacional baseada em VMRS.
- O CSV de pecas nao traz o vinculo direto com a linha de mao de obra; pecas
  preventivas sao alocadas no nivel da OS.
- A modelagem principal se aplica a contratos `MAINT`; conclusoes para
  `NET`/`MIX` devem ser tratadas separadamente.
- A distribuicao e zero-inflada; a mediana geral do alvo segue em zero.
- `km_rodado_mes` e denominador do alvo por km e tambem feature operacional;
  sua interpretacao deve ser cuidadosa.
- A razao por `tipo_manutencao` na base completa e caveat estrutural de
  `NET`/`MIX`, nao tamanho de efeito contratual.
- O ranking de fatores da Random Forest nao deve ser apresentado como ranking
  global da frota inteira.
