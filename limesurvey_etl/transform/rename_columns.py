import pandas as pd

from limesurvey_etl.config.transform_config.rename_columns import RenameColumnsConfig
from limesurvey_etl.transform.base import BaseTransform


class RenameColumnsTransform(BaseTransform[RenameColumnsConfig]):
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.rename(columns=self.config.colname_to_colname)
        return df
