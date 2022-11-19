CREATE TABLE IF NOT EXISTS reporting.subquestions (
    subquestion_id INT PRIMARY KEY
    , question_item_id INT REFERENCES reporting.question_items(question_item_id)
);

INSERT INTO reporting.subquestions (
    subquestion_id
    , question_item_id
)
SELECT DISTINCT
    qid AS subquestion_id
    , parent_qid AS question_item_id
FROM raw.lime_questions lq
WHERE parent_qid != 0
AND NOT EXISTS (
    SELECT
        1
    FROM reporting.subquestions sq
    WHERE sq.subquestion_id = lq.qid
);