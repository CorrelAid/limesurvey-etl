import pandas as pd
import pytest
from sqlalchemy.engine import Engine

from limesurvey_etl.config.load_config.reporting_db import ReportingDBLoadConfig
from limesurvey_etl.load.reporting_db import ReportingDBLoad


def test_reporting_db_load(
    reporting_db_load_config: ReportingDBLoadConfig, reporting_db_engine: Engine
) -> None:
    load = ReportingDBLoad(reporting_db_load_config)
    load.load()

    with reporting_db_engine.connect() as conn:
        staging_test = conn.execute(f"SELECT * FROM reporting.staging_test").all()
        assert staging_test == [(1, "Francesca"), (2, "Paolo")]
