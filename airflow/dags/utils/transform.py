import sys

import pandas as pd
import sqlparse
from sqlalchemy import create_engine, exc, text, inspect


EXCLUDE_COLS = []
PATTERNS = []

def sql_transform(config: dict, sql_file: str = None, sql_stmts: str = None):
    """
    Run SQL queries on the Coolify MariaDB based on 
    either a .sql file or a string containing sql statements. 
    :param config: dictionary containing the credentials to connect to the Coolify MariaDB.
    :param sql_file: path to a SQL file that should be executed. 
                     Either sql_file or sql_stmts should be assigned a value, not both.
    :param sql_stmts: SQL statement. Either sql_file or sql_stmts should be assigned a value, not both.
    """
    # connect to target MariaDB Platform
    try:
        print("Connecting to MariaDB")
        target_url = (
            f"mariadb+mariadbconnector"
            f"://{config['COOLIFY_MARIADB_USER']}"
            f":{config['COOLIFY_MARIADB_PASSWORD']}"
            f"@{config['COOLIFY_MARIADB_HOST']}"
            f":{config['COOLIFY_MARIADB_PORT']}"
            f"/{config['COOLIFY_MARIADB_DATABASE']}"
        )
        engine = create_engine(target_url, echo=True)
        print("Connection to target MariaDB established")
    except exc.SQLAlchemyError as e:
        print(f"Error connecting to target MariaDB Platform: {e}")
        sys.exit(1)
    
    with engine.connect() as con:
        if sql_file:
            with open(sql_file, 'r') as f:
                sql = f.read()
        else:
            sql = sql_stmts
        sql_stmts = sqlparse.split(sql)
        for sql_stmt in sql_stmts:
            con.execute(text(sql_stmt))


def transform_survey(config: dict):
    # connect to target MariaDB Platform
    try:
        print("Connecting to MariaDB")
        target_url = (
            f"mariadb+mariadbconnector"
            f"://{config['COOLIFY_MARIADB_USER']}"
            f":{config['COOLIFY_MARIADB_PASSWORD']}"
            f"@{config['COOLIFY_MARIADB_HOST']}"
            f":{config['COOLIFY_MARIADB_PORT']}"
            f"/{config['COOLIFY_MARIADB_DATABASE']}"
        )
        engine = create_engine(target_url, echo=True)
        print("Connection to target MariaDB established")
    except exc.SQLAlchemyError as e:
        print(f"Error connecting to target MariaDB Platform: {e}")
        sys.exit(1)

    # get survey tables
    inspector = inspect(engine)
    tables = [pd.read_sql(f"SELECT * FROM raw.{table}", engine) for table in inspector.get_table_names(schema='raw') \
            if table.startswith("lime_survey_")]
    
    # load survey data as Pandas dataframe
    df = pd.concat(tables, ignore_index=True)
    df = drop_unnecessary_variables(df, exclude_cols=EXCLUDE_COLS, patterns=PATTERNS)


def drop_unnecessary_variables(df: pd.DataFrame, exclude_cols: list[str] = [], patterns: list[tuple] = []):
    drop_cols = exclude_cols
    for col in df.columns:
        for pattern in patterns:
            if pattern[0] == 'contains' and col.contains(pattern[1]):
                drop_cols.append(col)
                break
            elif pattern[0] == 'ends_with' and col.ends_with(pattern[1]):
                drop_cols.append(col)
                break
            elif pattern[0] == 'starts_with' and col.starts_with(pattern[1]):
                drop_cols.append(col)
                break
            
    df = df.drop(exclude_cols, axis=1, inplace=False)

    return df
