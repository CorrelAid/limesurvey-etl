import pandas as pd

from limesurvey_etl.config.transform_config.add_columns import AddColumnsConfig
from limesurvey_etl.transform.base import BaseTransform


class AddColumnsTransform(BaseTransform[AddColumnsConfig]):
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        column_content = self.config.default_value or pd.Series(dtype="str")
        df[self.config.column_name] = column_content

        return df
