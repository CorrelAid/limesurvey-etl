WITH question_types AS (
    SELECT DISTINCT
        "Fragetyp Major (CFE)" AS type_major
        , "Fragetyp-ID (LS)" AS type_id
    FROM {{ ref('Mapping_LS-QuestionTypesMajor')}}
)

SELECT DISTINCT
    lime_questions.qid AS question_item_id
    , lime_questions.title AS question_item_title
    , lime_questions.gid AS question_group_id
    , lime_questions.type AS type_minor
    , question_types.type_major
FROM {{ source(env_var('TARGET_DB_NAME'), 'lime_questions') }} AS lime_questions
LEFT JOIN question_types
ON lime_questions.type = question_types.type_id
