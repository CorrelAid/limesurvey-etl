import re

import pandas as pd
from sqlalchemy import Column, Integer, MetaData, Table, inspect
from utils import connect_to_mariadb, create_table_if_not_exists, insert_on_duplicate


def get_respondents(config: dict, columns: dict):
    engine = connect_to_mariadb(
        db_host=config["COOLIFY_MARIADB_HOST"],
        db_port=config["COOLIFY_MARIADB_PORT"],
        db_user=config["COOLIFY_MARIADB_USER"],
        db_password=config["COOLIFY_MARIADB_PASSWORD"],
        db_name=config["COOLIFY_MARIADB_DATABASE"],
    )

    # create table in reporting layer if not exists
    create_table_if_not_exists(
        engine=engine, table_name="respondents", columns=columns, schema="reporting"
    )

    inspector = inspect(engine)

    # get all survey tables
    tables = inspector.get_table_names(schema="raw")
    survey_tables = [table for table in tables if re.match(r"lime_survey_\d+", table)]

    # get a dataframe containing all surveys
    dfs = [
        pd.read_sql(f"SELECT * FROM raw.{table};", con=engine)
        for table in survey_tables
    ]
    df = pd.concat(dfs, ignore_index=True)

    # get unique respondents and write data to respondents table
    respondents = pd.Series(df["id"].unique(), name="respondent_id")
    respondents.to_sql(
        name="respondents",
        con=engine,
        schema="reporting",
        if_exists="append",
        index=False,
        method=insert_on_duplicate,
    )
