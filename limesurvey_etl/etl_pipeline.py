import logging
import sys
from enum import Enum
from pathlib import Path
from typing import Any, Sequence

import yaml
from sqlalchemy import Column, ForeignKey, MetaData, Table
from sqlalchemy.dialects.mysql import insert as mysql_insert
from sqlalchemy.dialects.postgresql import insert as postgresql_insert
from sqlalchemy.engine import Engine
from sqlalchemy.schema import CreateSchema

from limesurvey_etl.config.extract_config.limesurvey import (  # noqa
    LimesurveyExtractConfig,
)
from limesurvey_etl.config.load_config.reporting_db import ReportingDBLoadConfig  # noqa
from limesurvey_etl.config.transform_config.transformation_pipeline import (
    TransformationPipelineConfig,
)
from limesurvey_etl.connectors.staging_db_connect import StagingDBConnect
from limesurvey_etl.extract.base import BaseExtract
from limesurvey_etl.extract.limesurvey import LimesurveyExtract  # noqa
from limesurvey_etl.load.base import BaseLoad
from limesurvey_etl.load.reporting_db import ReportingDBLoad  # noqa
from limesurvey_etl.settings.staging_db_settings import StagingDBSettings
from limesurvey_etl.transform.add_columns import AddColumnsTransform  # noqa
from limesurvey_etl.transform.add_computed_column import AddComputedColumnTransform
from limesurvey_etl.transform.fill_null_values import FillNullValuesTransform  # noqa
from limesurvey_etl.transform.filter_data import FilterDataTransform  # noqa
from limesurvey_etl.transform.join_with_csv_mapping import (  # noqa
    JoinWithCSVMappingTransform,
)
from limesurvey_etl.transform.rename_columns import RenameColumnsTransform  # noqa
from limesurvey_etl.transform.select_source_data import (  # noqa
    SelectSourceDataTransform,
)
from limesurvey_etl.transformation_pipeline import TransformationPipeline


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


def str_to_class(classname: str) -> Any:
    return getattr(sys.modules[__name__], classname)


class Extractor(Enum):
    LimesurveyExtract = "limesurvey_extract"


class Transformer(Enum):
    AddColumnsTransform = "add_columns"
    FillNullValuesTransform = "fill_null_values"
    FilterDataTransform = "filter_data"
    JoinWithCSVMappingTransform = "join_with_csv_mapping"
    RenameColumnsTransform = "rename_columns"
    AddComputedColumnTransform = "add_computed_column"


class Loader(Enum):
    ReportingDBLoad = "reporting_db_load"


