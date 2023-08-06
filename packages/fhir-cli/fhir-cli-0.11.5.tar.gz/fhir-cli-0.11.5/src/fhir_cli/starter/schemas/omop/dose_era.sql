SELECT
    1 AS dose_era_id,
    1 AS person_id,
    0 AS drug_concept_id,
    0 AS unit_concept_id,
    1.0 AS dose_value,
    now()::DATE AS dose_era_start_date,
    now()::DATE AS dose_era_end_date
