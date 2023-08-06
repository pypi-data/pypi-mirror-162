from pyspark.sql import DataFrame
from pyspark.sql.types import DecimalType, FloatType, DoubleType

from p360_export.exceptions.type_resolver import InvalidDecimalTypeException
from p360_export.data.type.resolve.TypeResolverInterface import TypeResolverInterface


class DataFrameTypeResolver(TypeResolverInterface):
    def __init__(self) -> None:
        self.__float_precision = 3
        self.__double_precision = 4
        self.__float_scale = 7
        self.__double_scale = 15

    def get_decimal_precision(self, df: DataFrame, column_name: str) -> int:
        data_type = df.schema[column_name].dataType

        if isinstance(data_type, DecimalType):
            return data_type.precision
        if isinstance(data_type, FloatType):
            return self.__float_precision
        if isinstance(data_type, DoubleType):
            return self.__double_precision

        raise InvalidDecimalTypeException(f"Type {data_type} is not recognized as a decimal type.")

    def get_decimal_scale(self, df: DataFrame, column_name: str) -> int:
        data_type = df.schema[column_name].dataType

        if isinstance(data_type, DecimalType):
            return data_type.scale
        if isinstance(data_type, FloatType):
            return self.__float_scale
        if isinstance(data_type, DoubleType):
            return self.__double_scale

        raise InvalidDecimalTypeException(f"Type {data_type} is not recognized as a decimal type.")

    def resolve(self, df: DataFrame, column_name: str) -> str:
        df_type = dict(df.dtypes)[column_name]

        if df_type.startswith("decimal"):
            df_type = "decimal"

        return df_type
