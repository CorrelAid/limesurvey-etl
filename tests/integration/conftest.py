import os
from pathlib import Path
from typing import Any, Generator

import pytest
from sqlalchemy.engine import Engine
from testcontainers.mysql import MySqlContainer

from limesurvey_etl.config.extract_config.limesurvey import LimesurveyExtractConfig
from limesurvey_etl.config.load_config.reporting_db import ReportingDBLoadConfig
from limesurvey_etl.config.transform_config.select_source_data import (
    SelectSourceDataConfig,
)
from limesurvey_etl.connectors.limesurvey_connect import LimesurveyConnect
from limesurvey_etl.connectors.reporting_db_connect import ReportingDBConnect
from limesurvey_etl.connectors.staging_db_connect import StagingDBConnect
from limesurvey_etl.settings.limesurvey_settings import LimesurveySettings
from limesurvey_etl.settings.reporting_db_settings import ReportingDBSettings
from limesurvey_etl.settings.staging_db_settings import StagingDBSettings


@pytest.fixture(scope="session")
def mariadb_limesurvey_container():
    with MySqlContainer("mariadb:10.11.5") as container:
        yield container


@pytest.fixture(scope="session")
def mariadb_staging_container():
    with MySqlContainer("mariadb:10.11.5") as container:
        yield container


@pytest.fixture(scope="session", autouse=True)
def envconfig(mariadb_limesurvey_container, mariadb_staging_container) -> None:
    config = {
        "limesurvey_db_host": mariadb_limesurvey_container.get_container_host_ip(),
        "limesurvey_db_name": mariadb_limesurvey_container.MYSQL_DATABASE,
        "limesurvey_db_port": str(
            mariadb_limesurvey_container.get_exposed_port(
                mariadb_limesurvey_container.port_to_expose
            )
        ),
        "limesurvey_db_username": "root",  # mariadb_limesurvey_container.MYSQL_USER,
        "limesurvey_db_password": mariadb_limesurvey_container.MYSQL_PASSWORD,
        "staging_db_host": mariadb_staging_container.get_container_host_ip(),
        "staging_db_name": mariadb_staging_container.MYSQL_DATABASE,
        "staging_db_port": str(
            mariadb_staging_container.get_exposed_port(
                mariadb_limesurvey_container.port_to_expose
            )
        ),
        "staging_db_username": "root",  # mariadb_staging_container.MYSQL_USER,
        "staging_db_password": mariadb_staging_container.MYSQL_ROOT_PASSWORD,
        "staging_db_sqlalchemy_driver": "mysql+pymysql",
        "reporting_db_host": mariadb_staging_container.get_container_host_ip(),
        "reporting_db_name": mariadb_staging_container.MYSQL_DATABASE,
        "reporting_db_port": str(
            mariadb_staging_container.get_exposed_port(
                mariadb_limesurvey_container.port_to_expose
            )
        ),
        "reporting_db_username": "root",
        "reporting_db_password": mariadb_staging_container.MYSQL_ROOT_PASSWORD,
        "STAGING_SCHEMA_NAME": "staging",
    }

    os.environ.update(config)


# Define a fixture to establish a connection to the MariaDB container
@pytest.fixture(scope="session")
def limesurvey_engine(mariadb_limesurvey_container, envconfig) -> Engine:
    limesurvey_db_connect = LimesurveyConnect(LimesurveySettings())
    engine: Engine = limesurvey_db_connect.create_sqlalchemy_engine()
    yield engine


@pytest.fixture(scope="session")
def staging_db_engine(mariadb_staging_container, envconfig) -> Engine:
    staging_db_connect = StagingDBConnect(StagingDBSettings())
    engine: Engine = staging_db_connect.create_sqlalchemy_engine()
    return engine


# Create staging table with dummy data
@pytest.fixture(scope="session", autouse=True)
def create_tables_staging(staging_db_engine) -> None:
    with staging_db_engine.connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS staging_test (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL
            )
            """
        )

        conn.execute(
            """
            INSERT INTO staging_test (name) VALUES
            ('Francesca'),
            ('Paolo')
            """
        )


# Create limesurvey tables with dummy data
@pytest.fixture(scope="session", autouse=True)
def create_tables_limesurvey(limesurvey_engine):
    with limesurvey_engine.connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS surveys (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS questions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                survey_id INT,
                question_text TEXT,
                FOREIGN KEY (survey_id) REFERENCES surveys(id)
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS responses (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                survey_id INT,
                question_id INT,
                response_text TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (survey_id) REFERENCES surveys(id),
                FOREIGN KEY (question_id) REFERENCES questions(id)
            )
            """
        )

        conn.execute(
            """
            INSERT INTO users (name, email) VALUES
            ('John Doe', 'john.doe@example.com'),
            ('Jane Smith', 'jane.smith@example.com')
            """
        )

        conn.execute(
            """
            INSERT INTO surveys (title, description) VALUES
            ('Survey 1', 'This is the first survey'),
            ('Survey 2', 'This is the second survey')
            """
        )

        conn.execute(
            """
            INSERT INTO questions (survey_id, question_text) VALUES
            (1, 'How satisfied are you with our product?'),
            (1, 'What can we do to improve our services?'),
            (2, 'Do you have any comments about our website?')
            """
        )


@pytest.fixture(scope="function")
def limesurvey_extract_config() -> LimesurveyExtractConfig:
    return LimesurveyExtractConfig(
        extract_type="limesurvey_extract",
        tables=["surveys", "users", "questions", "responses"],
        use_ssh=False,
    )


@pytest.fixture(scope="function")
def select_source_data_config(
    limesurvey_extract_config: LimesurveyExtractConfig, envconfig
) -> SelectSourceDataConfig:
    return SelectSourceDataConfig(
        source_schema=limesurvey_extract_config.staging_schema,
        source_tables=[
            {"table_name": "surveys", "columns": ["title", "description"]},
        ],
    )


@pytest.fixture(scope="function")
def select_source_data_config_with_join(
    limesurvey_extract_config: LimesurveyExtractConfig, envconfig
) -> SelectSourceDataConfig:
    return SelectSourceDataConfig(
        source_schema=limesurvey_extract_config.staging_schema,
        source_tables=[
            {"table_name": "surveys", "columns": ["id AS survey_id", "title"]},
            {
                "table_name": "questions",
                "columns": ["id AS question_id", "question_text"],
            },
        ],
        join={
            "type": "RIGHT JOIN",
            "left_table": "surveys",
            "right_table": "questions",
            "left_on": "id",
            "right_on": "survey_id",
        },
    )


@pytest.fixture(scope="function")
def reporting_db_engine() -> Engine:
    reporting_db_connect = ReportingDBConnect(ReportingDBSettings())
    reporting_db_engine: Engine = reporting_db_connect.create_sqlalchemy_engine()
    return reporting_db_engine


@pytest.fixture(scope="function")
def reporting_db_load_config(
    mariadb_staging_container: Generator[MySqlContainer, Any, None],
) -> ReportingDBLoadConfig:
    return ReportingDBLoadConfig(
        load_type="reporting_db_load",
        tables=["staging_test"],
        staging_schema=mariadb_staging_container.MYSQL_DATABASE,
        target_schema="reporting",
    )


@pytest.fixture(scope="function")
def pipeline_config_file(envconfig) -> Path:
    return Path("tests/integration/test_configs/pipeline_config.yaml")
