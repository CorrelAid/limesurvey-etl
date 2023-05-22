import os
import sys
from typing import Union

import pandas as pd
from sqlalchemy import Column, ForeignKey, MetaData, Table, create_engine, engine, exc
from sqlalchemy.dialects.mysql import insert


def connect_to_mariadb(
    db_host: str, db_port: int, db_user: str, db_password: str, db_name: str
):
    """
    Connects to a MariaDB database and returns a SQLAlchemy engine.
    :param db_host: Host of the database.
    :param db_port: Port of the database.
    :param db_user: Name of the database user.
    :param db_password: Password to authenticate the database user.
    :param db_name: Name of the database to connect with.
    :return: A SQLAlchemy engine.
    :rtype: sqlalchemy.engine.Engine
    """
    try:
        print("Connecting to MariaDB")
        url = (
            f"mariadb+mariadbconnector://{db_user}"
            f":{db_password}"
            f"@{db_host}"
            f":{db_port}"
            f"/{db_name}"
        )
        engine = create_engine(url, echo=True)
        print("Connection to MariaDB established")

        return engine
    except exc.SQLAlchemyError as e:
        print(f"Error connecting to MariaDB: {e}")
        sys.exit(1)


def insert_on_duplicate(table, conn, keys, data_iter):
    """
    Method to be passed to pd.to_sql. Ensures no duplicates on primary keys are
    inserted into the given table.
    """
    insert_stmt = insert(table.table).values(list(data_iter))
    on_duplicate_key_stmt = insert_stmt.on_duplicate_key_update(insert_stmt.inserted)
    conn.execute(on_duplicate_key_stmt)


def create_table_if_not_exists(
    engine: engine.Engine, table_name: str, columns: dict, schema: str = None
):
    """
    Function to create a table if it does not exist using SQLAlchemy.
    :param engine: SqlAlchemy engine to be used for table creation.
    :param table_name: Name of the table to be created.
    :param columns: dictionary containing the column specifications of
                    the following format:
                    {
                        "<COLUMN_NAME>": {
                            "type": "<SQLALCHEMY_DATA_TYPE>",
                            "primary_key": boolean, defaults to False,
                            "nullable": boolean, defaults to True,
                            "foreign_key": <TABLE.COLUMN>, defaults to None
                        }
                    }
    """
    with engine.connect() as con:
        if not engine.dialect.has_table(con, table_name=table_name, schema=schema):
            print("Creating table")
            metadata = MetaData(engine, schema=schema)
            metadata.reflect(bind=engine)
            Table(
                table_name,
                metadata,
                schema=schema,
                *(
                    Column(
                        column_name,
                        config["type"],
                        ForeignKey(config["foreign_key"]),
                        nullable=config.get("nullable", True),
                        primary_key=config.get("primary_key", False),
                    )
                    if "foreign_key" in config.keys()
                    else Column(
                        column_name,
                        config["type"],
                        nullable=config.get("nullable", True),
                        primary_key=config.get("primary_key", False),
                    )
                    for column_name, config in columns.items()
                ),
            ).create()


def log_missing_values(
    df: pd.DataFrame,
    source_col: str,
    target_cols: Union[str, list[str]],
    log_file_name: str,
) -> None:
    target_cols = target_cols if type(target_cols) == list else [target_cols]
    missing_values_df = df.loc[df[[source_col] + target_cols].isna().any(axis=1)]
    if len(missing_values_df) > 0:
        path = "logs/mappings"
        if not os.path.exists(path):
            os.mkdir(path)
        missing_values_df.to_csv(path + f"/{log_file_name}", index=False)
