/*postgresql OMOP CDM Indices
  There are no unique indices created because it is assumed that the primary key constraints have been run prior to
  implementing indices.
*/

{% macro add_omop_indexes() %}

    {% set indexes_sql %}
        BEGIN;

        /************************
        Standardized clinical data
        ************************/

        CREATE INDEX idx_person_id  ON {{ target.schema }}_omop.person  (person_id ASC);
        CLUSTER {{ target.schema }}_omop.person  USING idx_person_id ;
        CREATE INDEX idx_gender ON {{ target.schema }}_omop.person (gender_concept_id ASC);

        CREATE INDEX idx_observation_period_id_1  ON {{ target.schema }}_omop.observation_period  (person_id ASC);
        CLUSTER {{ target.schema }}_omop.observation_period  USING idx_observation_period_id_1 ;

        CREATE INDEX idx_visit_person_id_1  ON {{ target.schema }}_omop.visit_occurrence  (person_id ASC);
        CLUSTER {{ target.schema }}_omop.visit_occurrence  USING idx_visit_person_id_1 ;
        CREATE INDEX idx_visit_concept_id_1 ON {{ target.schema }}_omop.visit_occurrence (visit_concept_id ASC);

        CREATE INDEX idx_visit_det_person_id_1  ON {{ target.schema }}_omop.visit_detail  (person_id ASC);
        CLUSTER {{ target.schema }}_omop.visit_detail  USING idx_visit_det_person_id_1 ;
        CREATE INDEX idx_visit_det_concept_id_1 ON {{ target.schema }}_omop.visit_detail (visit_detail_concept_id ASC);
        CREATE INDEX idx_visit_det_occ_id ON {{ target.schema }}_omop.visit_detail (visit_occurrence_id ASC);

        CREATE INDEX idx_condition_person_id_1  ON {{ target.schema }}_omop.condition_occurrence  (person_id ASC);
        CLUSTER {{ target.schema }}_omop.condition_occurrence  USING idx_condition_person_id_1 ;
        CREATE INDEX idx_condition_concept_id_1 ON {{ target.schema }}_omop.condition_occurrence (condition_concept_id ASC);
        CREATE INDEX idx_condition_visit_id_1 ON {{ target.schema }}_omop.condition_occurrence (visit_occurrence_id ASC);

        CREATE INDEX idx_drug_person_id_1  ON {{ target.schema }}_omop.drug_exposure  (person_id ASC);
        CLUSTER {{ target.schema }}_omop.drug_exposure  USING idx_drug_person_id_1 ;
        CREATE INDEX idx_drug_concept_id_1 ON {{ target.schema }}_omop.drug_exposure (drug_concept_id ASC);
        CREATE INDEX idx_drug_visit_id_1 ON {{ target.schema }}_omop.drug_exposure (visit_occurrence_id ASC);

        CREATE INDEX idx_procedure_person_id_1  ON {{ target.schema }}_omop.procedure_occurrence  (person_id ASC);
        CLUSTER {{ target.schema }}_omop.procedure_occurrence  USING idx_procedure_person_id_1 ;
        CREATE INDEX idx_procedure_concept_id_1 ON {{ target.schema }}_omop.procedure_occurrence (procedure_concept_id ASC);
        CREATE INDEX idx_procedure_visit_id_1 ON {{ target.schema }}_omop.procedure_occurrence (visit_occurrence_id ASC);

        CREATE INDEX idx_device_person_id_1  ON {{ target.schema }}_omop.device_exposure  (person_id ASC);
        CLUSTER {{ target.schema }}_omop.device_exposure  USING idx_device_person_id_1 ;
        CREATE INDEX idx_device_concept_id_1 ON {{ target.schema }}_omop.device_exposure (device_concept_id ASC);
        CREATE INDEX idx_device_visit_id_1 ON {{ target.schema }}_omop.device_exposure (visit_occurrence_id ASC);

        CREATE INDEX idx_measurement_person_id_1  ON {{ target.schema }}_omop.measurement  (person_id ASC);
        CLUSTER {{ target.schema }}_omop.measurement  USING idx_measurement_person_id_1 ;
        CREATE INDEX idx_measurement_concept_id_1 ON {{ target.schema }}_omop.measurement (measurement_concept_id ASC);
        CREATE INDEX idx_measurement_visit_id_1 ON {{ target.schema }}_omop.measurement (visit_occurrence_id ASC);

        CREATE INDEX idx_observation_person_id_1  ON {{ target.schema }}_omop.observation  (person_id ASC);
        CLUSTER {{ target.schema }}_omop.observation  USING idx_observation_person_id_1 ;
        CREATE INDEX idx_observation_concept_id_1 ON {{ target.schema }}_omop.observation (observation_concept_id ASC);
        CREATE INDEX idx_observation_visit_id_1 ON {{ target.schema }}_omop.observation (visit_occurrence_id ASC);

        CREATE INDEX idx_death_person_id_1  ON {{ target.schema }}_omop.death  (person_id ASC);
        CLUSTER {{ target.schema }}_omop.death  USING idx_death_person_id_1 ;

        CREATE INDEX idx_note_person_id_1  ON {{ target.schema }}_omop.note  (person_id ASC);
        CLUSTER {{ target.schema }}_omop.note  USING idx_note_person_id_1 ;
        CREATE INDEX idx_note_concept_id_1 ON {{ target.schema }}_omop.note (note_type_concept_id ASC);
        CREATE INDEX idx_note_visit_id_1 ON {{ target.schema }}_omop.note (visit_occurrence_id ASC);

        CREATE INDEX idx_note_nlp_note_id_1  ON {{ target.schema }}_omop.note_nlp  (note_id ASC);
        CLUSTER {{ target.schema }}_omop.note_nlp  USING idx_note_nlp_note_id_1 ;
        CREATE INDEX idx_note_nlp_concept_id_1 ON {{ target.schema }}_omop.note_nlp (note_nlp_concept_id ASC);

        CREATE INDEX idx_specimen_person_id_1  ON {{ target.schema }}_omop.specimen  (person_id ASC);
        CLUSTER {{ target.schema }}_omop.specimen  USING idx_specimen_person_id_1 ;
        CREATE INDEX idx_specimen_concept_id_1 ON {{ target.schema }}_omop.specimen (specimen_concept_id ASC);

        CREATE INDEX idx_fact_relationship_id1 ON {{ target.schema }}_omop.fact_relationship (domain_concept_id_1 ASC);
        CREATE INDEX idx_fact_relationship_id2 ON {{ target.schema }}_omop.fact_relationship (domain_concept_id_2 ASC);
        CREATE INDEX idx_fact_relationship_id3 ON {{ target.schema }}_omop.fact_relationship (relationship_concept_id ASC);

        /************************
        Standardized health system data
        ************************/

        CREATE INDEX idx_location_id_1  ON {{ target.schema }}_omop.location  (location_id ASC);
        CLUSTER {{ target.schema }}_omop.location  USING idx_location_id_1 ;

        CREATE INDEX idx_care_site_id_1  ON {{ target.schema }}_omop.care_site  (care_site_id ASC);
        CLUSTER {{ target.schema }}_omop.care_site  USING idx_care_site_id_1 ;

        CREATE INDEX idx_provider_id_1  ON {{ target.schema }}_omop.provider  (provider_id ASC);
        CLUSTER {{ target.schema }}_omop.provider  USING idx_provider_id_1 ;

        /************************
        Standardized health economics
        ************************/

        CREATE INDEX idx_period_person_id_1  ON {{ target.schema }}_omop.payer_plan_period  (person_id ASC);
        CLUSTER {{ target.schema }}_omop.payer_plan_period  USING idx_period_person_id_1 ;

        CREATE INDEX idx_cost_event_id  ON {{ target.schema }}_omop.cost (cost_event_id ASC);

        /************************
        Standardized derived elements
        ************************/

        CREATE INDEX idx_drug_era_person_id_1  ON {{ target.schema }}_omop.drug_era  (person_id ASC);
        CLUSTER {{ target.schema }}_omop.drug_era  USING idx_drug_era_person_id_1 ;
        CREATE INDEX idx_drug_era_concept_id_1 ON {{ target.schema }}_omop.drug_era (drug_concept_id ASC);

        CREATE INDEX idx_dose_era_person_id_1  ON {{ target.schema }}_omop.dose_era  (person_id ASC);
        CLUSTER {{ target.schema }}_omop.dose_era  USING idx_dose_era_person_id_1 ;
        CREATE INDEX idx_dose_era_concept_id_1 ON {{ target.schema }}_omop.dose_era (drug_concept_id ASC);

        CREATE INDEX idx_condition_era_person_id_1  ON {{ target.schema }}_omop.condition_era  (person_id ASC);
        CLUSTER {{ target.schema }}_omop.condition_era  USING idx_condition_era_person_id_1 ;
        CREATE INDEX idx_condition_era_concept_id_1 ON {{ target.schema }}_omop.condition_era (condition_concept_id ASC);

        /**************************
        Standardized meta-data
        ***************************/

        CREATE INDEX idx_metadata_concept_id_1  ON {{ target.schema }}_omop.metadata  (metadata_concept_id ASC);
        CLUSTER {{ target.schema }}_omop.metadata  USING idx_metadata_concept_id_1 ;

        /**************************
        Standardized vocabularies
        ***************************/

        CREATE INDEX idx_source_to_concept_map_3  ON {{ target.schema }}_omop.source_to_concept_map  (target_concept_id ASC);
        CLUSTER {{ target.schema }}_omop.source_to_concept_map  USING idx_source_to_concept_map_3 ;
        CREATE INDEX idx_source_to_concept_map_1 ON {{ target.schema }}_omop.source_to_concept_map (source_vocabulary_id ASC);
        CREATE INDEX idx_source_to_concept_map_2 ON {{ target.schema }}_omop.source_to_concept_map (target_vocabulary_id ASC);
        CREATE INDEX idx_source_to_concept_map_c ON {{ target.schema }}_omop.source_to_concept_map (source_code ASC);

        --Additional v6.0 indices

        --CREATE CLUSTERED INDEX idx_survey_person_id_1 ON {{ target.schema }}_omop.survey_conduct (person_id ASC);


        --CREATE CLUSTERED INDEX idx_episode_person_id_1 ON {{ target.schema }}_omop.episode (person_id ASC);
        --CREATE INDEX idx_episode_concept_id_1 ON {{ target.schema }}_omop.episode (episode_concept_id ASC);

        --CREATE CLUSTERED INDEX idx_episode_event_id_1 ON {{ target.schema }}_omop.episode_event (episode_id ASC);
        --CREATE INDEX idx_ee_field_concept_id_1 ON {{ target.schema }}_omop.episode_event (event_field_concept_id ASC);
        /*postgresql OMOP CDM Indices
        There are no unique indices created because it is assumed that the primary key constraints have been run prior to
          implementing indices.
        */
        COMMIT;

    {% endset %}

    {% do run_query(indexes_sql) %}

{% endmacro %}
