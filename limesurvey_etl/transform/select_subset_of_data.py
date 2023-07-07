import pandas as pd
from sqlalchemy.engine import Engine

from limesurvey_etl.config.transform_config.select_subset_of_data import (
    SelectSubsetOfDataConfig,
)
from limesurvey_etl.connectors.staging_db_connect import StagingDBConnect
from limesurvey_etl.settings.staging_db_settings import StagingDBSettings
from limesurvey_etl.transform.base import BaseTransform


class SelectSubsetOfDataTransform(BaseTransform[SelectSubsetOfDataConfig]):
    """
    Performs the initial selection of data to be transformed. Needs to be part of every pipeline.
    """

    def __init__(
        self,
        config: SelectSubsetOfDataConfig,
        staging_schema_name: str,
        staging_table_name: str,
    ):
        super().__init__(config)
        self.staging_schema_name = staging_schema_name
        self.staging_table_name = staging_table_name
        self.staging_db_settings = StagingDBSettings()

    def transform(self) -> pd.DataFrame:
        """
        This is the first step of a transformation pipeline. The DataFrame is not use
        """
        # connect to staging DB
        staging_db_connect = StagingDBConnect(self.staging_db_settings)
        staging_db_engine: Engine = staging_db_connect.create_sqlalchemy_engine()

        # select data
        left_table_name = self.config.source_tables[0].table_name
        left_table_columns = self.config.source_tables[0].columns
        left_table_columns = [f"left_table.{column}" for column in left_table_columns]

        # create sql statement
        sql_stmt = f"""
                SELECT DISTINCT {",".join(left_table_columns)}
                FROM {self.config.source_schema}.{left_table_name} left_table
        """
        if len(self.config.source_tables) == 2:
            # perform join
            right_table_name = self.config.source_tables[1].table_name
            right_table_columns = self.config.source_tables[1].columns
            right_table_columns = [
                f"right_table.{column}" for column in right_table_columns
            ]
            sql_stmt = f"""
                SELECT DISTINCT
                    {",".join(left_table_columns)}
                    , {",".join(right_table_columns)}
                FROM {self.config.source_schema}.{left_table_name} left_table
                {self.config.join.type}
                {self.config.source_schema}.{right_table_name} right_table
                ON left_table.{self.config.join.left_on}=right_table.{self.config.join.right_on}
            """
        if self.config.filter is not None:
            sql_stmt += self.config.filter

        df = pd.read_sql(sql_stmt, staging_db_engine)
        return df
