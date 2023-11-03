from typing import Literal, Union

from pydantic import BaseModel, Field, validator


class FilterCondition(BaseModel):
    """
    Represents a filtering condition.

    Attributes:
        column (str): The column name to apply the condition on.
        value (str): The value to compare against.
        operator (Union[Literal["=="], Literal["!="], Literal[">"], Literal["<"], Literal[">="], Literal["<="], Literal["contains"], Literal["not_contains"]]): The comparison operator.

    """

    column: str
    value: str
    operator: Union[
        Literal["=="],
        Literal["!="],
        Literal[">"],
        Literal["<"],
        Literal[">="],
        Literal["<="],
        Literal["contains"],
        Literal["not_contains"],
    ]

    @validator("operator")
    @classmethod
    def validate_operator(cls, o):
        operator_mapping = {
            "==": lambda x, y: x == y,
            "!=": lambda x, y: x != y,
            ">": lambda x, y: x > y,
            "<": lambda x, y: x < y,
            ">=": lambda x, y: x >= y,
            "<=": lambda x, y: x <= y,
            "contains": lambda x, y: x.str.contains(y),
            "not_contains": lambda x, y: ~x.str.contains(y),
        }
        if not o in operator_mapping.keys():
            raise ValueError(
                f"Invalid Operator, got {o}, must be one of {operator_mapping.keys()}"
            )
        return operator_mapping[o]


class FilterDataConfig(BaseModel):
    """
    Configuration for filtering data.

    Attributes:
        transform_type (Literal["filter_data"]): Type of transformation, should be "filter_data".
        conditions (list[FilterCondition]): List of FilterCondition objects.
        logical_operator (Union[Literal["AND"], Literal["OR"]], optional):
            Logical operator to be applied if multiple conditions should be applied.

    """

    transform_type: Literal["filter_data"]
    conditions: list[FilterCondition] = Field(
        ..., description="List of FilterCondition objects"
    )
    logical_operator: Union[Literal["AND"], Literal["OR"]] = Field(
        None,
        description="Logical operator to be applied if multiple conditions should be applied.",
    )
