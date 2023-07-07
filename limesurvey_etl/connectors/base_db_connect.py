import logging
import sys
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseSettings
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

S = TypeVar("S", bound=BaseSettings)


class BaseDBConnect(Generic[S]):
    """
    Base class for all database connects.
    """

    def __init__(self, settings: S) -> None:
        self.settings = settings

    def create_sqlalchemy_engine(self) -> Engine:
        """
        Connects to a database and returns a SQLAlchemy engine.
        :return: A SQLAlchemy engine.
        :rtype: sqlalchemy.engine.Engine
        """
        print(self.__dir__())
        try:
            logging.info("Connecting to DB")
            url = (
                f"{self.db_driver}://{self.db_user}"
                f":{self.db_password}"
                f"@{self.db_host}"
                f":{self.db_port}"
                f"/{self.db_name}"
            )
            engine = create_engine(url, echo=True)
            logging.info("Connection to DB established successfully")
        except SQLAlchemyError as e:
            logging.critical(f"Error connecting to DB: {e}")
            raise
        else:
            return engine
