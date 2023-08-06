from abc import ABC, abstractmethod
from pyspark.sql import DataFrame


class TypeResolverInterface(ABC):
    @abstractmethod
    def resolve(self, df: DataFrame, column_name: str) -> str:
        pass
