SELECT
    1 AS provider_id,
    '' AS provider_name,
    '' AS npi,
    '' AS dea,
    0 AS specialty_concept_id,
    1 AS care_site_id,
    0 AS gender_concept_id,
    '' AS provider_source_value,
    '' AS specialty_source_value,
    0 AS specialty_source_concept_id,
    '' AS gender_source_value,
    0 AS gender_source_concept_id,
    to_char(now(), 'YYYY')::int AS year_of_birth
