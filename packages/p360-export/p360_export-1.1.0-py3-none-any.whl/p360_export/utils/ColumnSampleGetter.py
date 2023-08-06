from typing import List
from pyspark.sql import DataFrame

from p360_export.exceptions.utils import ColumnContainsNoValidExampleException


class ColumnSampleGetter:
    def get(self, df: DataFrame, column_name: str) -> List[str]:
        example_rows = df.dropna(subset=[column_name]).take(10)

        if not example_rows:
            raise ColumnContainsNoValidExampleException(f"Unable to get example value, column {column_name} contains only null values")

        return [example_row[column_name] for example_row in example_rows]
