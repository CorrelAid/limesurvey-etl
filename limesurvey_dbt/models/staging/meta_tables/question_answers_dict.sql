SELECT
    question_items.question_item_id
    , question_items.question_item_title
    , CASE
        WHEN mapping_question_answers.lang  IS NULL THEN '99'
        ELSE mapping_question_answers.lang
      END
    , mapping_question_answers.answer_id
    , mapping_question_answers.label AS answer_text
FROM {{ ref('question_items') }} AS question_items
JOIN {{ ref('mapping_question_answers')}} AS mapping_question_answers
ON question_items.question_item_title = mapping_question_answers.question_item_id
