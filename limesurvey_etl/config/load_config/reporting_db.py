from typing import Literal

from pydantic import BaseModel, Field


class ReportingDBLoadConfig(BaseModel):
    """
    Configuration for loading data into the reporting database.

    Attributes:
        load_type (Literal["reporting_db_load"]): Type of load, should be "reporting_db_load".
        tables (list[str]): Tables to be loaded to the target. Must be in the correct order if foreign keys are used.
        staging_schema (str, optional): If applicable, the name of the schema in the staging area to load the data from.
        target_schema (str, optional): Name of the schema to load the data to.

    """

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
