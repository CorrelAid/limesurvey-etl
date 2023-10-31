import numpy as np
import pandas as pd

from limesurvey_etl.config.transform_config.add_columns import AddColumnsConfig
from limesurvey_etl.transform.base import BaseTransform


class AddColumnsTransform(BaseTransform[AddColumnsConfig]):
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        column_names = self.config.column_names
        if not isinstance(column_names, list):
            column_names = [column_names]

        if len(set(df.columns).intersection(set(column_names))) > 0:
            raise ValueError("At least one of the columns to be added already exists")

        df[self.config.column_names] = self.config.default_value or np.nan

        return df
