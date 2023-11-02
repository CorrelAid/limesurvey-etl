from pathlib import Path

import pandas as pd
import pytest

from limesurvey_etl.etl_pipeline import Pipeline


@pytest.mark.dependency()
def test_pipeline_run_all(pipeline_config_file: Path) -> None:
    pipeline = Pipeline.get_pipeline(pipeline_config_file)
    pipeline.run_all()
