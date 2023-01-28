import os

import pandas as pd
import csv
from jinja2 import Template

from utils import connect_to_mariadb, insert_on_duplicate, \
    create_table_if_not_exists


def get_question_groups(config: dict, columns: dict):
    engine = connect_to_mariadb(
        db_host=config['COOLIFY_MARIADB_HOST'],
        db_port=config['COOLIFY_MARIADB_PORT'],
        db_user=config['COOLIFY_MARIADB_USER'],
        db_password=config['COOLIFY_MARIADB_PASSWORD'],
        db_name=config['COOLIFY_MARIADB_DATABASE']
    )
    # create table in reporting layer if not exists
    create_table_if_not_exists(
        engine=engine,
        table_name="question_groups",
        columns=columns,
        schema="reporting"
    )

    # execute transformation
    sql_stmt = """
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
    """
    with engine.connect() as con:
        con.execute(sql_stmt)


def get_question_items(config: dict, columns: dict):
    engine = connect_to_mariadb(
        db_host=config['COOLIFY_MARIADB_HOST'],
        db_port=config['COOLIFY_MARIADB_PORT'],
        db_user=config['COOLIFY_MARIADB_USER'],
        db_password=config['COOLIFY_MARIADB_PASSWORD'],
        db_name=config['COOLIFY_MARIADB_DATABASE']
    )

    # create table in reporting layer if not exists
    create_table_if_not_exists(
        engine=engine,
        table_name="question_items",
        columns=columns,
        schema="reporting"
    )

    # import mappings and apply transformations
    mappings_path = 'include/mappings/Mapping_LS-QuestionTypesMajor.csv'
    mappings_df = pd.read_csv(mappings_path, delimiter=';')
    mappings = list(zip(mappings_df['Fragetyp-ID (LS)'], mappings_df['Fragetyp Major (CFE)']))

    jinja_sql = """
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
    sql_stmt = Template(jinja_sql).render(mappings=mappings)
    with engine.connect() as con:
        con.execute(sql_stmt)


def get_subquestions(config: dict, columns: dict):
    engine = connect_to_mariadb(
        db_host=config['COOLIFY_MARIADB_HOST'],
        db_port=config['COOLIFY_MARIADB_PORT'],
        db_user=config['COOLIFY_MARIADB_USER'],
        db_password=config['COOLIFY_MARIADB_PASSWORD'],
        db_name=config['COOLIFY_MARIADB_DATABASE']
    )
    # create table in reporting layer if not exists
    create_table_if_not_exists(
        engine=engine,
        table_name="subquestions",
        columns=columns,
        schema="reporting"
    )

    # transform data
    mapping_path = 'include/mappings/mapping_subquestions.csv'
    mapping_dict = {}
    with open(mapping_path, 'r') as f:
        for i, line in enumerate(csv.reader(f)):
            if i > 0 and line[2] not in mapping_dict.keys():
                mapping_dict[line[2]] = line[0]
                

    mapping_df = pd.read_csv(mapping_path, delimiter=',')
    
    sql_stmt = """
        SELECT DISTINCT
            subq.title AS subquestion_id
            , parent.title AS question_item_id
        FROM raw.lime_questions subq
        JOIN raw.lime_questions parent
        ON subq.parent_qid=parent.qid
        WHERE subq.parent_qid != 0;
    """
    
    # replace subquestion_ids with those from the mapping
    subquestions_df = pd.read_sql(sql_stmt, con=engine)
    subquestions_df = subquestions_df.replace(mapping_dict)
    print(subquestions_df.head())
    subquestions_df.to_sql(
        name="subquestions",
        con=engine,
        schema="reporting",
        if_exists="replace",
        index=False
    )
