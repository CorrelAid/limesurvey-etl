from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel

C = TypeVar("C", bound=BaseModel)


class BaseExtract(ABC, Generic[C]):
    """
    Base class for all extract steps.
    """

    def __init__(self, config: C):
        self.config = config

    @abstractmethod
    def extract(self) -> None:
        """
        Extract data from a source and store it in a staging area (e.g., a staging Database)
        """
