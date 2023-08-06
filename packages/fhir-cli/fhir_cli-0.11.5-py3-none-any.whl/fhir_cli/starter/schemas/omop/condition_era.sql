SELECT
    1 AS condition_era_id,
    1 AS person_id,
    0 AS condition_concept_id,
    now()::DATE AS condition_era_start_date,
    now()::DATE AS condition_era_end_date,
    1 AS condition_occurrence_count
