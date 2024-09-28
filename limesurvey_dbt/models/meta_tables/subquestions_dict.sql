SELECT
    subquestions.subquestion_id
    , subquestions.question_item_id
    , subquestions.subquestion_item_title
    , subquestions.question_item_title
    , mapping_subquestions.label_major
    , mapping_subquestions.label_minor
    , mapping_subquestions.lang
    , mapping_subquestions.subquestion_id_minor
FROM {{ ref('subquestions') }} AS subquestions
LEFT JOIN {{ ref('mapping_subquestions') }} AS mapping_subquestions
ON subquestions.subquestion_item_title = mapping_subquestions.subquestion_id
