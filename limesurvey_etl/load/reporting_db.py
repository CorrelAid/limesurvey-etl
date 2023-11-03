import logging

import pandas as pd
import sqlalchemy.exc
from sqlalchemy import MetaData, Table, create_engine, insert, inspect, select
from sqlalchemy.dialects.mysql import insert as mysql_insert
from sqlalchemy.dialects.postgresql import insert as postgresql_insert
from sqlalchemy.engine import Engine

from limesurvey_etl.config.load_config.reporting_db import ReportingDBLoadConfig
from limesurvey_etl.connectors.reporting_db_connect import ReportingDBConnect
from limesurvey_etl.connectors.staging_db_connect import StagingDBConnect
from limesurvey_etl.load.base import BaseLoad
from limesurvey_etl.settings.reporting_db_settings import ReportingDBSettings
from limesurvey_etl.settings.staging_db_settings import StagingDBSettings


def insert_on_duplicate(table, conn, keys, data_iter):
    """
    Method to be passed to pd.to_sql. Ensures no duplicates on primary keys are
    inserted into the given table.
    """
    data_list = [dict(zip(keys, row)) for row in data_iter]
    insert_stmt = mysql_insert(table.table).values(list(data_list))
    on_duplicate_key_stmt = insert_stmt.on_duplicate_key_update(insert_stmt.inserted)
    conn.execute(on_duplicate_key_stmt)


def postgres_upsert(table, conn, keys, data_iter):
    data = [dict(zip(keys, row)) for row in data_iter]
    insert_stmt = postgresql_insert(table.table).values(data)
    upsert_stmt = insert_stmt.on_conflict_do_update(
        constraint=f"{table.table.name}_pkey",
        set_={c.name: c for c in insert_stmt.excluded if not c.primary_key},
    )

    conn.execute(upsert_stmt)


class DatabaseTransfer:
    def __init__(self, source_db_url, destination_db_url):
        self.source_db_url = source_db_url
        self.destination_db_url = destination_db_url
        self.source_engine = None
        self.destination_engine = None

    def __enter__(self):
        self.source_engine = create_engine(self.source_db_url)
        self.destination_engine = create_engine(self.destination_db_url)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.source_engine.dispose()
        self.destination_engine.dispose()

    def transfer_tables(self):
        table_names = self.source_engine.table_names()
        for table_name in table_names:
            source_table = self.source_engine.meta.tables[table_name]
            select_query = select([source_table])
            result = self.source_engine.execute(select_query)
            data = result.fetchall()
            destination_table = self.destination_engine.meta.tables[table_name]
            self.destination_engine.execute(insert(destination_table).values(data))
        self.destination_engine.commit()


class ReportingDBLoad(BaseLoad[ReportingDBLoadConfig]):
    """
    Load data from staging DB to target DB.
    """

    def __init__(self, config: ReportingDBLoadConfig) -> None:
        super().__init__(config)
        self.staging_db_settings = StagingDBSettings()
        self.reporting_db_settings = ReportingDBSettings()

    def load(self) -> None:
        """
        Loads data from a staging DB to a target DB.
        """

        # connect to staging DB
        logging.info("Connecting to Staging DB.")
        staging_db_connect = StagingDBConnect(self.staging_db_settings)
        staging_db_engine: Engine = staging_db_connect.create_sqlalchemy_engine()
        logging.info("Successfully connected to staging DB.")

        # connect to reporting DB
        logging.info("Connecting to Reporting DB.")
        reporting_db_connect = ReportingDBConnect(self.reporting_db_settings)
        reporting_db_engine = reporting_db_connect.create_sqlalchemy_engine()
        logging.info("Successfully connected to reporting DB.")

        # create schema to store data in if it does not exist
        reporting_schema = self.config.target_schema or "limesurvey_dwh"
        with reporting_db_engine.connect() as conn:
            conn.execute(f"CREATE SCHEMA IF NOT EXISTS {reporting_schema}")
        # load data from staging DB to reporting DB
        staging_db_meta = MetaData(
            bind=staging_db_engine, schema=self.config.staging_schema
        )
        reporting_db_meta = MetaData(bind=reporting_db_engine, schema=reporting_schema)

        logging.info("Loading tables from staging DB to reporting DB.")
        table_names = self.config.tables

        for table_name in table_names:
            source_table = Table(
                table_name,
                staging_db_meta,
                autoload=True,
                autoload_with=staging_db_engine,
            )

            reporting_tables = inspect(reporting_db_engine).get_table_names(
                schema=reporting_schema
            )

            if table_name not in reporting_tables:
                destination_table = destination_table = source_table.to_metadata(
                    reporting_db_meta
                )
                destination_table.schema = reporting_schema
                reporting_db_meta.create_all()

            select_query = f"SELECT * FROM {self.config.staging_schema}.{table_name}"
            df = pd.read_sql(select_query, con=staging_db_engine)
            sql_driver_to_method_mapper = {
                "postgresql": postgres_upsert,
                "mysql+pymysql": insert_on_duplicate,
            }
            method = sql_driver_to_method_mapper[
                ReportingDBSettings().reporting_db_sqlalchemy_driver
            ]
            try:
                df.to_sql(
                    name=table_name,
                    con=reporting_db_engine,
                    schema=reporting_schema,
                    if_exists="append",
                    index=False,
                    method=method,
                )
            except sqlalchemy.exc.ProgrammingError:
                df.to_sql(
                    name=table_name,
                    con=reporting_db_engine,
                    schema=reporting_schema,
                    if_exists="replace",
                    index=False,
                )
