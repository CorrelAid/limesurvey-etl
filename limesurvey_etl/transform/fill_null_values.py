import pandas as pd

from limesurvey_etl.config.transform_config.fill_null_values import FillNullValuesConfig
from limesurvey_etl.transform.base import BaseTransform


class FillNullValuesTransform(BaseTransform[FillNullValuesConfig]):
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        column = self.config.column_name
        if self.config.value:
            df[column] = df[column].fillna(self.config.value)
        else:
            df[column] = df[column].fillna(method=self.config.method)

        return df
