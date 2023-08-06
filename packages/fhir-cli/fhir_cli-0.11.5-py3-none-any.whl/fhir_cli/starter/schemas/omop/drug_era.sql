SELECT
    1 AS drug_era_id,
    1 AS person_id,
    0 AS drug_concept_id,
    now()::DATE AS drug_era_start_date,
    now()::DATE AS drug_era_end_date,
    1 AS drug_exposure_count,
    1 AS gap_days
