from typing import Optional

import pandas as pd

from limesurvey_etl.config.transform_config.replace_values import ReplaceValuesConfig
from limesurvey_etl.transform.base import BaseTransform


class ReplaceValuesTransform(BaseTransform[ReplaceValuesConfig]):
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.replace(self.config.replacement_values)
