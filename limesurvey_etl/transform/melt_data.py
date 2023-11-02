from typing import Optional

import pandas as pd

from limesurvey_etl.config.transform_config.melt_data import MeltDataConfig
from limesurvey_etl.transform.base import BaseTransform


class MeltDataTransform(BaseTransform[MeltDataConfig]):
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.melt(
            id_vars=self.config.id_vars,
            value_vars=self.config.value_vars,
            value_name=self.config.value_name,
            var_name=self.config.var_name,
        )
