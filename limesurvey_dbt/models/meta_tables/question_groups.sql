SELECT DISTINCT
    gid AS question_group_id
    , group_name AS question_group_name
FROM {{ source(env_var('TARGET_DB_NAME'), 'lime_group_l10ns')}}
