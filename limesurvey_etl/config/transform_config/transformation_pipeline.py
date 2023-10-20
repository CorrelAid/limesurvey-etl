import sys
from typing import Optional, Sequence, Union

from pydantic import BaseModel, Field, validator
from sqlalchemy.sql.sqltypes import INTEGER, VARCHAR  # noqa

from limesurvey_etl.config.transform_config.add_columns import AddColumnsConfig
from limesurvey_etl.config.transform_config.add_computed_column import (
    AddComputedColumnConfig,
)
from limesurvey_etl.config.transform_config.fill_null_values import FillNullValuesConfig
from limesurvey_etl.config.transform_config.filter_data import FilterDataConfig
from limesurvey_etl.config.transform_config.join_with_csv_mapping import (
    JoinWithCSVMappingConfig,
)
from limesurvey_etl.config.transform_config.rename_columns import RenameColumnsConfig
from limesurvey_etl.config.transform_config.replace_values import ReplaceValuesConfig
from limesurvey_etl.config.transform_config.select_source_data import (
    SelectSourceDataConfig,
)

SQLALCHEMY_TYPES = ["VARCHAR", "INTEGER"]


def str_to_class(classname):
    return getattr(sys.modules[__name__], classname)


class Column(BaseModel):
    """
    Represents a column in a database table.

    Attributes:
        name (str): The name of the column.
        type (str): Valid sqlalchemy data type, such as VARCHAR(255) or INTEGER.
        primary_key (bool): Whether or not the column is a primary key column in the reporting table.
        nullable (bool): Whether or not the column can be Null.
        foreign_key (Optional[str]): The foreign key associated with the column, if any.
    """

    name: str
    type: str = Field(
        ..., description="Valid sqlalchemy data type, such as VARCHAR(255) or INTEGER"
    )
    primary_key: bool = Field(
        False,
        description="Whether or not the column is a primary key column in the reporting table",
    )
    nullable: bool = Field(False, description="Whether or not the column can be Null")
    foreign_key: Optional[str]

    @validator("type")
    @classmethod
    def validate_sqlalchemy_type(cls, type: str):
        base_type = type.split("(")[0]
        if base_type not in SQLALCHEMY_TYPES:
            raise ValueError(f"Must be one of {SQLALCHEMY_TYPES}, got {base_type}.")
        column_type_list = type.split("(")
        type = str_to_class(base_type)
        if len(column_type_list) > 1:
            type = type(int(column_type_list[1][:-1]))
        return type


class TransformationPipelineConfig(BaseModel):
    """
    Configuration for a transformation pipeline.

    Attributes:
        table_name (str): Name of the table to be created in the staging area.
        transform_steps (Sequence[Union[AddColumnsConfig,FillNullValuesConfig,FilterDataConfig,JoinWithCSVMappingConfig,RenameColumnsConfig,ReplaceValuesConfig,AddComputedColumnConfig]]): Sequence of transform step configs.
            If None, only an empty table is created.
        staging_schema (str): Name of the schema to store data in the staging area.
        columns (list[Column]): List of column definitions relevant in case the staging table does not yet exists in the database.
            See Column class for relevant items for the config dicts.
            If None (default), table is created directly from pandas df.
        source_data (SelectSourceDataConfig): Source data from the extracted data the transformations should be applied to.

    """

    table_name: str = Field(
        ..., description="Name of the table to be created in the staging area."
    )
    transform_steps: Sequence[
        Union[
            AddColumnsConfig,
            FillNullValuesConfig,
            FilterDataConfig,
            JoinWithCSVMappingConfig,
            RenameColumnsConfig,
            ReplaceValuesConfig,
            AddComputedColumnConfig,
        ]
    ] = Field(
        None,
        description="Sequence of transform step configs. If None, only an empty table is created.",
    )
    staging_schema: str
    columns: list[Column] = Field(
        None,
        description="List of dictionaries containing the column specs used when creating a new table in the database. Keys are column names, values are configs. See Column class for relevant items for the config dicts. If None (default), table is created directly from pandas df.",
    )
    source_data: SelectSourceDataConfig = Field(
        None, description="Data the transformations should be applied to"
    )
