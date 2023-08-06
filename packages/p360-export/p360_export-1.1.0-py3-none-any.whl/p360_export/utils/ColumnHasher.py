from typing import Sequence, Callable
from pyspark.sql import DataFrame
from pyspark.sql.functions import pandas_udf
import pandas as pd
from numpy import vectorize
from hashlib import sha256


class ColumnHasher:
    def hash(
        self,
        df: DataFrame,
        columns: Sequence[str],
        converter: Callable[[str], str],
    ) -> DataFrame:
        converter_vectorized = vectorize(converter)

        @pandas_udf("string")  # pyre-ignore[20]
        def hash_udf(series: pd.Series) -> pd.Series:
            return pd.Series(converter_vectorized(series))

        return df.select(*([hash_udf(column).alias(column) for column in columns] + list(set(df.columns) - set(columns))))

    def sha256(self, original: str) -> str:
        return sha256(original.encode()).hexdigest()
