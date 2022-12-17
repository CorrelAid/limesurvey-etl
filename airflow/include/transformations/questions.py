import os

import pandas as pd
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
    sql_stmt = """
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
    """
    with engine.connect() as con:
        con.execute(sql_stmt)
