import pandas as pd
from utils import (
    connect_to_mariadb,
    create_table_if_not_exists,
    insert_on_duplicate,
    log_missing_values,
)


def get_question_items_dict(config: dict, columns: dict):
    engine = connect_to_mariadb(
        db_host=config["COOLIFY_MARIADB_HOST"],
        db_port=config["COOLIFY_MARIADB_PORT"],
        db_user=config["COOLIFY_MARIADB_USER"],
        db_password=config["COOLIFY_MARIADB_PASSWORD"],
        db_name=config["COOLIFY_MARIADB_DATABASE"],
    )

    # create table in reporting layer if not exists
    create_table_if_not_exists(
        engine=engine,
        table_name="question_items_dict",
        columns=columns,
        schema="reporting",
    )

    # transform data
    mapping_path = "include/mappings/mapping_question_items.csv"
    mapping_df = pd.read_csv(mapping_path, delimiter=",")
    mapping_df["question_item_id"] = mapping_df["question_item_id"].astype(str)

    sql_stmt = """
        SELECT DISTINCT
            lq.title AS question_item_id
            , lqln.language as lang
        FROM raw.lime_questions lq
        LEFT JOIN raw.lime_question_l10ns lqln
        ON lq.qid = lqln.qid
        WHERE lq.parent_qid = 0;
    """
    question_items_df = pd.read_sql(sql_stmt, con=engine)

    question_items_dict_df = question_items_df.merge(
        mapping_df, on="question_item_id", how="left", suffixes=("", "_y")
    )
    # add missing column 'label_major_short' to dataframe -> empty, since no mapping available
    question_items_dict_df["label_major_short"] = pd.Series(dtype="str")
    target_cols = [
        "question_item_id",
        "lang",
        "label_major",
        "label_major_short",
        "label_minor",
    ]
    question_items_dict_df = question_items_dict_df[target_cols]

    log_missing_values(
        question_items_dict_df,
        source_col="question_item_id",
        target_cols=["lang", "label_major", "label_major_short", "label_minor"],
        log_file_name="mapping_question_items_dict.csv",
    )

    print(question_items_dict_df)
    question_items_dict_df.to_sql(
        name="question_items_dict",
        con=engine,
        schema="reporting",
        if_exists="append",
        index=False,
        method=insert_on_duplicate,
    )


def get_subquestions_dict(config: dict, columns: dict):
    engine = connect_to_mariadb(
        db_host=config["COOLIFY_MARIADB_HOST"],
        db_port=config["COOLIFY_MARIADB_PORT"],
        db_user=config["COOLIFY_MARIADB_USER"],
        db_password=config["COOLIFY_MARIADB_PASSWORD"],
        db_name=config["COOLIFY_MARIADB_DATABASE"],
    )

    create_table_if_not_exists(
        engine=engine,
        table_name="subquestions_dict",
        columns=columns,
        schema="reporting",
    )

    sql_stmt = """
        SELECT DISTINCT
            subquestion_id
            , question_item_id
        FROM reporting.subquestions;
    """

    subquestions_df = pd.read_sql(sql_stmt, con=engine)

    mapping_path = "include/mappings/mapping_subquestions.csv"
    mapping_df = pd.read_csv(mapping_path)

    subquestions_dict_df = subquestions_df.merge(
        mapping_df, on="subquestion_id", how="left"
    )

    log_missing_values(
        subquestions_dict_df,
        "subquestion_id",
        ["lang", "subquestion_id_minor", "label_major", "label_minor"],
        log_file_name="mapping_subquestions_dict.csv",
    )
    subquestions_dict_df["lang"] = subquestions_dict_df["lang"].fillna("99")

    subquestions_dict_df.to_sql(
        name="subquestions_dict",
        con=engine,
        schema="reporting",
        if_exists="append",
        index=False,
        method=insert_on_duplicate,
    )


def get_question_answers_dict(config: dict, columns: dict):
    engine = connect_to_mariadb(
        db_host=config["COOLIFY_MARIADB_HOST"],
        db_port=config["COOLIFY_MARIADB_PORT"],
        db_user=config["COOLIFY_MARIADB_USER"],
        db_password=config["COOLIFY_MARIADB_PASSWORD"],
        db_name=config["COOLIFY_MARIADB_DATABASE"],
    )

    create_table_if_not_exists(
        engine=engine,
        table_name="question_answers_dict",
        columns=columns,
        schema="reporting",
    )

    sql_stmt = """
        SELECT DISTINCT
            question_item_id
        FROM reporting.question_items;
    """

    question_items_df = pd.read_sql(sql_stmt, con=engine)

    mapping_path = "include/mappings/mapping_question_answers.csv"
    mapping_df = pd.read_csv(mapping_path)

    questions_answers_df = question_items_df.merge(
        mapping_df, on="question_item_id", how="outer"
    )

    log_missing_values(
        questions_answers_df,
        "question_item_id",
        "answer_id",
        "mapping_question_answers.csv",
    )

    questions_answers_df["lang"] = questions_answers_df["lang"].fillna("99")
    questions_answers_df["answer_id"] = questions_answers_df["answer_id"].fillna(-999)
    questions_answers_df = questions_answers_df.rename(columns={"label": "answer_text"})

    questions_answers_df.to_sql(
        name="question_answers_dict",
        con=engine,
        schema="reporting",
        if_exists="append",
        index=False,
        method=insert_on_duplicate,
    )


def get_diversity_items_dict(config: dict, columns: dict):
    engine = connect_to_mariadb(
        db_host=config["COOLIFY_MARIADB_HOST"],
        db_port=config["COOLIFY_MARIADB_PORT"],
        db_user=config["COOLIFY_MARIADB_USER"],
        db_password=config["COOLIFY_MARIADB_PASSWORD"],
        db_name=config["COOLIFY_MARIADB_DATABASE"],
    )

    create_table_if_not_exists(
        engine=engine,
        table_name="question_answers_dict",
        columns=columns,
        schema="reporting",
    )

    sql_stmt = """
        SELECT DISTINCT
            diversity_item_id
        FROM reporting.diversity_items;
    """

    diversity_items_df = pd.read_sql(sql_stmt, con=engine)

    mapping_path = "include/mappings/mapping_diversity_items.csv"
    mapping_df = pd.read_csv(mapping_path)

    diversity_items_dict_df = diversity_items_df.merge(
        mapping_df, on="diversity_item_id", how="left"
    )

    log_missing_values(
        diversity_items_dict_df,
        source_col="diversity_item_id",
        target_cols=["lang", "label_long"],
        log_file_name="mapping_diversity_items_dict.csv",
    )

    target_cols = ["diversity_item_id", "lang", "label_long"]
    diversity_items_dict_df[target_cols].to_sql(
        name="diversity_items_dict",
        con=engine,
        schema="reporting",
        if_exists="append",
        index=False,
        method=insert_on_duplicate,
    )
