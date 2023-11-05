from typing import Literal, Union

from pydantic import BaseModel, Field, validator


class ReplaceValuesConfig(BaseModel):
    """
    Configuration for replacing values in columns.

    Attributes:
        transform_type (Literal["replace_values"]): Type of transformation, should be "replace_values".
        replacement_values (dict[str, dict[Union[str, int, float, bool], Union[str, int, float, bool]]]):
            Dictionary containing the replacement values. Dictionary keys indicate values to be
            replaced by corresponding dictionary values."""

    transform_type: Literal["replace_values"]
    replacement_values: dict[
        str, dict[Union[str, int, float, bool], Union[str, int, float, bool]]
    ] = Field(
        ...,
        description="Dictionary containing the replacement values. Dictionary keys indicate the columns the replacement should be applied to. The values are dictionaries where the key is to be replaced with the value in the corresponding column.",
    )
