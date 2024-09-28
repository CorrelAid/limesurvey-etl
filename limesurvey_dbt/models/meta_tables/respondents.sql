{{
    config(
        materialized='incremental',
        unique_key='respondent_id'
    )
}}

SELECT
    id AS respondent_id
FROM {{ source(env_var('TARGET_DB_NAME'), 'lime_survey_977429') }}
