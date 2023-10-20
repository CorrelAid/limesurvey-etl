from pathlib import Path
from typing import Literal, Union

from pydantic import BaseModel, Field, root_validator, validator


class JoinWithCSVMappingConfig(BaseModel):
    """
    Configuration for joining data with a CSV mapping.

    Attributes:
        transform_type (Literal["join_with_csv_mapping"]): Type of transformation, should be "join_with_csv_mapping".
        mapping_path (str): Path to the CSV mapping file.
        mapping_delimiter (str, optional): Delimiter used in the CSV mapping file. Default is ",".
        keep_columns (list[str], optional): List of columns to keep from mapping table.
            If None, all columns are kept.
        how (Union[Literal["left"], Literal["right"], Literal["outer"], Literal["inner"], Literal["cross"]], optional):
            Type of join to be performed. Default is "inner".
        on (Union[str, list[str]], optional): Column names to join on. If None, then both left_on and right_on must be specified.
        left_on (Union[str, list[str]], optional): Column names to join on in the original data frame.
        right_on (Union[str, list[str]], optional): Column names to join on in the mapping data frame.
    """

    transform_type: Literal["join_with_csv_mapping"]
    mapping_path: str
    mapping_delimiter: str = Field(",", description="Delimiter")
    keep_columns: list[str] = Field(
        None,
        description="List of columns to keep from mapping table. If None, all columns are kept",
    )
    how: Union[
        Literal["left"],
        Literal["right"],
        Literal["outer"],
        Literal["inner"],
        Literal["cross"],
    ] = Field("inner", description="Type of join to be performed")
    on: Union[str, list[str]] = Field(
        None,
        description="Column names to join on. If None, then both left_on and right_on must be specified.",
    )
    left_on: Union[str, list[str]] = Field(
        None, description="Column names to join on in the original data frame"
    )
    right_on: Union[str, list[str]] = Field(
        None, description="Column names to join on in the mapping data frame."
    )

    @validator("mapping_path")
    @classmethod
    def transform_mapping_path(cls, path):
        return Path(path)

    @root_validator()
    @classmethod
    def validate_join_cols(cls, field_values):
        on = field_values["on"]
        left_on = field_values["left_on"]
        right_on = field_values["right_on"]
        if on is None and left_on is None and right_on is None:
            raise ValueError(
                "Either 'on' or both 'left_on' and 'right_on' must not be None."
            )
        if on is not None and (left_on is not None or right_on is not None):
            raise ValueError("If using 'on', 'left_on' and 'right_on' must be None")
        if (left_on is not None and right_on is None) or (
            left_on is None and right_on is not None
        ):
            raise ValueError("Both 'right_on' and 'left_on' must be set.")
        return field_values
