CREATE TABLE IF NOT EXISTS reporting.question_groups (
    question_group_id INT PRIMARY KEY
    , question_group_name VARCHAR(255) NOT NULL
    , description VARCHAR(255)
);

INSERT INTO reporting.question_groups 
(
    question_group_id
    , question_group_name
    , description
)
SELECT DISTINCT 
    gid
    , group_name
    , description
FROM raw.lime_group_l10ns lg
WHERE NOT EXISTS (
	SELECT
		1
	FROM reporting.question_groups qg
	WHERE qg.question_group_id = lg.gid
);
