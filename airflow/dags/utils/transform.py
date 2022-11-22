import sys

import sqlparse
from sqlalchemy import create_engine, inspect, exc, text


def sql_transform(config, sql_file=None, sql_stmts=None):
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
        engine =  create_engine(target_url, echo=True)
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
