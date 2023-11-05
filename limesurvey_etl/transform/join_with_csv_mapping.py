import pandas as pd

from limesurvey_etl.config.transform_config.join_with_csv_mapping import (
    JoinWithCSVMappingConfig,
)
from limesurvey_etl.transform.base import BaseTransform


class JoinWithCSVMappingTransform(BaseTransform[JoinWithCSVMappingConfig]):
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        base_columns = df.columns
        mapping_df = pd.read_csv(
            self.config.mapping_path, delimiter=self.config.mapping_delimiter
        )
        if self.config.on is not None:
            df = df.merge(mapping_df, on=self.config.on)
        else:
            df = df.merge(
                mapping_df,
                left_on=self.config.left_on,
                right_on=self.config.right_on,
                suffixes=["", "to_be_del"],
            )
        final_columns_list = list(base_columns) + list(self.config.keep_columns)
        final_columns_list = [
            col for col in final_columns_list if not col.endswith("to_be_del")
        ]
        if self.config.keep_columns is not None:
            df = df[final_columns_list]

        return df
