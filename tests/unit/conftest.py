import numpy as np
import pandas as pd
import pytest

from limesurvey_etl.config.transform_config.add_columns import AddColumnsConfig
from limesurvey_etl.config.transform_config.add_computed_column import (
    AddComputedColumnConfig,
)
from limesurvey_etl.config.transform_config.fill_null_values import FillNullValuesConfig
from limesurvey_etl.config.transform_config.filter_data import FilterDataConfig


@pytest.fixture(scope="function")
def surveys_questions_data() -> pd.DataFrame:
    return pd.DataFrame(
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


@pytest.fixture(scope="function")
def add_columns_config() -> AddColumnsConfig:
    return AddColumnsConfig(
        transform_type="add_columns", column_names="city", default_value="Berlin"
    )


@pytest.fixture(scope="function")
def add_columns_config_multiple_columns() -> AddColumnsConfig:
    return AddColumnsConfig(
        transform_type="add_columns", column_names=["city", "country"]
    )


@pytest.fixture(scope="function")
def add_columns_config_duplicate_column() -> AddColumnsConfig:
    return AddColumnsConfig(transform_type="add_columns", column_names="survey_id")


@pytest.fixture(scope="function")
def add_computed_column_config() -> AddComputedColumnConfig:
    return AddComputedColumnConfig(
        transform_type="add_computed_column",
        column_name="question_id_and_text",
        input_columns=["question_id", "question_text"],
        operator={"name": "concat", "separator": "_"},
        drop_input_columns="all",
    )


@pytest.fixture(scope="function")
def fill_null_values_config() -> FillNullValuesConfig:
    return FillNullValuesConfig(
        transform_type="fill_null_values",
        column_name="city",
        value="Berlin",
    )


@pytest.fixture(scope="function")
def surveys_questions_data_with_null_values() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "survey_id": 1,
                "title": "Survey 1",
                "question_id": 1,
                "question_text": "How satisfied are you with our product?",
                "city": np.nan,
            },
            {
                "survey_id": 1,
                "title": "Survey 1",
                "question_id": 2,
                "question_text": "What can we do to improve our services?",
                "city": np.nan,
            },
            {
                "survey_id": 2,
                "title": "Survey 2",
                "question_id": 3,
                "question_text": "Do you have any comments about our website?",
                "city": np.nan,
            },
        ]
    )


@pytest.fixture(scope="function")
def filter_data_config() -> FilterDataConfig:
    return FilterDataConfig(
        transform_type="filter_data",
        conditions=[
            {"column": "survey_id", "value": "1", "operator": "=="},
            {"column": "question_id", "value": 1, "operator": ">"},
        ],
        logical_operator="AND",
    )
