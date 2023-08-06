from abc import ABC, abstractmethod
from pyspark.sql import DataFrame


class DataBuilderInterface(ABC):
    @property
    @abstractmethod
    def data_location(self):
        pass

    @abstractmethod
    def build(self, config: dict) -> DataFrame:
        pass
