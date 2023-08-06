SELECT
    1 AS cohort_definition_id,
    '' AS cohort_definition_name,
    '' AS cohort_definition_description,
    0 AS definition_type_concept_id,
    '' AS cohort_definition_syntax,
    0 AS subject_concept_id,
    now()::DATE AS cohort_initiation_date
