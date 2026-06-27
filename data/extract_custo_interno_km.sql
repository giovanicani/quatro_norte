-- ============================================================================
-- Extracao curada: custo de manutencao INTERNO (charge_flag='I') por KM
-- Projeto Quatro Norte / MBA - Grupo 01
--
-- Populacao analisada: carretas PROPRIAS e ATIVAS (cus_id_owner = 4,
--   active_flag = 'Y') que possuem ao menos uma leitura de odometro em KM
--   (rep_unit_readings.reading_uom = 'KM', void_flag = 'N') na janela.
-- Janela de analise: 2020-01-01 ate 2025-12-31 (filtrada pela DATA DO EVENTO:
--   wo_date nas OS, reading_date nas leituras -- NAO create_date).
-- Alvo: custo interno = linhas charge_flag='I'.
--   labour = CASE sublet_flag='Y' -> total_sublet ; senao cost_hours * hourly_cost
--   parts  = CASE labour.sublet_flag='Y' -> parts.total_sublet ; senao nvl(item_average_cost,item_cost) * actual_qty
--
-- Gera 7 CSVs em data/raw/. Executar com SQLcl:  sql user/pass@db @data/extract_custo_interno_km.sql
-- SOMENTE LEITURA.
-- ============================================================================

-- SQLcl specific settings
SET FEEDBACK OFF
SET TERMOUT OFF
SET SQLFORMAT CSV
SET HEADING ON
SET PAGESIZE 0
SET TRIMSPOOL ON

ALTER SESSION SET NLS_TIMESTAMP_TZ_FORMAT = 'YYYY-MM-DD"T"HH24:MI:SS.FF6 TZH:TZM';
ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD"T"HH24:MI:SS';
-- Forca PONTO como separador decimal (lat/long, custos): evita virgula decimal quebrando o CSV
ALTER SESSION SET NLS_NUMERIC_CHARACTERS = '.,';

-- ----------------------------------------------------------------------------
-- 1) dim_carretas  (1 linha por carreta da populacao)
-- ----------------------------------------------------------------------------
PROMPT Exporting dim_carretas
SPOOL data/raw/dim_carretas_2020-01-01_to_2025-12-31.csv

WITH frota AS (
    SELECT u.uni_id
      FROM ym_units u
     WHERE u.cus_id_owner = 4
       AND u.active_flag = 'Y'
       AND EXISTS (SELECT 1
                     FROM rep_unit_readings r
                    WHERE r.uni_id = u.uni_id
                      AND r.reading_uom = 'KM'
                      AND r.void_flag = 'N'
                      AND r.reading_date >= DATE '2020-01-01'
                      AND r.reading_date <  DATE '2026-01-01')
)
SELECT u.uni_id                AS id_carreta,
       u.description           AS descricao_carreta,
       u.serial_vin            AS chassi_vin,
       u.license_plate         AS placa,
       mk.code                 AS cod_montadora,
       md.code                 AS cod_modelo,
       u.year                  AS ano_modelo,
       u.in_service_date       AS data_entrada_servico,
       u.axles                 AS eixos,
       u.length                AS comprimento,
       CASE WHEN u.uni_id_reefer IS NOT NULL THEN 'Y' ELSE 'N' END AS flag_refrigerado,
       cl.code                 AS cod_classe,
       cl.description          AS classe,
       cl.age_from             AS idade_classe_de,
       cl.age_to               AS idade_classe_ate,
       mg.code                 AS cod_grupo_manutencao,
       mg.description          AS grupo_manutencao,
       es.description          AS status_equipamento
  FROM ym_units u
  JOIN frota f                         ON f.uni_id = u.uni_id
  LEFT JOIN ym_unit_makes mk           ON mk.unimak_id = u.unimak_id
  LEFT JOIN rla_unit_models md         ON md.unimod_id = u.unimod_id
  LEFT JOIN adm_unit_classification cl ON cl.unicla_id = u.unicla_id
  LEFT JOIN pm_maintenance_groups mg   ON mg.maigro_id = u.maigro_id
  LEFT JOIN adm_equipment_status es    ON es.equsta_id = u.equsta_id;

SPOOL OFF

-- ----------------------------------------------------------------------------
-- 2) fato_readings  (serie de odometro KM por carreta)
-- ----------------------------------------------------------------------------
PROMPT Exporting fato_readings
SPOOL data/raw/fato_readings_2020-01-01_to_2025-12-31.csv

