from pathlib import Path

import pytest
from sqlalchemy.engine import Engine

from limesurvey_etl.etl_pipeline import Pipeline


def test_pipeline_run_all(
    pipeline_config_file: Path, reporting_db_engine: Engine
) -> None:
    pipeline = Pipeline.get_pipeline(pipeline_config_file)
    pipeline.run_all()

    with reporting_db_engine.connect() as conn:
        surveys = conn.execute("SELECT * FROM reporting.surveys_staging").all()
        questions = conn.execute("SELECT * FROM reporting.questions_staging").all()

    assert surveys == [
        (1, "Survey 1", "This is the first survey"),
        (2, "Survey 2", "This is the second survey"),
    ]
    assert questions == [
        (1, 1, "How satisfied are you with our product?"),
        (2, 1, "What can we do to improve our services?"),
        (3, 2, "Do you have any comments about our website?"),
    ]
