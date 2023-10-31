import pandas as pd
import pytest

from limesurvey_etl.config.transform_config.rename_columns import RenameColumnsConfig
from limesurvey_etl.transform.rename_columns import RenameColumnsTransform


def test_rename_columns(
    surveys_questions_data: pd.DataFrame, rename_columns_config: RenameColumnsConfig
) -> None:
    transform = RenameColumnsTransform(rename_columns_config)
    df = transform.transform(surveys_questions_data)

    assert df.equals(
        pd.DataFrame(
            [
                {
                    "survey_id": 1,
                    "survey_name": "Survey 1",
                    "question_id": 1,
                    "question_text": "How satisfied are you with our product?",
                },
                {
                    "survey_id": 1,
                    "survey_name": "Survey 1",
                    "question_id": 2,
                    "question_text": "What can we do to improve our services?",
                },
                {
                    "survey_id": 2,
                    "survey_name": "Survey 2",
                    "question_id": 3,
                    "question_text": "Do you have any comments about our website?",
                },
            ]
        )
    )
