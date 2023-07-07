from typing import Literal, Union

from pydantic import BaseModel, Field, validator


class FilterCondition(BaseModel):
    column: str
    value: str
    operator: str

    @validator("operator")
    @classmethod
    def validate_operator(cls, o):
        operator_mapping = {
            "==": lambda x, y: x == y,
            ">": lambda x, y: x > y,
            "<": lambda x, y: x < y,
            ">=": lambda x, y: x >= y,
            "<=": lambda x, y: x <= y,
        }
        if not o in operator_mapping.keys():
            raise ValueError(
                f"Invalid Operator, got {o}, must be one of {operator_mapping.keys()}"
            )
        return operator_mapping[o]


class FilterDataConfig(BaseModel):
    transform_type: Literal["filter_data"]
    conditions: list[FilterCondition] = Field(
        ..., description="List of FilterCondition objects"
    )
    logical_operator: Union[Literal["AND"], Literal["OR"]] = Field(
        None,
        description="Logical operator to be applied if multiple conditions should be applied.",
    )
