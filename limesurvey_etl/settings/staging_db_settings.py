from typing import Literal, Union

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings


class StagingDBSettings(BaseSettings):
    staging_db_sqlalchemy_driver: Union[
        Literal["mysql+pymysql"], Literal["postgresql"]
    ] = Field(
        "postgresql",
        alias=AliasChoices(
            "target_db_sqlalchemy_driver", "staging_db_sqlalchemy_driver"
        ),
    )
    staging_db_host: str = Field(
        "limesurvey_postgres", alias=AliasChoices("target_db_host", "staging_db_host")
    )
    staging_db_name: str = Field(
        ..., alias=AliasChoices("target_db_name", "staging_db_name")
    )
    staging_db_port: str = Field(
        "5432", alias=AliasChoices("target_db_port", "staging_db_port")
    )
    staging_db_username: str = Field(
        ..., alias=AliasChoices("target_db_username", "staging_db_username")
    )
    staging_db_password: str = Field(
        ..., alias=AliasChoices("target_db_password", "staging_db_password")
    )
