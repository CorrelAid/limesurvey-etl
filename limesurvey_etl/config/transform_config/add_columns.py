from typing import Literal, Union

from pydantic import BaseModel, Field


class AddColumnsConfig(BaseModel):
    transform_type: Literal["add_columns"]
    column_names: Union[str, list[str]] = Field(
        ..., description="Name of the columns to be added."
    )
    default_value: Union[str, int, bool, float] = Field(
        None,
        description="If set, columns will contain this value. Else, columns will be null.",
    )
