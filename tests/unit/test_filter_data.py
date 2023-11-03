import pandas as pd
import pytest

from limesurvey_etl.config.transform_config.filter_data import FilterDataConfig
from limesurvey_etl.transform.filter_data import FilterDataTransform


def test_filter_data(
    surveys_questions_data: pd.DataFrame, filter_data_config: FilterDataConfig
) -> None:
    transform = FilterDataTransform(filter_data_config)
    df = transform.transform(surveys_questions_data)
    assert df.equals(
        pd.DataFrame(
            [
                {
                    "survey_id": 1,
                    "title": "Survey 1",
                    "question_id": 2,
                    "question_text": "What can we do to improve our services?",
                }
            ]
        )
    )


def test_filter_data_not_contains(
    surveys_questions_data: pd.DataFrame,
    filter_data_config_not_contains: FilterDataConfig,
) -> None:
    transform = FilterDataTransform(filter_data_config_not_contains)
    df = transform.transform(surveys_questions_data)
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
                    "survey_id": 2,
                    "title": "Survey 2",
                    "question_id": 3,
                    "question_text": "Do you have any comments about our website?",
                },
            ]
        )
    )
