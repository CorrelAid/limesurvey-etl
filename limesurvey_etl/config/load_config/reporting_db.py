from typing import Literal

from pydantic import BaseModel, Field


class ReportingDBLoadConfig(BaseModel):
    load_type: Literal["reporting_db_load"]
    tables: list[str] = Field(
        ...,
        description="Tables to be loaded to target. Must be in the correct order if foreign keys are used.",
    )
    staging_schema: str = Field(
        None,
        description="If applicable: name of the schema in the staging area to load the data from",
    )
    target_schema: str = Field(
        None, description="Name of the schema to load the data to."
    )
