from typing import Literal, Union

from pydantic import BaseModel, Field, root_validator


class FillNullValuesConfig(BaseModel):
    """
    Configuration for filling null values in a column.

    Attributes:
        transform_type (Literal["fill_null_values"]): Type of transformation, should be "fill_null_values".
        column_name (str): Name of the column in which Null values should be replaced.
        value (Union[str, int, float, bool], optional): Value to replace Null values with.
        method (Union[Literal["backfill"], Literal["ffill"]], optional):
            Method to use for filling Null values in Column.
            'ffill' -> propagate last valid observation forward to next valid.
            'backfill' -> use next valid observation to fill gap.
    """

    transform_type: Literal["fill_null_values"]
    column_name: str = Field(
        ..., description="Name of the column in which Null values should be raplaced."
    )
    value: Union[str, int, float, bool] = Field(
        None, description="Value to replace Null values with."
    )
    method: Union[Literal["backfill"], Literal["ffill"]] = Field(
        None,
        description="Method to use for filling Null values in Column. ffil -> propagate last valid observation forward to next valid. backfill -> use next valid observation to fill gap",
    )

    @root_validator()
    @classmethod
    def validate_value_or_method(cls, field_values):
        value = field_values["value"]
        method = field_values["method"]

        if value is None and method is None:
            raise ValueError("Either value or method must be set.")
        if value is not None and method is not None:
            raise ValueError("Either value or method must be set, but not both.")

        return field_values
