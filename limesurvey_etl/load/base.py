from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel

C = TypeVar("C", bound=BaseModel)


class BaseLoad(ABC, Generic[C]):
    """
    This is the base class for all load steps.
    """

    def __init__(self, config: C):
        self.config = config

    @abstractmethod
    def load(self) -> None:
        """
        Load the data into the target system.
        """