WITH frota AS (
    SELECT u.uni_id
      FROM ym_units u
     WHERE u.cus_id_owner = 4
       AND u.active_flag = 'Y'
       AND EXISTS (SELECT 1 FROM rep_unit_readings r
                    WHERE r.uni_id = u.uni_id
                      AND r.reading_uom = 'KM' AND r.void_flag = 'N'
                      AND r.reading_date >= DATE '2020-01-01'
                      AND r.reading_date <  DATE '2026-01-01')
)
SELECT r.unirea_id        AS id_leitura,
       r.uni_id           AS id_carreta,
       CAST(r.reading_date AS DATE) AS data_leitura,
       r.reading          AS km_acumulado,
       r.reading_uom      AS unidade_leitura,
       r.reset_reading_at AS km_reset_em,
       r.reset_reading_to AS km_reset_para,
       r.worord_id        AS id_os
  FROM rep_unit_readings r
  JOIN frota f ON f.uni_id = r.uni_id
 WHERE r.reading_uom = 'KM'
   AND r.void_flag = 'N'
   AND r.reading_date >= DATE '2020-01-01'
   AND r.reading_date <  DATE '2026-01-01'
 ORDER BY r.uni_id, r.reading_date;

SPOOL OFF

-- ----------------------------------------------------------------------------
-- 3) fato_wo  (cabecalho das ordens de servico)
-- ----------------------------------------------------------------------------
PROMPT Exporting fato_wo
SPOOL data/raw/fato_wo_2020-01-01_to_2025-12-31.csv

WITH frota AS (
    SELECT u.uni_id
      FROM ym_units u
     WHERE u.cus_id_owner = 4
       AND u.active_flag = 'Y'
       AND EXISTS (SELECT 1 FROM rep_unit_readings r
                    WHERE r.uni_id = u.uni_id
                      AND r.reading_uom = 'KM' AND r.void_flag = 'N'
                      AND r.reading_date >= DATE '2020-01-01'
                      AND r.reading_date <  DATE '2026-01-01')
)
SELECT w.worord_id        AS id_os,
       w.uni_id           AS id_carreta,
       w.wo_number        AS numero_os,
       CAST(w.wo_date AS DATE)        AS data_os,
       w.repair_request   AS solicitacao_reparo,
       loc.code           AS cod_local_os,
       loc.description    AS local_os,
       w.wo_location      AS endereco_os,
       ps.code            AS cod_provincia_estado,
       ps.name            AS provincia_estado,
       (SELECT nvl(round(SUM(CASE WHEN l.sublet_flag = 'Y'
                                  THEN nvl(l.total_sublet, 0)
                                  ELSE nvl(l.cost_hours, 0) * nvl(l.hourly_cost, 0)
                             END), 2), 0)
          FROM rep_work_order_labour l
         WHERE l.worord_id = w.worord_id
           AND l.charge_flag = 'I'
           AND l.deleted_flag = 'N')  AS total_interno_mao_obra,
       (SELECT nvl(round(SUM(CASE WHEN l.sublet_flag = 'Y'
                                  THEN nvl(p.total_sublet, 0)
                                  ELSE nvl(nvl(p.item_average_cost, p.item_cost), 0) * nvl(p.actual_qty, 0)
                             END), 2), 0)
          FROM rep_work_order_parts p
          JOIN rep_work_order_labour l ON l.worordlab_id = p.worordlab_id
         WHERE l.worord_id = w.worord_id
           AND p.charge_flag = 'I'
           AND p.deleted_flag = 'N')  AS total_interno_pecas
  FROM rep_work_orders w
  JOIN frota f ON f.uni_id = w.uni_id
  LEFT JOIN rla_locations loc       ON loc.loc_id = w.loc_id
  LEFT JOIN adm_province_states ps  ON ps.prosta_id = w.prosta_id_repair
 WHERE w.void_date IS NULL
   AND w.approved_date IS NOT NULL
   AND w.completed_date IS NOT NULL
   AND w.wo_date >= DATE '2020-01-01'
   AND w.wo_date <  DATE '2026-01-01'
   AND (EXISTS (SELECT 1
                  FROM rep_work_order_labour l
                 WHERE l.worord_id = w.worord_id
                   AND l.charge_flag = 'I'
                   AND l.deleted_flag = 'N')
     OR EXISTS (SELECT 1
                  FROM rep_work_order_parts p
                  JOIN rep_work_order_labour l ON l.worordlab_id = p.worordlab_id
                 WHERE l.worord_id = w.worord_id
                   AND p.charge_flag = 'I'
                   AND p.deleted_flag = 'N'));

SPOOL OFF

-- ----------------------------------------------------------------------------
-- 4) fato_wo_labour  (mao de obra interna; internal_labour_cost = cost_hours*hourly_cost)
-- ----------------------------------------------------------------------------
PROMPT Exporting fato_wo_labour
SPOOL data/raw/fato_wo_labour_2020-01-01_to_2025-12-31.csv

