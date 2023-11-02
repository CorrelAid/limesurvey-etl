import pandas as pd
import pytest

from limesurvey_etl.config.load_config.reporting_db import ReportingDBLoadConfig
from limesurvey_etl.load.reporting_db import ReportingDBLoad


@pytest.mark.dependency(depends=["test_pipeline_run_all"])
def test_reporting_db_load(reporting_db_load_config: ReportingDBLoadConfig) -> None:
    pass
