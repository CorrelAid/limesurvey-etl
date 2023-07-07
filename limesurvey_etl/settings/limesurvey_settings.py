from typing import Optional

from pydantic import BaseSettings, Field


class LimesurveySettings(BaseSettings):
    limesurvey_db_host: str
    limesurvey_db_name: str
    limesurvey_db_port: str
    limesurvey_db_username: str
    limesurvey_db_password: str
    limesurvey_ssh_host: Optional[str]
    limesurvey_ssh_username: Optional[str]
    limesurvey_ssh_password: Optional[str]
    limesurvey_ssh_port: int = Field(22)
