import logging
import sys
from enum import Enum
from pathlib import Path
from typing import Any

import pandas as pd
import yaml
from sshtunnel import SSHTunnelForwarder

from limesurvey_etl.config.extract_config.limesurvey import LimesurveyExtractConfig
from limesurvey_etl.config.load_config.reporting_db import ReportingDBLoadConfig
from limesurvey_etl.config.transform_config.select_subset_of_data import (
    SelectSubsetOfDataConfig,
)
from limesurvey_etl.config.transform_config.transformation_pipeline import (
    TransformationPipelineConfig,
)
from limesurvey_etl.etl_pipeline import Pipeline
from limesurvey_etl.extract.base import BaseExtract
from limesurvey_etl.extract.limesurvey import LimesurveyExtract
from limesurvey_etl.load.base import BaseLoad
from limesurvey_etl.load.reporting_db import ReportingDBLoad
from limesurvey_etl.transform.add_columns import AddColumnsTransform
from limesurvey_etl.transform.fill_null_values import FillNullValuesTransform
from limesurvey_etl.transform.filter_data import FilterDataTransform
from limesurvey_etl.transform.join_with_csv_mapping import JoinWithCSVMappingTransform
from limesurvey_etl.transform.rename_columns import RenameColumnsTransform
from limesurvey_etl.transform.select_subset_of_data import SelectSubsetOfDataTransform


def str_to_class(classname: str) -> Any:
    return getattr(sys.modules[__name__], classname)


class Extractor(Enum):
    LimesurveyExtract = "limesurvey_extract"


class Transformer(Enum):
    AddColumnsTransform = "add_columns_transform"
    SelectSubsetOfDataTransform = "select_subset_of_data_transform"


class Loader(Enum):
    ReportingDBLoad = "reporting_db_load"


def get_extractor(config: dict) -> BaseExtract:
    extract_type = config["extract_type"]
    extract_config = str_to_class(Extractor(extract_type).name + "Config")(**config)
    extractor = str_to_class(Extractor(extract_type).name)(extract_config)

    return extractor


def get_transformation_pipelines(config: dict) -> TransformationPipelineConfig:
    return [transformation_pipeline for transformation_pipeline in config]


def get_loader(config: dict) -> BaseLoad:
    load_type = config["load_type"]
    loader_config = str_to_class(Loader(load_type).name + "Config")(**config)
    loader = str_to_class(Loader(load_type).name)(loader_config)

    return loader


def get_pipeline(config_file_path: Path) -> Pipeline:
    if not config_file_path.exists():
        raise ValueError(
            f"config_file_path {config_file_path.resolve()} does not exist!"
        )

    with open(str(config_file_path), "r") as config_file:
        config = yaml.safe_load(config_file)

    # build pipeline
    extractor = get_extractor(config["extract"])
    transformation_pipelines = get_transformation_pipelines(
        config["transformation_pipelines"]
    )
    loader = get_loader(config["load"])

    pipeline = Pipeline(
        extract=extractor,
        transformation_pipelines=transformation_pipelines,
        load=loader,
    )

    return pipeline


def main():
    with SSHTunnelForwarder(
        ("116.203.20.255", 22),
        ssh_username="ls_test",
        ssh_password="XLbhV01AuqOENead9uuu",
        remote_bind_address=("127.0.0.1", 3306),
        local_bind_address=("127.0.0.1", 3306),
    ):
        try:
            # parse config
            pipeline = get_pipeline(Path("configs/test.yaml"))

            pipeline.run_extract()

            df = pipeline.run_transform()

            pipeline.run_load()

        except Exception as e:
            logging.critical(f"An uncaught exception occured: {e}", exc_info=e)

    #     limesurvey_extractor_config = LimesurveyExtractConfig(
    #         **{
    #             "extract_type": "limesurvey_extract",
    #             "tables": [
    #                 "lime_group_l10ns",
    #                 "lime_questions",
    #                 "lime_question_l10ns",
    #                 "lime_survey_977429",
    #             ],
    #         }
    #     )

    #     limesurvey_extractor = LimesurveyExtract(limesurvey_extractor_config)
    #     limesurvey_extractor.extract()

    # # transform
    # transformation_pipeline = {
    #     "table_name": "test",
    #     "staging_schema": "test",
    #     "transform_steps": [
    #         {
    #             "transform_type": "select_subset_of_data",
    #             "columns": [
    #                 {
    #                     "name": "question_group_id",
    #                     "type": "INTEGER",
    #                     "primary_key": True,
    #                     "nullable": False,
    #                 },
    #                 {"name": "question_group_name", "type": "VARCHAR(255)"},
    #                 {"name": "description", "type": "VARCHAR(255)"},
    #             ],
    #             "source_tables": [
    #                 ("lime_group_l10ns", ["gid", "group_name", "description"])
    #             ],
    #             "source_schema": "raw",
    #             "target_table_name": "question_groups",
    #             "target_schema": "reporting",
    #         }
    #     ],
    # }

    # transform_steps = [
    #     SelectSubsetOfDataConfig(**transform_step)
    #     for transform_step in transformation_pipeline["transform_steps"]
    # ]
    # df = SelectSubsetOfDataTransform(transform_steps[0]).transform()
    # for transform in transform_steps[1:]:
    #     df = transform.transform(df)

    # # subset_transformer = SelectSubsetOfDataTransform(subset_transformer_config)
    # # df = subset_transformer.transform()
    # print(df.head())


if __name__ == "__main__":
    main()
