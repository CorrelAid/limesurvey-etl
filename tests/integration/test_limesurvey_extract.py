# tests/test_limesurvey_extract.py

import logging
from unittest.mock import MagicMock

import pandas as pd
from sqlalchemy.engine import Engine

from limesurvey_etl.config.extract_config.limesurvey import LimesurveyExtractConfig
from limesurvey_etl.connectors.staging_db_connect import StagingDBConnect
from limesurvey_etl.extract.limesurvey import LimesurveyExtract
from limesurvey_etl.settings.staging_db_settings import StagingDBSettings


def test_get_staging_db_engine(limesurvey_extract_config):
    extractor = LimesurveyExtract(limesurvey_extract_config)
    print("extractor: ", extractor)
    engine = extractor._get_staging_db_engine()

    assert engine is not None


def test_extract_data(limesurvey_extract_config: LimesurveyExtractConfig):
    extractor = LimesurveyExtract(limesurvey_extract_config)

    # Mocking the _extract_data method
    extractor.extract()

    staging_db_connect = StagingDBConnect(StagingDBSettings())
    engine = staging_db_connect.create_sqlalchemy_engine()

    with engine.connect() as conn:
        # conn.execute(f"USE {limesurvey_extract_config.staging_schema}")

        users = conn.execute(
            f"SELECT * FROM {limesurvey_extract_config.staging_schema}.users"
        ).all()
        assert len(users) == 2

        surveys = conn.execute(
            f"SELECT * FROM {limesurvey_extract_config.staging_schema}.surveys"
        ).all()
        assert len(surveys) == 2

        questions = conn.execute(
            f"SELECT * FROM {limesurvey_extract_config.staging_schema}.questions"
        ).all()
        assert len(questions) == 3

        responses = conn.execute(
            f"SELECT * FROM {limesurvey_extract_config.staging_schema}.responses"
        ).all()
        assert len(responses) == 0  # No responses in this example
