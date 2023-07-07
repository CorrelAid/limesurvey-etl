import sys
from typing import Literal, Optional

from pydantic import BaseModel, Field, PrivateAttr, validator


class Join(BaseModel):
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
    # TODO: change type of columns to str
    table_name: str
    columns: list[tuple[str, Optional[str]]]

    @validator("columns")
    @classmethod
    def transform_columns(cls, columns):
        return [
            " AS ".join(column) if column[1] is not None else column[0]
            for column in columns
        ]


class SelectSubsetOfDataConfig(BaseModel):
    transform_type: Literal["select_subset_of_data"]
    source_schema: str
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
