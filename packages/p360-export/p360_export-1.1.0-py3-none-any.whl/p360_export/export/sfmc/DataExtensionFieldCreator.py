from typing import Dict
from pyspark.sql import DataFrame

from p360_export.data.type.resolve.DataFrameTypeResolver import DataFrameTypeResolver
from p360_export.data.type.resolve.SFMCTypeResolver import SFMCTypeResolver


class DataExtensionFieldCreator:
    def __init__(
        self,
        df_type_resolver: DataFrameTypeResolver,
        type_resolver: SFMCTypeResolver,
    ):
        self.__max_decimal_scale = 8
        self.__max_decimal_precision = 29
        self.__type_resolver = type_resolver
        self.__df_type_resolver = df_type_resolver

    def __add_decimal_field_properties(self, df: DataFrame, field_name: str, field_properties: Dict[str, str]):
        scale = min(self.__df_type_resolver.get_decimal_scale(df, field_name), self.__max_decimal_scale)
        precision = min(self.__df_type_resolver.get_decimal_precision(df, field_name), self.__max_decimal_precision)

        field_properties["MaxLength"] = str(precision + scale)
        field_properties["Scale"] = str(scale)

    def __get_field_type(self, df: DataFrame, field_name: str) -> str:
        return self.__type_resolver.resolve(df, field_name)

    def create_primary_key_field(self, df: DataFrame, field_name: str) -> Dict[str, str]:
        field_properties = self.create(df=df, field_name=field_name)

        field_properties["IsPrimaryKey"] = "true"
        field_properties["MaxLength"] = "100"
        field_properties["IsRequired"] = "true"

        return field_properties

    def create(self, df: DataFrame, field_name: str) -> Dict[str, str]:
        field_type = self.__get_field_type(df, field_name)
        field_properties = {"Name": field_name, "FieldType": field_type}

        if field_type == "Decimal":
            self.__add_decimal_field_properties(df, field_name, field_properties)

        return field_properties
