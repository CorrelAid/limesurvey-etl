from typing import Literal, Union

from pydantic import BaseModel, Field, validator

DATA_TYPES = {"str": str, "int": int, "bool": bool, "float": float}


class CastDataTypeConfig(BaseModel):
    transform_type: Literal["cast_data_type"]
    column_names: Union[str, list[str]] = Field(
        ..., description="Name(s) of the column(s) to apply data type casting to."
    )
    target_data_type: Union[
        Literal["str"], Literal["int"], Literal["bool"], Literal["float"]
    ] = Field(..., description="Data type the selected column(s) should be casted to.")

    @validator("target_data_type")
    def validate_target_data_type(cls, data_type):
        if data_type not in DATA_TYPES:
            raise ValueError(f'Data type must be on of {", ".join(DATA_TYPES.keys())}')
        return DATA_TYPES[data_type]
