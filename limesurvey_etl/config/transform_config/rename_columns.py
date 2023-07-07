from typing import Literal

from pydantic import BaseModel, Field


class RenameColumnsConfig(BaseModel):
    transform_type: Literal["rename_columns"]
    colname_to_colname: dict[str, str] = Field(
        ...,
        description="Dictionary containig the original column names as keys and the new column names as values",
    )
