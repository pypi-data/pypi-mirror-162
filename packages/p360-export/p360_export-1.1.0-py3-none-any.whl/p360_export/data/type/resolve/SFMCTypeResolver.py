from typing import Dict, List
from pyspark.sql import DataFrame

from p360_export.data.type.validate.EmailValidator import EmailValidator
from p360_export.data.type.validate.PhoneNumberValidator import PhoneNumberValidator
from p360_export.data.type.resolve.TypeResolverInterface import TypeResolverInterface
from p360_export.data.type.resolve.DataFrameTypeResolver import DataFrameTypeResolver
from p360_export.utils.ColumnSampleGetter import ColumnSampleGetter


class SFMCTypeResolver(TypeResolverInterface):
    def __init__(
        self,
        email_validator: EmailValidator,
        phone_number_validator: PhoneNumberValidator,
        df_type_resolver: DataFrameTypeResolver,
        column_sample_getter: ColumnSampleGetter,
    ):
        self.__email_validator = email_validator
        self.__phone_number_validator = phone_number_validator
        self.__df_type_resolver = df_type_resolver
        self.__column_sample_getter = column_sample_getter

    @property
    def type_map(self) -> Dict[str, str]:
        return {
            "tinyint": "Number",
            "smallint": "Number",
            "int": "Number",
            "bigint": "Number",
            "float": "Decimal",
            "double": "Decimal",
            "decimal": "Decimal",
            "boolean": "Boolean",
            "string": "Text",
            "date": "Date",
            "timestamp": "Date",
        }

    def _resolve_text_type(self, sample_values: List[str]) -> str:
        if all(self.__email_validator.validate(value) for value in sample_values):
            return "EmailAddress"

        if all(self.__phone_number_validator.validate(value) for value in sample_values):
            return "Phone"

        return "Text"

    def resolve(self, df: DataFrame, column_name: str) -> str:
        df_type = self.__df_type_resolver.resolve(df, column_name)
        sfmc_type = self.type_map[df_type]

        if sfmc_type != "Text":
            return sfmc_type

        sample_values = self.__column_sample_getter.get(df, column_name)

        return self._resolve_text_type(sample_values)
