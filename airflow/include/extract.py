import pandas as pd
from airflow.hooks.base import BaseHook
from airflow.models import Variable
from include.utils import connect_to_mariadb
from sqlalchemy import create_engine, inspect


def extract_limesurvey(target_db_conn_id: str, table_names: list[str] = None):
    # connect to source MariaDB Platform
    engine_source = connect_to_mariadb(
        db_host="127.0.0.1",
        db_port=Variable.get("LIMESURVEY_SECRET_DATABASE_PORT"),
        db_user=Variable.get("LIMESURVEY_SECRET_SQL_USER"),
        db_password=Variable.get("LIMESURVEY_SQL_PASSWORD"),
        db_name=Variable.get("LIMESURVEY_SECRET_DATABASE_NAME"),
    )

    # connect to target DB
    target = BaseHook.get_connection(target_db_conn_id)
    engine_target = create_engine(
        f"postgresql://{target.login}:{target.password}@{target.host}:{target.port}/{target.schema}"
    )

    source_inspector = inspect(engine_source)
    if not table_names:
        table_names = [
            table
            for table in source_inspector.get_table_names()
            if not table.startswith("lime_old_survey")
        ]
    # load tables to target DB
    with engine_target.connect() as con:
        con.execute("CREATE SCHEMA IF NOT EXISTS raw;")

    for table in table_names:
        print(f"table: {table}")
        dataFrame = pd.read_sql(f"SELECT * FROM {table};", engine_source)

        dataFrame.to_sql(
            name=table,
            con=engine_target,
            schema="raw",
            if_exists="replace",
            index=False,
        )
