import pandas as pd
import pytest

from limesurvey_etl.config.transform_config.fill_null_values import FillNullValuesConfig
from limesurvey_etl.transform.fill_null_values import FillNullValuesTransform


def test_fill_null_values(
    surveys_questions_data_with_null_values: pd.DataFrame,
    fill_null_values_config: FillNullValuesConfig,
) -> None:
    transform = FillNullValuesTransform(fill_null_values_config)
    df = transform.transform(surveys_questions_data_with_null_values)

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
