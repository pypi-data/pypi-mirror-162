SELECT
    1 AS observation_period_id,
    1 AS person_id,
    now()::DATE AS observation_period_start_date,
    now():: DATE AS observation_period_end_date,
    0 AS period_type_concept_id
