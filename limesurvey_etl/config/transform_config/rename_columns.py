from typing import Literal

from pydantic import BaseModel, Field


class RenameColumnsConfig(BaseModel):
    """
    Configuration for renaming columns.

    Attributes:
        transform_type (Literal["rename_columns"]): Type of transformation, should be "rename_columns".
        colname_to_colname (dict[str, str]): Dictionary containing the original column names as keys
            and the new column names as values.

    """

    transform_type: Literal["rename_columns"]
    colname_to_colname: dict[str, str] = Field(
        ...,
        description="Dictionary containig the original column names as keys and the new column names as values",
    )
