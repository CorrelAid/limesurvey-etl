{% macro transform_survey(survey_table_name) %}
    WITH intermediary_1 AS (
        {{ unpivot(
                relation=source(env_var('TARGET_DB_NAME'), survey_table_name),
                exclude=['id'],
                remove=['token', 'submitdate', 'lastpage', 'startlanguage', 'seed', 'startdate', 'datestamp'],
                cast_to='varchar',
                field_name='name',
                value_name='answer_code'
        )
        }}
    ),

    intermediary_2 AS (
        SELECT
            id AS respondent
            , split_part("name", 'X', 1) AS survey_id
            , split_part("name", 'X', 2)AS ls_gid
            , CASE
                WHEN CAST(LEFT(split_part("name", 'X', 3), 4) AS INTEGER) IS NULL THEN 0
                ELSE CAST(LEFT(split_part("name", 'X', 3), 4) AS INTEGER)
            END AS ls_qid
            , CASE
                WHEN SUBSTRING(split_part("name", 'X', 3), 5, 5) IS NULL THEN 'SQ001'
                WHEN SUBSTRING(split_part("name", 'X', 3), 5, 5) = 'other' THEN 'SQother'
                ELSE SUBSTRING(split_part("name", 'X', 3), 5, 5)
            END AS ls_sqid_minor
            , CASE
                WHEN split_part("name", '#', 2) = '' THEN '0'
                ELSE split_part("name", '#', 2)
            END AS scale_id
            , answer_code
        FROM intermediary_1
        WHERE "name" NOT LIKE '%comment%'
    ),

    intermediary_3 AS (
        SELECT
            intermediary_2.respondent
            , intermediary_2.survey_id
            , intermediary_2.ls_gid
            , intermediary_2.ls_qid AS question_item_id
            , intermediary_2.ls_sqid_minor
            , intermediary_2.scale_id
            , intermediary_2.answer_code
            , lime_questions.qid
            , lime_questions.parent_qid
            , lime_questions.title
            , CASE
                WHEN intermediary_2.ls_sqid_minor != '' THEN CONCAT(intermediary_2.ls_qid, '_', intermediary_2.ls_sqid_minor)
                ELSE NULL
            END AS subquestion_id
        FROM intermediary_2
        LEFT JOIN {{ source(env_var('TARGET_DB_NAME'), 'lime_questions') }} AS lime_questions
        ON intermediary_2.ls_qid = lime_questions.qid
        WHERE lime_questions.parent_qid = 0
    )

    SELECT
        intermediary_3.*
        , question_items.type_major
    FROM intermediary_3
    LEFT JOIN {{ ref('question_items') }} AS question_items
    ON intermediary_3.question_item_id = question_items.question_item_id
    WHERE type_major IS NOT NULL

{% endmacro %}
