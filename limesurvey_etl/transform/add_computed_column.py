from enum import Enum

import pandas as pd

from limesurvey_etl.config.transform_config.add_computed_column import (
    AddComputedColumnConfig,
)
from limesurvey_etl.transform.base import BaseTransform

CAST_TYPES = {"str": str, "int": int, "bool": bool, "float": float}


class AddComputedColumnTransform(BaseTransform[AddComputedColumnConfig]):
    def transform(self, df: pd.DataFrame | None) -> pd.DataFrame:
        operator = self.config.operator.name
        new_column_name = self.config.column_name
        input_columns = self.config.input_columns
        if operator == "sum":
            df[new_column_name] = df[input_columns].sum(axis=1)
        elif operator == "product":
            df[new_column_name] = df[input_columns].prod(axis=1)
        elif operator == "difference":
            df[new_column_name] = df[input_columns].diff(axis=1)
        elif operator == "concat":
            separator = self.config.operator.separator or ""
            df[new_column_name] = (
                df[input_columns].astype(str).apply(separator.join, axis=1)
            )
        elif operator == "split":
            delimiter = self.config.operator.delimiter or "_"
            expand = self.config.operator.expand or False
            df[new_column_name] = df[input_columns].str.split(delimiter, expand=expand)
        elif operator == "extract":
            df[new_column_name] = df[input_columns].str.extract(
                self.config.operator.regex, expand=self.config.operator.expand
            )

        drop_input_columns = self.config.drop_input_columns
        if drop_input_columns == "all":
            df.drop(input_columns, axis=1, inplace=True)
        elif drop_input_columns is not None:
            df.drop(drop_input_columns, axis=1, inplace=True)

        return df
