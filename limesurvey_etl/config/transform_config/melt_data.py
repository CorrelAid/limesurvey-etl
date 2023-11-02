from typing import Literal, Optional, Union

from pydantic import BaseModel, Field


class MeltDataConfig(BaseModel):
    """Configuration for unpivoting (melting) a DataFrame from wide to long format.

    Massage data into a format where one or more columns are identifier variables (id_vars),
    while all other columns, considered measured variables (value_vars), are 'unpivoted' to
    the row axis, leaving just two non-identifier columns, 'variable' and 'value.

    Attributes:
        transform_type (Literal["melt_data"]): The type of data transformation.
        id_vars (Optional[list]): Column(s) to use as identifier variables. Default is None.
        value_vars (Optional[list]): Column(s) to unpivot. If not specified, uses all columns
            that are not set as id_vars.
        var_name (str): Name to use for the 'variable' column.
        value_name (str): Name to use for the 'value' column.
    """

    transform_type: Literal["melt_data"]
    id_vars: Optional[list] = Field(
        None, description="Column(s) to use as identifier variables"
    )
    value_vars: Optional[list] = Field(
        None,
        description="Column(s) to unpivot. If not specified, uses all columns that are note set as id_vars",
    )
    var_name: str = Field(..., description="Name to use for the 'variable' column.")
    value_name: str = Field(..., description="Name to use for the 'value' column.")
