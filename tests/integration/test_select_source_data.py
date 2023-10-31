import os

import pandas as pd
import pytest

from limesurvey_etl.config.transform_config.select_source_data import (
    SelectSourceDataConfig,
)
from limesurvey_etl.transform.select_source_data import SelectSourceDataTransform


def test_select_source_data(select_source_data_config: SelectSourceDataConfig) -> None:
    staging_schema = os.getenv("STAGING_SCHEMA_NAME")
    transform = SelectSourceDataTransform(
        config=select_source_data_config,
        staging_schema_name=os.getenv("STAGING_SCHEMA_NAME"),
        staging_table_name="",
    )

    print(os.getenv("STAGING_SCHEMA_NAME"))

    df = transform.transform()

    assert df.equals(
        pd.DataFrame(
            [
                {"title": "Survey 1", "description": "This is the first survey"},
                {"title": "Survey 2", "description": "This is the second survey"},
            ]
        )
    )


def test_select_source_data_with_join(
    select_source_data_config_with_join: SelectSourceDataConfig,
) -> None:
    staging_schema = os.getenv("STAGING_SCHEMA")
    transform = SelectSourceDataTransform(
        config=select_source_data_config_with_join,
        staging_schema_name=staging_schema,
        staging_table_name="",
    )

    df = transform.transform()

    assert df.equals(
        pd.DataFrame(
            [
                {
                    "survey_id": 1,
                    "title": "Survey 1",
                    "question_id": 1,
                    "question_text": "How satisfied are you with our product?",
                },
                {
                    "survey_id": 1,
                    "title": "Survey 1",
                    "question_id": 2,
                    "question_text": "What can we do to improve our services?",
                },
                {
                    "survey_id": 2,
                    "title": "Survey 2",
                    "question_id": 3,
                    "question_text": "Do you have any comments about our website?",
                },
            ]
        )
    )
