from typing import Literal, Union

from pydantic import BaseModel, Field, root_validator


class Operator(BaseModel):
    """
    Represents an operator used in computations.

    Attributes:
        name (Union[Literal["sum"], Literal["product"], Literal["difference"], Literal["concat"], Literal["split"]]):
            Operation used to compute new column.
        separator (str, optional): Separator used to separate strings when using 'concat'. Defaults to '_'
        delimiter (str, optional): Delimiter used to split strings when using 'split' operator. Defaults to '_'
        expand (bool, optional): Whether or not to expand the split values into multiple columns when using the 'split' operator. Defaults to False.
    """

    name: Union[
        Literal["sum"],
        Literal["product"],
        Literal["difference"],
        Literal["concat"],
        Literal["split"],
    ] = Field(..., description="Operation used to compute new column.")
    separator: str = Field(None, description="Separator used to separate strings")
    delimiter: str = Field(None, description="Delimiter used to split strings")
    expand: bool = Field(
        None,
        description="Whether or not to expand the split values when using the 'split' operator.",
    )

    @root_validator
    @classmethod
    def validate_fields(cls, field_values):
        if field_values["name"] != "concat" and field_values["separator"] is not None:
            raise ValueError("Separator can only be used when using 'concat' operator.")
        if (
            field_values["name"] != "split"
            and field_values["delimiter"] is not None
            and field_values["expand"] is not None
        ):
            raise ValueError(
                "Delimiter and expand parameters can only be used with 'split' operator"
            )
        return field_values


class AddComputedColumnConfig(BaseModel):
    """
    Configuration for adding a computed column.

    Attributes:
        transform_type (Literal["add_computed_column"]): Type of transformation, should be "add_computed_column".
        column_name (Union[str, list[str]]): Name(s) of the new column(s).
        input_columns (Union[str, list[str]]): Column(s) that should be used to compute the new column(s).
        operator (Operator): Operation used to compute the new column.
        drop_input_columns (Union[Literal["all"], list[str]], optional): Input columns to be dropped from
            data frame after computation.

    """

    transform_type: Literal["add_computed_column"]
    column_name: Union[str, list[str]] = Field(
        ..., description="Name(s) of the new column(s)."
    )
    input_columns: Union[str, list[str]] = Field(
        ..., description="Columns that should be used to compute the new column."
    )
    operator: Operator = Field(..., description="Operation used to compute new column.")
    drop_input_columns: Union[Literal["all"], list[str]] = Field(
        None,
        description="Input columns to be dropped from data frame after computation.",
    )
