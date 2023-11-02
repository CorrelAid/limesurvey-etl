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


def test_filter_data_contains(
    surveys_questions_data: pd.DataFrame, filter_data_config_contains: FilterDataConfig
) -> None:
    transform = FilterDataTransform(filter_data_config_contains)
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
