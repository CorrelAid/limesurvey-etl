import pandas as pd
import pytest

from limesurvey_etl.config.transform_config.melt_data import MeltDataConfig
from limesurvey_etl.transform.melt_data import MeltDataTransform


def test_melt_data(
    melt_data_config: MeltDataConfig, surveys_questions_data: pd.DataFrame
) -> None:
    transform = MeltDataTransform(melt_data_config)
    df = transform.transform(surveys_questions_data)

    assert df.equals(
        pd.DataFrame(
            [
                {"survey_id": 1, "name": "title", "code": "Survey 1"},
                {"survey_id": 1, "name": "title", "code": "Survey 1"},
                {"survey_id": 2, "name": "title", "code": "Survey 2"},
            ]
        )
    )
