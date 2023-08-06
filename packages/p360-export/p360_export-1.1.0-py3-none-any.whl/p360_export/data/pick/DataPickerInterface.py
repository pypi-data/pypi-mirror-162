from abc import ABC, abstractmethod
from pyspark.sql import DataFrame


class DataPickerInterface(ABC):
    @property
    @abstractmethod
    def export_destination(self):
        pass

    @abstractmethod
    def pick(self, df: DataFrame, query: str, table_id: str, config: dict) -> DataFrame:
        pass