WITH frota AS (
    SELECT u.uni_id
      FROM ym_units u
     WHERE u.cus_id_owner = 4
       AND u.active_flag = 'Y'
       AND EXISTS (SELECT 1 FROM rep_unit_readings r
                    WHERE r.uni_id = u.uni_id
                      AND r.reading_uom = 'KM' AND r.void_flag = 'N'
                      AND r.reading_date >= DATE '2020-01-01'
                      AND r.reading_date <  DATE '2026-01-01')
)
SELECT l.worordlab_id     AS id_linha_mao_obra,
       l.worord_id        AS id_os,
       w.uni_id           AS id_carreta,
       CAST(w.wo_date AS DATE) AS data_os,
       jt.code            AS cod_tipo_servico,
       l.cost_hours       AS horas_custo,
       l.hourly_cost      AS custo_hora,
       round(CASE WHEN l.sublet_flag = 'Y'
                  THEN nvl(l.total_sublet, 0)
                  ELSE nvl(l.cost_hours, 0) * nvl(l.hourly_cost, 0)
             END, 2) AS custo_interno_mao_obra,
       l.total_sublet     AS total_terceirizado,
       l.sublet_flag      AS flag_terceirizado,
       s.code             AS cod_sistema_vmrs,
       s.description      AS sistema_vmrs
  FROM rep_work_order_labour l
  JOIN rep_work_orders w     ON w.worord_id = l.worord_id
  JOIN frota f               ON f.uni_id = w.uni_id
  LEFT JOIN adm_job_types jt ON jt.jobtyp_id = l.jobtyp_id
  LEFT JOIN pm_vmrs_system_assemblies sa ON sa.vmrsysass_id = l.vmrsysass_id
  LEFT JOIN pm_vmrs_systems s            ON s.vmrsys_id = sa.vmrsys_id
 WHERE l.charge_flag = 'I'
   AND l.deleted_flag = 'N'
   AND w.void_date IS NULL
   AND w.approved_date IS NOT NULL
   AND w.completed_date IS NOT NULL
   AND w.wo_date >= DATE '2020-01-01'
   AND w.wo_date <  DATE '2026-01-01';

SPOOL OFF

-- ----------------------------------------------------------------------------
-- 5) fato_wo_parts  (pecas internas; internal_part_cost = nvl(item_average_cost,item_cost)*actual_qty)
-- ----------------------------------------------------------------------------
PROMPT Exporting fato_wo_parts
SPOOL data/raw/fato_wo_parts_2020-01-01_to_2025-12-31.csv

WITH frota AS (
    SELECT u.uni_id
      FROM ym_units u
     WHERE u.cus_id_owner = 4
       AND u.active_flag = 'Y'
       AND EXISTS (SELECT 1 FROM rep_unit_readings r
                    WHERE r.uni_id = u.uni_id
                      AND r.reading_uom = 'KM' AND r.void_flag = 'N'
                      AND r.reading_date >= DATE '2020-01-01'
                      AND r.reading_date <  DATE '2026-01-01')
)
SELECT p.worordpar_id      AS id_linha_peca,
       w.worord_id        AS id_os,
       w.uni_id           AS id_carreta,
       CAST(w.wo_date AS DATE) AS data_os,
       p.par_id           AS id_peca,
       ip.code            AS numero_peca,
       ip.description     AS descricao_peca,
       p.actual_qty       AS qtd_real,
       p.item_cost        AS custo_item,
       p.item_average_cost AS custo_medio_item,
       round(CASE WHEN l.sublet_flag = 'Y'
                  THEN nvl(p.total_sublet, 0)
                  ELSE nvl(nvl(p.item_average_cost, p.item_cost), 0) * nvl(p.actual_qty, 0)
             END, 2) AS custo_interno_peca,
       l.sublet_flag      AS flag_terceirizado,
       p.warranty_flag    AS flag_garantia
  FROM rep_work_order_parts p
  JOIN rep_work_order_labour l ON l.worordlab_id = p.worordlab_id
  JOIN rep_work_orders w       ON w.worord_id = l.worord_id
  JOIN frota f                 ON f.uni_id = w.uni_id
  LEFT JOIN inv_parts ip       ON ip.par_id = p.par_id
 WHERE p.charge_flag = 'I'
   AND p.deleted_flag = 'N'
   AND w.void_date IS NULL
   AND w.approved_date IS NOT NULL
   AND w.completed_date IS NOT NULL
   AND w.wo_date >= DATE '2020-01-01'
   AND w.wo_date <  DATE '2026-01-01';

