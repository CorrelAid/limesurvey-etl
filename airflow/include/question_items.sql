CREATE TABLE IF NOT EXISTS reporting.question_items (
    question_item_id INT PRIMARY KEY
    , question_group_id INT REFERENCES reporting.question_groups(question_group_id)
    , type_major VARCHAR(255)
    , type_minor VARCHAR(255)
);

INSERT INTO reporting.question_items (
    question_item_id
    , question_group_id
    , type_major
    , type_minor
)
SELECT DISTINCT
    qid AS question_item_id
	, gid AS question_group_id
	, type AS type_major
    , NULL AS type_minor
FROM raw.lime_questions lq
WHERE parent_qid = 0
AND NOT EXISTS (
    SELECT 
        1
    FROM reporting.question_items qi
    WHERE qi.question_item_id = lq.qid
);