class Pipeline:
    def __init__(
        self,
        extract: BaseExtract,
        transformation_pipelines: Sequence[TransformationPipelineConfig],
        load: BaseLoad,
    ):
        self.extract = extract
        self.transformation_pipelines = transformation_pipelines
        self.load = load

    @classmethod
    def _get_extractor(cls, config: dict) -> BaseExtract:
        extract_type = config["extract_type"]
        extract_config = str_to_class(Extractor(extract_type).name + "Config")(**config)
        extractor = str_to_class(Extractor(extract_type).name)(extract_config)

        return extractor

    @classmethod
    def _get_transformation_pipelines(
        cls, config: dict
    ) -> TransformationPipelineConfig:
        return [transformation_pipeline for transformation_pipeline in config]

    @classmethod
    def _get_loader(cls, config: dict) -> BaseLoad:
        load_type = config["load_type"]
        loader_config = str_to_class(Loader(load_type).name + "Config")(**config)
        loader = str_to_class(Loader(load_type).name)(loader_config)

        return loader

    @classmethod
    def get_pipeline(cls, config_file_path: Path) -> "Pipeline":
        """
        Classmethod that can be used to construct a Pipeline object from a config file.
        :param config_file_path: Path to a yaml config file.
        :return: An ETL pipeline
        :rtype: Pipeline
        """
        if not config_file_path.exists():
            raise ValueError(
                f"config_file_path {config_file_path.resolve()} does not exist!"
            )

        with open(str(config_file_path), "r") as config_file:
            config = yaml.safe_load(config_file)

        # build pipeline
        extractor = cls._get_extractor(config["extract"])
        transformation_pipelines = cls._get_transformation_pipelines(
            config["transformation_pipelines"]
        )
        loader = cls._get_loader(config["load"])

        pipeline = cls(
            extract=extractor,
            transformation_pipelines=transformation_pipelines,
            load=loader,
        )

        return pipeline

    def run_all(self) -> None:
        self.run_extract()
        self.run_transform()
        self.run_load()

    def run_extract(self) -> None:
        return self.extract.extract()

    def run_transform(self, table_name: str = None) -> None:
        staging_db_connect = StagingDBConnect(StagingDBSettings())
        staging_db_engine = staging_db_connect.create_sqlalchemy_engine()

        for transformation_pipeline in self.transformation_pipelines:
            if (
                transformation_pipeline["table_name"] == table_name
                or table_name is None
            ):
                # get table
                transformation_pipeline_config = TransformationPipelineConfig(
                    **transformation_pipeline
                )
                transformation_pipeline = TransformationPipeline(
                    transformation_pipeline_config
                )
                # create table in staging area
                staging_schema_name = transformation_pipeline.config.staging_schema
                staging_table_name = transformation_pipeline.config.table_name

                if transformation_pipeline.config.columns is not None:
                    print(f"Creating table {staging_table_name}")
                    self.create_table_if_not_exists(
                        engine=staging_db_engine,
                        table_name=staging_table_name,
                        columns=transformation_pipeline.config.columns,
                        schema=staging_schema_name,
                    )

                # run transformation steps
                transformation_steps = transformation_pipeline.config.transform_steps
                if (
                    transformation_steps is None
                    or transformation_pipeline.config.source_data is None
                ):
                    continue

                transformer_data_config = transformation_pipeline.config.source_data
                transformer = SelectSourceDataTransform(
                    transformer_data_config, staging_schema_name, staging_table_name
                )

                df = transformer.transform()
                if len(transformation_steps) > 0:
                    for (
                        transformer_config
                    ) in transformation_pipeline.config.transform_steps:
                        transformer = str_to_class(
                            Transformer(transformer_config.transform_type).name
                        )(transformer_config)
                        df = transformer.transform(df)

                # store table in staging area
                df = df.drop_duplicates()
                sql_driver_to_method_mapper = {
                    "postgresql": postgres_upsert,
                    "mysql+pymysql": insert_on_duplicate,
                }
                method = sql_driver_to_method_mapper[
                    StagingDBSettings().staging_db_sqlalchemy_driver
                ]
                df.to_sql(
                    name=transformation_pipeline.config.table_name,
                    con=staging_db_engine,
                    schema=transformation_pipeline.config.staging_schema,
                    if_exists="append",
                    index=False,
                    method=method,
                )

    def run_load(self) -> None:
        self.load.load()

    def create_table_if_not_exists(
        self, engine: Engine, table_name: str, columns: dict, schema: str = None
    ) -> None:
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
            if not con.dialect.has_schema(con, schema):
                con.execute(CreateSchema(schema))
            if not engine.dialect.has_table(con, table_name=table_name, schema=schema):
                logging.info(f"Creating table {schema}.{table_name}")
                metadata = MetaData(engine, schema=schema)
                metadata.reflect(bind=engine)
                Table(
                    table_name,
                    metadata,
                    schema=schema,
                    *(
                        Column(
                            column.name,
                            column.type,
                            ForeignKey(column.foreign_key),
                            nullable=column.nullable,
                            primary_key=column.primary_key,
                        )
                        if column.foreign_key is not None
                        else Column(
                            column.name,
                            column.type,
                            nullable=column.nullable,
                            primary_key=column.primary_key,
                        )
                        for column in columns
                    ),
                ).create()
                logging.info(f"Successfully created table {schema}.{table_name}")
