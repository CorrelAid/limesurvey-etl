import logging

import pandas as pd
from sqlalchemy.engine import Engine
from sshtunnel import SSHTunnelForwarder

from limesurvey_etl.config.extract_config.limesurvey import LimesurveyExtractConfig
from limesurvey_etl.connectors.limesurvey_connect import LimesurveyConnect
from limesurvey_etl.connectors.staging_db_connect import StagingDBConnect
from limesurvey_etl.extract.base import BaseExtract
from limesurvey_etl.settings.limesurvey_settings import LimesurveySettings
from limesurvey_etl.settings.staging_db_settings import StagingDBSettings


class LimesurveyExtract(BaseExtract[LimesurveyExtractConfig]):
    """
    Extract data from Limesurvey.
    """

    def __init__(self, config: LimesurveyExtractConfig) -> None:
        super().__init__(config)
        self.limesurvey_settings = LimesurveySettings()
        staging_db_settings = StagingDBSettings()
        self.staging_db_engine: Engine = StagingDBConnect(
            staging_db_settings
        ).create_sqlalchemy_engine()
        self.limesurvey_engine: Engine = LimesurveyConnect(
            LimesurveySettings()
        ).create_sqlalchemy_engine()

    def _get_staging_db_engine(self) -> Engine:
        # connect to staging DB
        staging_db_connect = StagingDBConnect(StagingDBSettings())
        return staging_db_connect.create_sqlalchemy_engine()

    def extract(self) -> None:
        """
        Extracts data from a Limesurvey MariaDB database and stores the results in a staging DB
        based on the configuration.
        :return: a list of DataFrames containing the extracted data
        :rtype: list[pd.DataFrame]
        """

        # create schema to store raw data in if it does not exist
        logging.info("Creating staging schema in staging DB if not exists.")
        staging_schema = self.config.staging_schema
        with self.staging_db_engine.connect() as conn:
            conn.execute(f"CREATE SCHEMA IF NOT EXISTS {staging_schema};")

        logging.info("Successfully created staging schema.")

        # extract data and store it to staging db
        logging.info("Extracting data from limesurvey.")
        if self.config.use_ssh:
            logging.info("SSHing into limesurvey server.")
            with SSHTunnelForwarder(
                (
                    self.limesurvey_settings.limesurvey_ssh_host,
                    self.limesurvey_settings.limesurvey_ssh_port,
                ),
                ssh_username=self.limesurvey_settings.limesurvey_ssh_username,
                ssh_password=self.limesurvey_settings.limesurvey_ssh_password,
                remote_bind_address=(
                    self.limesurvey_settings.limesurvey_db_host,
                    int(self.limesurvey_settings.limesurvey_db_port),
                ),
                local_bind_address=(
                    self.limesurvey_settings.limesurvey_db_host,
                    int(self.limesurvey_settings.limesurvey_db_port),
                ),
            ):
                logging.info("SSHed into limesurvey server.")
                dfs = self._extract_data(
                    staging_db_engine=self.staging_db_engine,
                    staging_schema=staging_schema,
                )
        else:
            dfs = self._extract_data()

        for table, df in dfs.items():
            logging.info(f"Storing extracted data from {table} to staging DB")
            df.to_sql(
                name=table,
                con=self.staging_db_engine,
                schema=staging_schema,
                # TODO: replace might not be the best choice here
                if_exists="replace",
                index=False,
            )
            logging.info(f"Successfully stored table {table} in staging area")

    def _extract_data(
        self,
    ) -> pd.DataFrame:
        dfs = {}
        logging.info("Initializing data extraction")
        tables: list[str] = self.config.tables
        for table in tables:
            logging.info(f"Extracting data from table: {table}")
            df = pd.read_sql(f"SELECT * FROM {table};", self.limesurvey_engine)
            dfs[table] = df
        return dfs
