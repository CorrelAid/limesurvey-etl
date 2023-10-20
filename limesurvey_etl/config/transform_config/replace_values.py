from typing import Literal, Union

from pydantic import BaseModel, Field, validator


class ReplaceValuesConfig(BaseModel):
    """
    Configuration for replacing values in columns.

    Attributes:
        transform_type (Literal["replace_values"]): Type of transformation, should be "replace_values".
        column_name (Union[str, list[str]], optional): Columns in which to replace values.
            If None, then value will be replaced in the entire dataframe.
        replacement_values (dict[Union[str, int, float, bool], Union[str, int, float, bool]]):
            Dictionary containing the replacement values. Dictionary keys indicate values to be
            replaced by corresponding dictionary values."""

    transform_type: Literal["replace_values"]
    column_name: Union[str, list[str]] = Field(
        None,
        description="Columns in which to replace values. If None, then value will be replaced in the entire dataframe.",
    )
    replacement_values: dict[
        Union[str, int, float, bool], Union[str, int, float, bool]
    ] = Field(
        ...,
        description="Dictionary containing the replacement values. Dictionary keys indicate values to be replaced by corresponding dictionary values.",
    )
