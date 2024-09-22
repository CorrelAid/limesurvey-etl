WITH lime_questions AS (
    SELECT
        lime_questions.qid AS question_item_id
        , lime_questions.title AS question_item_title
        , lime_questions_l10ns.language AS lang
    FROM {{ source(env_var('TARGET_DB_NAME'), 'lime_questions')}} AS lime_questions
    LEFT JOIN {{ source(env_var('TARGET_DB_NAME'), 'lime_question_l10ns') }} AS lime_questions_l10ns
    ON lime_questions.qid = lime_questions_l10ns.qid
    WHERE lime_questions.parent_qid = 0
)

SELECT
    lime_questions.question_item_id
    , lime_questions.question_item_title
    , lime_questions.lang
    , mapping_question_items.label_major
    , mapping_question_items.label_minor
FROM lime_questions
LEFT JOIN {{ ref('mapping_question_items') }}
ON lime_questions.question_item_title = mapping_question_items.question_item_id
