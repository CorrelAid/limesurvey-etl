import sys

from sqlalchemy import create_engine, inspect, exc, text
import pandas as pd


def extract_limesurvey(config, table_names=None):
    # connect to source MariaDB Platform
    try:
        print("Connecting to Limesurvey DB")
        source_url = (
            f"mariadb+mariadbconnector://{config['LIMESURVEY_SQL_USER']}"
            f":{config['LIMESURVEY_SQL_PASSWORD']}"
            f"@127.0.0.1"
            f":{config['LIMESURVEY_DATABASE_PORT']}"
            f"/{config['LIMESURVEY_DATABASE_NAME']}"
        )
        engine_source = create_engine(source_url, echo=True)
        print("Connection to Limesurvey DB established")
    except exc.SQLAlchemyError as e:
        print(f"Error connecting to source MariaDB Platform: {e}")
        sys.exit(1)

    # connect to target MariaDB Platform
    try:
        print("Connecting to target MariaDB")
        target_url = (
            f"mariadb+mariadbconnector"
            f"://{config['COOLIFY_MARIADB_USER']}"
            f":{config['COOLIFY_MARIADB_PASSWORD']}"
            f"@{config['COOLIFY_MARIADB_HOST']}"
            f":{config['COOLIFY_MARIADB_PORT']}"
            f"/{config['COOLIFY_MARIADB_DATABASE']}"
        )
        engine_target =  create_engine(target_url, echo=True)
       
        print("Connection to target MariaDB established")
    except exc.SQLAlchemyError as e:
        print(f"Error connecting to target MariaDB Platform: {e}")
        sys.exit(1)

    if not table_names:
        source_inspector = inspect(engine_source)
        table_names = [table for table in source_inspector.get_table_names() \
            if not table.startswith("lime_old_survey")]

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
            if_exists='replace',
            index=False
        )