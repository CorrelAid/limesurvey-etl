from typing import Optional

import pandas as pd

from limesurvey_etl.config.transform_config.cast_data_type import CastDataTypeConfig
from limesurvey_etl.transform.base import BaseTransform


class CastDataTypeTransform(BaseTransform[CastDataTypeConfig]):
    def transform(self, df: pd.DataFrame | None) -> pd.DataFrame:
        df[self.config.column_names] = df[self.config.column_names].astype(
            self.config.target_data_type
        )
        return df
