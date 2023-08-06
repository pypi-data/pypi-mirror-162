SELECT
    '' AS source_code,
    0 AS source_concept_id,
    'CDM' AS source_vocabulary_id,
    '' AS source_code_description,
    0 AS target_concept_id,
    'CDM' AS target_vocabulary_id,
    now()::DATE AS valid_start_date,
    now()::DATE AS valid_end_date,
    '' AS invalid_reason
