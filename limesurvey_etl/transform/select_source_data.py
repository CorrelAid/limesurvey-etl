import pandas as pd
from sqlalchemy import inspect
from sqlalchemy.engine import Engine

from limesurvey_etl.config.transform_config.select_source_data import (
    SelectSourceDataConfig,
)
from limesurvey_etl.connectors.staging_db_connect import StagingDBConnect
from limesurvey_etl.settings.staging_db_settings import StagingDBSettings
from limesurvey_etl.transform.base import BaseTransform


class SelectSourceDataTransform(BaseTransform[SelectSourceDataConfig]):
    """
    Performs the initial selection of data to be transformed. Needs to be part of every pipeline.
    """

    def __init__(
        self,
        config: SelectSourceDataConfig,
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
        if left_table_columns is None:
            inspector = inspect(staging_db_engine)
            columns = inspector.get_columns(left_table_name, self.config.source_schema)
            left_table_columns = [c["name"] for c in columns]
        if self.staging_db_settings.staging_db_sqlalchemy_driver == "postgresql":
            left_table_columns = [
                f'left_table."{column.split(" ")[0]}" {" ".join(column.split(" ")[1:]) if len(column.split(" ")) > 1 else ""}'
                for column in left_table_columns
            ]
        elif self.staging_db_settings.staging_db_sqlalchemy_driver == "mysql+pymysql":
            left_table_columns = [
                f'left_table.`{column.split(" ")[0]}` {" ".join(column.split(" ")[1:]) if len(column.split(" ")) > 1 else ""}'
                for column in left_table_columns
            ]
        else:
            left_table_columns = [
                f"left_table.{column}" for column in left_table_columns
            ]

        # create sql statement
        sql_stmt = f"""
                SELECT DISTINCT {",".join(left_table_columns)}
                FROM {self.config.source_schema}.{left_table_name} left_table
        """
        if len(self.config.source_tables) == 2:
            # perform join
            right_table_name = self.config.source_tables[1].table_name
            right_table_columns = self.config.source_tables[1].columns
            if right_table_columns is None:
                inspector = inspect(staging_db_engine)
                columns = inspector.get_columns(
                    right_table_name,
                    self.config.right_table_source_schema or self.config.source_schema,
                )
                right_table_columns = [c["name"] for c in columns]
            if self.staging_db_settings.staging_db_sqlalchemy_driver == "postgresql":
                right_table_columns = [
                    f'right_table."{column.split(" ")[0]}" {" ".join(column.split(" ")[1:]) if len(column.split(" ")) > 1 else ""}'
                    for column in right_table_columns
                ]
            elif (
                self.staging_db_settings.staging_db_sqlalchemy_driver == "mysql+pymysql"
            ):
                right_table_columns = [
                    f'right_table.`{column.split(" ")[0]}` {" ".join(column.split(" ")[1:]) if len(column.split(" ")) > 1 else ""}'
                    for column in right_table_columns
                ]
            else:
                right_table_columns = [
                    f"right_table.{column}" for column in right_table_columns
                ]
            sql_stmt = f"""
                SELECT DISTINCT
                    {",".join(left_table_columns)}
                    , {",".join(right_table_columns)}
                FROM {self.config.source_schema}.{left_table_name} left_table
                {self.config.join.type}
                {self.config.right_table_source_schema or self.config.source_schema}.{right_table_name} right_table
                ON left_table.{self.config.join.left_on}=right_table.{self.config.join.right_on}
            """
        if self.config.filter is not None:
            sql_stmt += self.config.filter

        df = pd.read_sql(sql_stmt, staging_db_engine)
        return df
