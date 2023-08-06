SELECT
    1::BIGINT AS episode_id,
    1 AS person_id,
    0 AS episode_concept_id,
    now()::DATE AS episode_start_date,
    now()::TIMESTAMP AS episode_start_datetime,
    now()::DATE AS episode_end_date,
    now()::TIMESTAMP AS episode_end_datetime,
    NULL::BIGINT AS episode_parent_id,
    1 AS episode_number,
    0 AS episode_object_concept_id,
    0 AS episode_type_concept_id,
    '' AS episode_source_value,
    0 AS episode_source_concept_id
