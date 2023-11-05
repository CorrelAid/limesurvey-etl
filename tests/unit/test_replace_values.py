import pandas as pd
import pytest

from limesurvey_etl.config.transform_config.replace_values import ReplaceValuesConfig
from limesurvey_etl.transform.replace_values import ReplaceValuesTransform


def test_replace_values(
    replace_values_config: ReplaceValuesConfig, surveys_questions_data: pd.DataFrame
) -> None:
    transform = ReplaceValuesTransform(replace_values_config)
    df = transform.transform(surveys_questions_data)

    assert df.equals(
        pd.DataFrame(
            [
                {
                    "survey_id": 1,
                    "title": "Questionnaire 1",
                    "question_id": 1,
                    "question_text": "How satisfied are you with our product?",
                },
                {
                    "survey_id": 1,
                    "title": "Questionnaire 1",
                    "question_id": 2,
                    "question_text": "What can we do to improve our services?",
                },
                {
                    "survey_id": 2,
                    "title": "Questionnaire 2",
                    "question_id": 3,
                    "question_text": "Do you have any comments about our website?",
                },
            ]
        )
    )
