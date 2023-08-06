SELECT
    1 AS metadata_id,
    0 AS metadata_concept_id,
    0 AS metadata_type_concept_id,
    '' AS "name",
    '' AS value_as_string,
    0 AS value_as_concept_id,
    1.0 AS value_as_number,
    now()::DATE AS metadata_date,
    now()::TIMESTAMP AS metadata_datetime
