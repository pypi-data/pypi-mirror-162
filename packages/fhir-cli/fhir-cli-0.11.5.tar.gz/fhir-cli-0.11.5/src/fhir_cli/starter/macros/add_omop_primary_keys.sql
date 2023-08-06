--postgresql CDM Primary Key Constraints for OMOP Common Data Model 5.4

{% macro add_omop_primary_keys() %}

    {% set primary_keys_sql %}
        BEGIN;

        ALTER TABLE {{ target.schema }}_omop.PERSON ADD CONSTRAINT xpk_PERSON PRIMARY KEY (person_id);

        ALTER TABLE {{ target.schema }}_omop.OBSERVATION_PERIOD ADD CONSTRAINT xpk_OBSERVATION_PERIOD PRIMARY KEY (observation_period_id);

        ALTER TABLE {{ target.schema }}_omop.VISIT_OCCURRENCE ADD CONSTRAINT xpk_VISIT_OCCURRENCE PRIMARY KEY (visit_occurrence_id);

        ALTER TABLE {{ target.schema }}_omop.VISIT_DETAIL ADD CONSTRAINT xpk_VISIT_DETAIL PRIMARY KEY (visit_detail_id);

        ALTER TABLE {{ target.schema }}_omop.CONDITION_OCCURRENCE ADD CONSTRAINT xpk_CONDITION_OCCURRENCE PRIMARY KEY (condition_occurrence_id);

        ALTER TABLE {{ target.schema }}_omop.DRUG_EXPOSURE ADD CONSTRAINT xpk_DRUG_EXPOSURE PRIMARY KEY (drug_exposure_id);

        ALTER TABLE {{ target.schema }}_omop.PROCEDURE_OCCURRENCE ADD CONSTRAINT xpk_PROCEDURE_OCCURRENCE PRIMARY KEY (procedure_occurrence_id);

        ALTER TABLE {{ target.schema }}_omop.DEVICE_EXPOSURE ADD CONSTRAINT xpk_DEVICE_EXPOSURE PRIMARY KEY (device_exposure_id);

        ALTER TABLE {{ target.schema }}_omop.MEASUREMENT ADD CONSTRAINT xpk_MEASUREMENT PRIMARY KEY (measurement_id);

        ALTER TABLE {{ target.schema }}_omop.OBSERVATION ADD CONSTRAINT xpk_OBSERVATION PRIMARY KEY (observation_id);

        ALTER TABLE {{ target.schema }}_omop.NOTE ADD CONSTRAINT xpk_NOTE PRIMARY KEY (note_id);

        ALTER TABLE {{ target.schema }}_omop.NOTE_NLP ADD CONSTRAINT xpk_NOTE_NLP PRIMARY KEY (note_nlp_id);

        ALTER TABLE {{ target.schema }}_omop.SPECIMEN ADD CONSTRAINT xpk_SPECIMEN PRIMARY KEY (specimen_id);

        ALTER TABLE {{ target.schema }}_omop.LOCATION ADD CONSTRAINT xpk_LOCATION PRIMARY KEY (location_id);

        ALTER TABLE {{ target.schema }}_omop.CARE_SITE ADD CONSTRAINT xpk_CARE_SITE PRIMARY KEY (care_site_id);

        ALTER TABLE {{ target.schema }}_omop.PROVIDER ADD CONSTRAINT xpk_PROVIDER PRIMARY KEY (provider_id);

        ALTER TABLE {{ target.schema }}_omop.PAYER_PLAN_PERIOD ADD CONSTRAINT xpk_PAYER_PLAN_PERIOD PRIMARY KEY (payer_plan_period_id);

        ALTER TABLE {{ target.schema }}_omop.COST ADD CONSTRAINT xpk_COST PRIMARY KEY (cost_id);

        ALTER TABLE {{ target.schema }}_omop.DRUG_ERA ADD CONSTRAINT xpk_DRUG_ERA PRIMARY KEY (drug_era_id);

        ALTER TABLE {{ target.schema }}_omop.DOSE_ERA ADD CONSTRAINT xpk_DOSE_ERA PRIMARY KEY (dose_era_id);

        ALTER TABLE {{ target.schema }}_omop.CONDITION_ERA ADD CONSTRAINT xpk_CONDITION_ERA PRIMARY KEY (condition_era_id);

        ALTER TABLE {{ target.schema }}_omop.EPISODE ADD CONSTRAINT xpk_EPISODE PRIMARY KEY (episode_id);

        ALTER TABLE {{ target.schema }}_omop.METADATA ADD CONSTRAINT xpk_METADATA PRIMARY KEY (metadata_id);

        ALTER TABLE {{ target.schema }}_omop.COHORT ADD CONSTRAINT xpk_COHORT PRIMARY KEY (cohort_definition_id, subject_id, cohort_start_date, cohort_end_date);

        ALTER TABLE {{ target.schema }}_omop.COHORT_DEFINITION ADD CONSTRAINT xpk_COHORT_DEFINITION PRIMARY KEY (cohort_definition_id);

        COMMIT;
    {% endset %}

    {% do run_query(primary_keys_sql) %}

{% endmacro %}
