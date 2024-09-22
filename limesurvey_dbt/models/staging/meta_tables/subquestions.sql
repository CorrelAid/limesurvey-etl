WITH lime_questions AS (
    SELECT
    qid
    , parent_qid
    , title
FROM {{ source(env_var('TARGET_DB_NAME'), 'lime_questions') }}
),

subquestions_questions AS (
    SELECT
        subquestions.qid AS subquestion_id
        , subquestions.title AS subquestion_item_title
        , questions.qid AS question_item_id
        , questions.title AS question_item_title
    FROM lime_questions AS subquestions
    JOIN lime_questions AS questions
    ON subquestions.parent_qid = questions.qid
    WHERE subquestions.parent_qid != 0
)

SELECT
    question_item_id
    , question_item_title
    , subquestion_id
    , CONCAT(question_item_title, '_', subquestion_item_title) AS subquestion_item_title
FROM subquestions_questions
