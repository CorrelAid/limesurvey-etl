from typing import Literal, Optional, Union

from pydantic import BaseModel, Field, validator


class SumOperator(BaseModel):
    """
    Model representing a 'sum' operator. Computes the sum of values.

    Attributes:
        name (Literal["sum"]): The name of the operator, which should be "sum".
    """

    name: Literal["sum"]


class ProductOperator(BaseModel):
    """
    Model representing a 'product' operator. Computes the product of values.

    Attributes:
        name (Literal["product"]): The name of the operator, which should be "product".
    """

    name: Literal["product"]


class DifferenceOperator(BaseModel):
    """
    Model representing a 'difference' operator. Subtracts the values.

    Attributes:
        name (Literal["difference"]): The name of the operator, which should be "difference".
    """

    name: Literal["difference"]


class ConcatOperator(BaseModel):
    """
    Model representing a 'concat' operator. Concatenates the values using a separator.

    Attributes:
        name (Literal["concat"]): The name of the operator, which should be "concat".
        separator (str, optional): Separator used to separate strings.
    """

    name: Literal["concat"]
    separator: str = Field(None, description="Separator used to separate strings")


class SplitOperator(BaseModel):
    """
    Model representing a 'split' operator. Splites a value based on a delimiter.

    Attributes:
        name (Literal["split"]): The name of the operator, which should be "split".
        delimiter (str, optional): Delimiter used to split strings.
        expand (bool, optional): Whether or not to expand the split values when using the 'split' operator.
    """

    name: Literal["split"]
    delimiter: str = Field(None, description="Delimiter used to split strings")
    expand: bool = Field(
        False,
        description="Whether or not to expand the split values when using the 'split' operator.",
    )


class ExtractOperator(BaseModel):
    """
    Model representing an 'extract' operator. Extracts a match from a string based on a regular expression.

    Attributes:
        name (Literal["extract"]): The name of the operator, which should be "extract".
        regex (str): Regular expression used to extract from string.
        expand (bool, optional): Whether or not to expand the values if multiple matches found.
    """

    name: Literal["extract"]
    regex: str = Field(
        ..., description="Regular expression used to extract from string."
    )
    expand: bool = Field(
        False,
        description="Whether or not to expand the values if multiple matches found.",
    )

    @validator("regex")
    def validate_regex(cls, regex: str):
        return rf"{regex}"


class AddComputedColumnConfig(BaseModel):
    """
    Configuration for adding a computed column.

    Attributes:
        transform_type (Literal["add_computed_column"]): Type of transformation, should be "add_computed_column".
        column_name (Union[str, list[str]]): Name(s) of the new column(s).
        input_columns (Union[str, list[str]]): Column(s) that should be used to compute the new column(s).
        operator (Union[SumOperator,ProductOperator,DifferenceOperator,ConcatOperator,SplitOperator,ExtractOperator]):
            Operation used to compute the new column.
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
    operator: Union[
        SumOperator,
        ProductOperator,
        DifferenceOperator,
        ConcatOperator,
        SplitOperator,
        ExtractOperator,
    ] = Field(
        ..., discriminator="name", description="Operation used to compute new column."
    )
    drop_input_columns: Union[Literal["all"], list[str]] = Field(
        None,
        description="Input columns to be dropped from data frame after computation.",
    )
