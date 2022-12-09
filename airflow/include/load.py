import sys

from sqlalchemy import create_engine, inspect
import pandas as pd

from airflow.providers.postgres.hooks.postgres import PostgresHook

from include.utils import connect_to_mariadb


def load(config, schema='reporting', table_names=None):
    # connect to source MariaDB Platform
    engine_source = connect_to_mariadb(
        db_host=config['COOLIFY_MARIADB_HOST'],
        db_port=config['COOLIFY_MARIADB_PORT'],
        db_user=config['COOLIFY_MARIADB_USER'],
        db_password=config['COOLIFY_MARIADB_PASSWORD'],
        db_name=config['COOLIFY_MARIADB_DATABASE']
    )

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
