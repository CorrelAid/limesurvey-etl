from typing import Literal

from pydantic import BaseModel, Field


class LimesurveyExtractConfig(BaseModel):
    """
    Configuration for extracting data from LimeSurvey.

    Attributes:
        extract_type (Literal["limesurvey_extract"]): Type of extraction, should be "limesurvey_extract".
        tables (list[str]): List of tables to be extracted.
        staging_schema (str, optional): Name of the schema to store raw data in the staging area. Default is "raw".
        use_ssh (bool, optional): Whether to ssh into a server before running extract step. Default is True.
    """

    extract_type: Literal["limesurvey_extract"]
    tables: list[str] = Field(..., description="List of tables to be extracted")
    staging_schema: str = Field(
        "raw", description="Name of the schema to store raw data in the staging area."
    )
    use_ssh: bool = Field(
        True, description="Whether to ssh into a server before running extract step."
    )
