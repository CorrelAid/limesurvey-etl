import logging
import sys
from typing import Literal, Union

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from limesurvey_etl.connectors.base_db_connect import BaseDBConnect
from limesurvey_etl.settings.limesurvey_settings import LimesurveySettings


class LimesurveyConnect(BaseDBConnect):
    def __init__(self, settings: LimesurveySettings) -> None:
        self.db_driver = "mysql+pymysql"
        self.db_host = settings.limesurvey_db_host
        self.db_port = settings.limesurvey_db_port
        self.db_user = settings.limesurvey_db_username
        self.db_password = settings.limesurvey_db_password
        self.db_name = settings.limesurvey_db_name
