import numpy as np
import pandas as pd
import pytest

from limesurvey_etl.config.transform_config.add_columns import AddColumnsConfig
from limesurvey_etl.transform.add_columns import AddColumnsTransform


def test_add_columns_transform(
    surveys_questions_data: pd.DataFrame, add_columns_config: AddColumnsConfig
) -> None:
    transform = AddColumnsTransform(add_columns_config)
    df = transform.transform(surveys_questions_data)
    print(df)
    assert df.equals(
        pd.DataFrame(
            [
                {
                    "survey_id": 1,
                    "title": "Survey 1",
                    "question_id": 1,
                    "question_text": "How satisfied are you with our product?",
                    "city": "Berlin",
                },
                {
                    "survey_id": 1,
                    "title": "Survey 1",
                    "question_id": 2,
                    "question_text": "What can we do to improve our services?",
                    "city": "Berlin",
                },
                {
                    "survey_id": 2,
                    "title": "Survey 2",
                    "question_id": 3,
                    "question_text": "Do you have any comments about our website?",
                    "city": "Berlin",
                },
            ]
        )
    )


def test_add_columns_transform_multiple_columns(
    surveys_questions_data: pd.DataFrame,
    add_columns_config_multiple_columns: AddColumnsConfig,
) -> None:
    transform = AddColumnsTransform(add_columns_config_multiple_columns)
    df = transform.transform(surveys_questions_data)
    assert df.equals(
        pd.DataFrame(
            [
                {
                    "survey_id": 1,
                    "title": "Survey 1",
                    "question_id": 1,
                    "question_text": "How satisfied are you with our product?",
                    "city": np.nan,
                    "country": np.nan,
                },
                {
                    "survey_id": 1,
                    "title": "Survey 1",
                    "question_id": 2,
                    "question_text": "What can we do to improve our services?",
                    "city": np.nan,
                    "country": np.nan,
                },
                {
                    "survey_id": 2,
                    "title": "Survey 2",
                    "question_id": 3,
                    "question_text": "Do you have any comments about our website?",
                    "city": np.nan,
                    "country": np.nan,
                },
            ]
        )
    )


def test_add_column_transform_duplicate_column(
    surveys_questions_data: pd.DataFrame,
    add_columns_config_duplicate_column: AddColumnsConfig,
) -> None:
    transform = AddColumnsTransform(add_columns_config_duplicate_column)
    with pytest.raises(ValueError):
        print(transform.transform(surveys_questions_data))
