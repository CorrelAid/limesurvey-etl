from typing import Literal, Union

from pydantic import BaseModel, Field, root_validator


class Operator(BaseModel):
    """
    Represents an operator used in computations.

    Attributes:
        name (Union[Literal["sum"], Literal["product"], Literal["difference"], Literal["concat"]]):
            Operation used to compute new column.
        separator (str, optional): Separator used to separate strings."""

    name: Union[
        Literal["sum"], Literal["product"], Literal["difference"], Literal["concat"]
    ] = Field(..., description="Operation used to compute new column.")
    separator: str = Field(None, description="Separator used to separate strings")

    @root_validator
    @classmethod
    def validate_fields(cls, field_values):
        if field_values["name"] != "concat" and field_values["separator"] is not None:
            raise ValueError("Separator can only be used when using 'concat' operator.")
        return field_values


class ConcatOperator(Operator):
    """
    Represents a concatenation operator.

    Attributes:
        operator (Literal["concat"]): Type of operator, should be "concat".
        separator (str, optional): Separator used to separate strings.

    """

    operator: Literal["concat"]
    separator: str = Field(None, description="Separator used to separate strings")


class AddComputedColumnConfig(BaseModel):
    """
    Configuration for adding a computed column.

    Attributes:
        transform_type (Literal["add_computed_column"]): Type of transformation, should be "add_computed_column".
        column_name (str): Name of the new column.
        input_columns (list[str]): Columns that should be used to compute the new column.
        operator (Operator): Operation used to compute the new column.
        drop_input_columns (Union[Literal["all"], list[str]], optional): Input columns to be dropped from
            data frame after computation.

    """

    transform_type: Literal["add_computed_column"]
    column_name: str = Field(..., description="Name of the new column.")
    input_columns: list[str] = Field(
        ..., description="Columns that should be used to compute the new column."
    )
    operator: Operator = Field(..., description="Operation used to compute new column.")
    drop_input_columns: Union[Literal["all"], list[str]] = Field(
        None,
        description="Input columns to be dropped from data frame after computation.",
    )
