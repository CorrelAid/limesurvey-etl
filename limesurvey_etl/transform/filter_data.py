import pandas as pd

from limesurvey_etl.config.transform_config.filter_data import FilterDataConfig
from limesurvey_etl.transform.base import BaseTransform


class FilterDataTransform(BaseTransform[FilterDataConfig]):
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        conditions = []
        for condition_config in self.config.conditions:
            value = condition_config.value
            column = df[condition_config.column]
            if column.dtype == "object":
                value = str(value)
            elif column.dtype == "int64":
                value = int(value)
            elif column.dtype == "float64":
                value = float(value)
            elif column.dtype == "bool":
                value = bool(value)
            condition = condition_config.operator(column, value)
            conditions.append(condition)
        common_idxs = set(conditions[0][conditions[0]].index)

        if self.config.logical_operator is None:
            pass
        elif self.config.logical_operator.upper() == "AND":
            for condition in conditions[1:]:
                common_idxs = common_idxs & set(conditions[1][conditions[1]].index)
        elif self.config.logical_operator.upper() == "OR":
            for condition in conditions[1:]:
                common_idxs = common_idxs | set(condition[condition].index)
        elif self.config.logical_operator is not None:
            raise ValueError("Invalid logical operator")

        return df.iloc[list(common_idxs)].reset_index(drop=True)
