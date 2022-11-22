import sys

from sqlalchemy import create_engine, inspect, exc
import pandas as pd

from airflow.providers.postgres.hooks.postgres import PostgresHook


def load(config, schema='reporting', table_names=None):
    # connect to source MariaDB Platform
    try:
        print("Connecting to target MariaDB")
        source_url = (
            f"mariadb+mariadbconnector"
            f"://{config['COOLIFY_MARIADB_USER']}"
            f":{config['COOLIFY_MARIADB_PASSWORD']}"
            f"@{config['COOLIFY_MARIADB_HOST']}"
            f":{config['COOLIFY_MARIADB_PORT']}"
            f"/{config['COOLIFY_MARIADB_DATABASE']}"
        )
        engine_source =  create_engine(source_url, echo=True)
       
        print("Connection to target MariaDB established")
    except exc.SQLAlchemyError as e:
        print(f"Error connecting to target MariaDB Platform: {e}")
        sys.exit(1)

    # connect to target PG DB
    pg_hook = PostgresHook(
        postgres_conn_id="coolify_pg"
    )
    engine_target = pg_hook.get_sqlalchemy_engine()
    print("Connected to target Postgres DB")

    if not table_names:
        source_inspector = inspect(engine_source)
        table_names = source_inspector.get_table_names(schema=schema)

    for table in table_names:
        print(f"table: {table}")
        dataFrame = pd.read_sql(f"SELECT * FROM {schema}.{table};", engine_source)

        dataFrame.to_sql(
            name=table,
            con=engine_target,
            schema="temp_dwh",
            if_exists='replace',
            index=False
        )