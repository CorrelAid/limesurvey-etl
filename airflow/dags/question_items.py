from jinja2 import Template
import pandas as pd

import os

sql = """
CREATE TABLE IF NOT EXISTS reporting.question_items (
    question_item_id VARCHAR(50) PRIMARY KEY
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
    title AS question_item_id
	, gid AS question_group_id
    , CASE
	    {% for mapping in mappings %}
        WHEN type = '{{ mapping[0] }}'
        THEN "{{ mapping[1] }}"
        {% endfor %} 
        ELSE NULL
    END AS type_major
    , type AS type_minor
FROM raw.lime_questions lq
WHERE parent_qid = 0
AND NOT EXISTS (
    SELECT 
        1
    FROM reporting.question_items qi
    WHERE qi.question_item_id = lq.title
);
"""
mappings_path = 'include/mappings/Mapping_LS-QuestionTypesMajor.csv'

mappings_df = pd.read_csv(mappings_path, delimiter=';')
mappings_df = mappings_df.dropna(subset=['Fragetyp Major (CFE)'])
print(mappings_df[['Fragetyp-ID (LS)','Fragetyp Major (CFE)']])
mappings = list(zip(mappings_df['Fragetyp-ID (LS)'], mappings_df['Fragetyp Major (CFE)']))

GET_QUESTION_ITEMS = Template(sql).render(mappings=mappings)
print(GET_QUESTION_ITEMS)