from typing import Literal, Union

from pydantic import BaseSettings


class ReportingDBSettings(BaseSettings):
    reporting_db_sqlalchemy_driver: Union[
        Literal["mysql+pymysql"], Literal["postgresql"]
    ] = "mysql+pymysql"
    reporting_db_host: str
    reporting_db_name: str
    reporting_db_port: str
    reporting_db_username: str
    reporting_db_password: str