SPOOL OFF

-- ----------------------------------------------------------------------------
-- 6) fato_contratos  (contratos de leasing/rental por carreta)
-- ----------------------------------------------------------------------------
PROMPT Exporting fato_contratos
SPOOL data/raw/fato_contratos_2020-01-01_to_2025-12-31.csv

WITH frota AS (
    SELECT u.uni_id
      FROM ym_units u
     WHERE u.cus_id_owner = 4
       AND u.active_flag = 'Y'
       AND EXISTS (SELECT 1 FROM rep_unit_readings r
                    WHERE r.uni_id = u.uni_id
                      AND r.reading_uom = 'KM' AND r.void_flag = 'N'
                      AND r.reading_date >= DATE '2020-01-01'
                      AND r.reading_date <  DATE '2026-01-01')
)
SELECT lra.learenass_id           AS id_contrato_carreta,
       lra.uni_id                 AS id_carreta,
       lra.agreement_type         AS tipo_contrato,
       lra.maint_type             AS tipo_manutencao,
       lra.cus_id_invoice_to      AS id_cliente,
       cus.code                   AS cod_cliente,
       CAST(lra.start_date AS DATE)  AS data_inicio,
       CAST(lra.return_date AS DATE) AS data_fim,
       lra.monthly_km_allowance   AS franquia_km_mensal,
       loc.code                   AS cod_local_contrato
  FROM rla_lease_rental_assets lra
  JOIN frota f               ON f.uni_id = lra.uni_id
  LEFT JOIN ym_customers cus ON cus.cus_id = lra.cus_id_invoice_to
  LEFT JOIN rla_locations loc ON loc.loc_id = lra.loc_id_revenue
 WHERE lra.void_date IS NULL;

SPOOL OFF

-- ----------------------------------------------------------------------------
-- 7) fato_gps  (posicoes GPS bewhere -- 1 ponto por carreta por dia)
--    Ligacao: ym_units.bewbea_id = tlm_bewhere_beacon_activity.id (id do beacon)
--    TIMESTAMP e epoch Unix -> convertido por system_functions_pkg.unix_time_to_timestamp.
--    Mantem o ULTIMO ponto de cada dia (ROW_NUMBER por carreta+dia, timestamp desc).
-- ----------------------------------------------------------------------------
PROMPT Exporting fato_gps
SPOOL data/raw/fato_gps_2020-01-01_to_2025-12-31.csv

WITH frota AS (
    SELECT u.uni_id, u.bewbea_id
      FROM ym_units u
     WHERE u.cus_id_owner = 4
       AND u.active_flag = 'Y'
       AND u.bewbea_id IS NOT NULL
       AND EXISTS (SELECT 1 FROM rep_unit_readings r
                    WHERE r.uni_id = u.uni_id
                      AND r.reading_uom = 'KM' AND r.void_flag = 'N'
                      AND r.reading_date >= DATE '2020-01-01'
                      AND r.reading_date <  DATE '2026-01-01')
),
pos AS (
    SELECT f.uni_id          AS uni_id,
           bba.id            AS beacon_id,
           bba.latitude,
           bba.longitude,
           bba.speed,
           bba.address,
           bba.timestamp     AS ts_epoch,
           CAST(system_functions_pkg.unix_time_to_timestamp(p_unix_epoch_time => bba.timestamp) AT LOCAL AS DATE) AS ts_local
      FROM tlm_bewhere_beacon_activity bba
      JOIN frota f ON f.bewbea_id = bba.id
     WHERE bba.latitude IS NOT NULL
       AND bba.longitude IS NOT NULL
),
pos_dia AS (
    SELECT pos.*,
           ROW_NUMBER() OVER (PARTITION BY pos.uni_id, TRUNC(pos.ts_local)
                              ORDER BY pos.ts_epoch DESC) AS rn
      FROM pos
     WHERE pos.ts_local >= DATE '2020-01-01'
       AND pos.ts_local <  DATE '2026-01-01'
)
SELECT uni_id        AS id_carreta,
       beacon_id     AS id_beacon,
       ts_local      AS data_hora_gps,
       TO_CHAR(latitude,  'TM9', 'NLS_NUMERIC_CHARACTERS=''.,''') AS latitude,
       TO_CHAR(longitude, 'TM9', 'NLS_NUMERIC_CHARACTERS=''.,''') AS longitude,
       speed         AS velocidade,
       address       AS endereco
  FROM pos_dia
 WHERE rn = 1
 ORDER BY uni_id, data_hora_gps;

SPOOL OFF
