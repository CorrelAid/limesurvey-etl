import os

import pymysql
import pytest
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from testcontainers.mysql import MySqlContainer

from limesurvey_etl.config.extract_config.limesurvey import LimesurveyExtractConfig
from limesurvey_etl.connectors.limesurvey_connect import LimesurveyConnect
from limesurvey_etl.settings.limesurvey_settings import LimesurveySettings


@pytest.fixture(scope="module")
def mariadb_limesurvey_container():
    with MySqlContainer("mariadb:latest") as container:
        yield container


@pytest.fixture(scope="module")
def mariadb_staging_container():
    with MySqlContainer("mariadb:latest") as container:
        yield container


@pytest.fixture(scope="module", autouse=True)
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
        "reporting_db_host": "localhost",
        "reporting_db_name": "staging_db",
        "reporting_db_port": "9000",
        "reporting_db_username": "foobar",
        "reporting_db_password": "secret4321",
    }

    os.environ.update(config)


# Define a fixture to establish a connection to the MariaDB container
@pytest.fixture(scope="module")
def limesurvey_engine(mariadb_limesurvey_container, envconfig) -> Engine:
    limesurvey_db_connect = LimesurveyConnect(LimesurveySettings())
    engine: Engine = limesurvey_db_connect.create_sqlalchemy_engine()
    yield engine


# Create tables with dummy data
@pytest.fixture(scope="module", autouse=True)
def create_tables(limesurvey_engine):
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


# @pytest.fixture(scope="function")
# def limesurvey_settings() -> LimesurveySettings:
#     return LimesurveySettings(lim)
