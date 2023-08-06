import unittest
import datetime
from decimal import Decimal
from pyspark.sql.types import (
    ByteType,
    ShortType,
    IntegerType,
    LongType,
    FloatType,
    DoubleType,
    DecimalType,
    BooleanType,
    StringType,
    DateType,
    TimestampType,
    StructField,
    StructType,
)
from pysparkbundle.test.PySparkTestCase import PySparkTestCase
from p360_export.data.type.validate.EmailValidator import EmailValidator
from p360_export.data.type.validate.PhoneNumberValidator import PhoneNumberValidator
from p360_export.data.type.resolve.SFMCTypeResolver import SFMCTypeResolver
from p360_export.data.type.resolve.DataFrameTypeResolver import DataFrameTypeResolver
from p360_export.utils.ColumnSampleGetter import ColumnSampleGetter


class TypeResolversTest(PySparkTestCase):
    @property
    def df(self):
        schema = StructType(
            [
                StructField("tinyint", ByteType(), True),
                StructField("smallint", ShortType(), True),
                StructField("int", IntegerType(), True),
                StructField("bigint", LongType(), True),
                StructField("float", FloatType(), True),
                StructField("double", DoubleType(), True),
                StructField("decimal", DecimalType(precision=4, scale=3), True),
                StructField("boolean", BooleanType(), True),
                StructField("string", StringType(), True),
                StructField("email", StringType(), True),
                StructField("date", DateType(), True),
                StructField("timestamp", TimestampType(), True),
                StructField("phone", StringType(), True),
                StructField("not_a_phone", StringType(), True),
                StructField("not_sure_if_email", StringType(), True),
            ]
        )

        return self.spark.createDataFrame(
            [
                [5, 5, 5, 5, 0.5, 0.3, Decimal(0.444), False, None, None, datetime.date.today(), None, "+421905905", None, "random_string"],
                [
                    5,
                    5,
                    5,
                    5,
                    0.5,
                    0.3,
                    None,
                    False,
                    "stringo",
                    "email@email.com",
                    None,
                    datetime.datetime.now(),
                    None,
                    "1231222",
                    "email@email.com",
                ],
            ],
            schema,
        )

    def get_phone_validator(self):
        return PhoneNumberValidator(
            min_phone_number_digit_count=8,
            max_phone_number_digit_count=15,
            phone_number_regex=r"^(\(?\+?\d{1,3}\)?)([ .\/-]?\d{2,4}){3,4}$",
        )

    def test_sfmc_type_resolver(self):
        expected_results = {
            "tinyint": "Number",
            "smallint": "Number",
            "int": "Number",
            "bigint": "Number",
            "float": "Decimal",
            "double": "Decimal",
            "decimal": "Decimal",
            "boolean": "Boolean",
            "string": "Text",
            "email": "EmailAddress",
            "date": "Date",
            "timestamp": "Date",
            "phone": "Phone",
            "not_a_phone": "Text",
            "not_sure_if_email": "Text",
        }

        resolver = SFMCTypeResolver(EmailValidator(), self.get_phone_validator(), DataFrameTypeResolver(), ColumnSampleGetter())

        for column, expected_type in expected_results.items():
            assert resolver.resolve(df=self.df, column_name=column) == expected_type


if __name__ == "__main__":
    unittest.main()
