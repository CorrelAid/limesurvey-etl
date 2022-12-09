import sys

import re
from sqlalchemy import create_engine, inspect, exc
import pandas as pd

from include.utils import connect_to_mariadb


def extract_limesurvey(config: dict, table_names: list[str] = None):
    # connect to source MariaDB Platform
    engine_source = connect_to_mariadb(
        db_host="127.0.0.1",
        db_port=config['LIMESURVEY_DATABASE_PORT'],
        db_user=config['LIMESURVEY_SQL_USER'],
        db_password=config['LIMESURVEY_SQL_PASSWORD'],
        db_name=config['LIMESURVEY_DATABASE_NAME']
    )

    # connect to target MariaDB Platform
    engine_target = connect_to_mariadb(
        db_host=config['COOLIFY_MARIADB_HOST'],
        db_port=config['COOLIFY_MARIADB_PORT'],
        db_user=config['COOLIFY_MARIADB_USER'],
        db_password=config['COOLIFY_MARIADB_PASSWORD'],
        db_name=config['COOLIFY_MARIADB_DATABASE']
    )
    
    source_inspector = inspect(engine_source)
    if not table_names:
        table_names = [table for table in source_inspector.get_table_names() \
            if not table.startswith("lime_old_survey")]
    else: 
        table_names.extend([table for table in source_inspector.get_table_names() \
            if re.match(r'lime_survey_\d+', table)])
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
