import sys
from typing import Literal, Optional

from pydantic import BaseModel, Field, PrivateAttr, validator


class Join(BaseModel):
    """
    Represents a join operation.

    Attributes:
        type (str): Type of join operation.
        left_table (str): Name of the join's left table.
        right_table (str): Name of the join's right table.
        left_on (Optional[str]): Column name for joining on the left table.
        right_on (Optional[str]): Column name for joining on the right table."""

    type: str
    left_table: str = Field(..., description="Name of the join's left table.")
    right_table: str = Field(..., description="Name of the join's right table.")
    left_on: Optional[str]
    right_on: Optional[str]

    @validator("type")
    @classmethod
    def validate_join_type(cls, t):
        join_types = ["JOIN", "LEFT JOIN", "RIGHT JOIN", "INNER JOIN", "OUTTER JOIN"]
        if not t.upper() in join_types:
            raise ValueError(f"Join type must be one of: {join_types}")
        return t


class SourceTable(BaseModel):
    """
    Represents a source table.

    Attributes:
        table_name (str): Name of the source table.
        columns (list[str]): List of column names in the source table.

    """

    table_name: str
    columns: list[str]


class SelectSourceDataConfig(BaseModel):
    """
    Configuration for selecting a subset of data from source tables.

    Attributes:
        source_schema (str): Name of the database schema the source data is stored in. Defaults to 'raw'
        source_tables (list[SourceTable]): List of source tables with their columns to be selected.
        join (Join, optional): Join configuration based on the Join class.
        filter (str, optional): Optional SQL filter clause.

    """

    source_schema: str = Field(
        "raw",
        description="Name of the database schema the source data is stored in. Defaults to 'raw'",
    )
    source_tables: list[SourceTable] = Field(
        ...,
        description="List of tuples containing the source table name and a list of the columns to be selected",
    )
    join: Join = Field(
        None,
        description="Dictionary containing join config based on Join class. Currently only supports one join",
    )
    filter: str = Field(
        None,
        description="Optional SQL filter clause, e.g., 'WHERE col_1=1 AND col_2=2' or, if join involved, 'WHERE left_table.col_1=right_table.col_1",
    )
