from typing import Literal, Union

from pydantic import BaseSettings


class StagingDBSettings(BaseSettings):
    staging_db_sqlalchemy_driver: Union[
        Literal["mysql+pymysql"], Literal["postgresql"]
    ] = "mysql+pymysql"
    staging_db_host: str
    staging_db_name: str
    staging_db_port: str
    staging_db_username: str
    staging_db_password: str
