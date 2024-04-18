from typing import Literal, Union

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings


class ReportingDBSettings(BaseSettings):
    reporting_db_sqlalchemy_driver: Union[
        Literal["mysql+pymysql"], Literal["postgresql"]
    ] = Field(
        "postgresql",
        alias=AliasChoices(
            "target_db_sqlalchemy_driver", "reporting_db_sqlalchemy_driver"
        ),
    )
    reporting_db_host: str = Field(
        "limesurvey_postgres", alias=AliasChoices("target_db_host", "reporting_db_host")
    )
    reporting_db_name: str = Field(
        ..., alias=AliasChoices("reporting_db_name", "target_db_name")
    )
    reporting_db_port: str = Field(
        "5432", alias=AliasChoices("target_db_port", "reporting_db_port")
    )
    reporting_db_username: str = Field(
        ..., alias=AliasChoices("reporting_db_username", "target_db_username")
    )
    reporting_db_password: str = Field(
        ..., alias=AliasChoices("reporting_db_password", "target_db_password")
    )
