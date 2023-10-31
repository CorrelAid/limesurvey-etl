import pandas as pd
import pytest

from limesurvey_etl.config.transform_config.join_with_csv_mapping import (
    JoinWithCSVMappingConfig,
)
from limesurvey_etl.transform.join_with_csv_mapping import JoinWithCSVMappingTransform


def test_join_with_csv_mapping(
    surveys_questions_data: pd.DataFrame,
    join_with_csv_mapping_config: JoinWithCSVMappingConfig,
) -> None:
    transform = JoinWithCSVMappingTransform(join_with_csv_mapping_config)
    df = transform.transform(surveys_questions_data)
    assert df.equals(
        pd.DataFrame(
            [
                {
                    "survey_id": 1,
                    "title": "Survey 1",
                    "question_id": 1,
                    "question_text": "How satisfied are you with our product?",
                    "survey_author": "CFE",
                },
                {
                    "survey_id": 1,
                    "title": "Survey 1",
                    "question_id": 2,
                    "question_text": "What can we do to improve our services?",
                    "survey_author": "CFE",
                },
                {
                    "survey_id": 2,
                    "title": "Survey 2",
                    "question_id": 3,
                    "question_text": "Do you have any comments about our website?",
                    "survey_author": "Another NPO",
                },
            ]
        )
    )
