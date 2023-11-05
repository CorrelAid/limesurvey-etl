import pandas as pd
import pytest

from limesurvey_etl.config.transform_config.cast_data_type import CastDataTypeConfig
from limesurvey_etl.transform.cast_data_type import CastDataTypeTransform


def test_cast_data_type(
    cast_data_type_config: CastDataTypeConfig, surveys_questions_data: pd.DataFrame
) -> None:
    transform = CastDataTypeTransform(cast_data_type_config)
    assert surveys_questions_data.question_id.dtype == int

    df = transform.transform(surveys_questions_data)

    assert df["question_id"].dtype == object
