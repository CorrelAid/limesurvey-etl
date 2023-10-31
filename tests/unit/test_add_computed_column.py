import pandas as pd
import pytest

from limesurvey_etl.config.transform_config.add_computed_column import (
    AddComputedColumnConfig,
)
from limesurvey_etl.transform.add_computed_column import AddComputedColumnTransform


def test_add_computed_column(
    surveys_questions_data: pd.DataFrame,
    add_computed_column_config: AddComputedColumnConfig,
) -> None:
    transform = AddComputedColumnTransform(add_computed_column_config)
    df = transform.transform(surveys_questions_data)

    assert df.equals(
        pd.DataFrame(
            [
                {
                    "survey_id": 1,
                    "title": "Survey 1",
                    "question_id_and_text": "1_How satisfied are you with our product?",
                },
                {
                    "survey_id": 1,
                    "title": "Survey 1",
                    "question_id_and_text": "2_What can we do to improve our services?",
                },
                {
                    "survey_id": 2,
                    "title": "Survey 2",
                    "question_id_and_text": "3_Do you have any comments about our website?",
                },
            ]
        )
    )
