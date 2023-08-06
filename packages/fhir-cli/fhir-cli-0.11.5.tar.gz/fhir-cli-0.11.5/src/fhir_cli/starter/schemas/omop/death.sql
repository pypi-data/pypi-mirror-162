SELECT
    1 AS person_id,
    now()::DATE AS death_date,
    now()::TIMESTAMP AS death_datetime,
    0 AS death_type_concept_id,
    0 AS cause_concept_id,
    '' AS cause_source_value,
    0 AS cause_source_concept_id
