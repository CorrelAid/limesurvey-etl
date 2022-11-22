CREATE TABLE IF NOT EXISTS reporting.subquestions (
    subquestion_id VARCHAR(50) PRIMARY KEY
    , question_item_id VARCHAR(50) REFERENCES reporting.question_items(question_item_id)
);

INSERT INTO reporting.subquestions (
    subquestion_id
    , question_item_id
)
SELECT DISTINCT
    CONCAT(parent.title, "_", lq.title) AS subquestion_id
    , parent.title AS question_item_id
FROM raw.lime_questions lq
JOIN raw.lime_questions parent
ON lq.parent_qid=parent.qid
WHERE lq.parent_qid != 0
AND NOT EXISTS (
    SELECT
        1
    FROM reporting.subquestions sq
    WHERE sq.subquestion_id = CONCAT(parent.title, "_", lq.title)
);
