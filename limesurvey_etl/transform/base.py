from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar

import pandas as pd
from pydantic import BaseModel

C = TypeVar("C", bound=BaseModel)


class BaseTransform(ABC, Generic[C]):
    def __init__(self, config: C):
        self.config = config

    @abstractmethod
    def transform(self, df: Optional[pd.DataFrame]) -> pd.DataFrame:
        """
        Transform the dataframe into a different dataframe.
        :param df: The original dataframe
        :return: The transformed dataframe
        :rtype: pd.DataFrame
        """
