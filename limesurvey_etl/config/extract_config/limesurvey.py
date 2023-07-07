from typing import Literal

from pydantic import BaseModel, Field


class LimesurveyExtractConfig(BaseModel):
    extract_type: Literal["limesurvey_extract"]
    tables: list[str] = Field(..., description="List of tables to be extracted")
    staging_schema: str = Field(
        None, description="Name of the schema to store raw data in the staging area."
    )
    use_ssh: bool = Field(
        True, description="Whether to ssh into a server before running extract step."
    )
