import unittest
from pyspark.sql.types import StructType, StructField, StringType
from pysparkbundle.test.PySparkTestCase import PySparkTestCase
from p360_export.exceptions.utils import ColumnContainsNoValidExampleException

from p360_export.utils.ColumnSampleGetter import ColumnSampleGetter


class ColumnValueExampleGetterTest(PySparkTestCase):
    def test_column_value_example_getter(self):
        column_sample_getter = ColumnSampleGetter()
        df = self.spark.createDataFrame(
            data=[
                [None, "b", None],
                ["a", None, None],
                [None, "0", "c"],
                ["1", "2", "3"],
                ["1", "2", "3"],
                ["1", "2", None],
                ["1", "2", None],
                ["1", "2", None],
                ["1", "2", None],
                ["1", "2", None],
                ["1", "2", "3"],
                ["1", "2", "3"],
                ["1", "2", "3"],
                ["1", "2", "3"],
            ],
            schema=["col1", "col2", "col3"],
        )

        expected_values = {
            "col1": ["a", "1", "1", "1", "1", "1", "1", "1", "1", "1"],
            "col2": ["b", "0", "2", "2", "2", "2", "2", "2", "2", "2"],
            "col3": ["c", "3", "3", "3", "3", "3", "3"],
        }
        for column, expected_value in expected_values.items():
            assert column_sample_getter.get(df, column) == expected_value

    def test_empty_column(self):
        schema = StructType(
            [
                StructField("empty_col", StringType(), True),
            ]
        )

        df = self.spark.createDataFrame(data=[[None], [None], [None]], schema=schema)

        with self.assertRaises(ColumnContainsNoValidExampleException):
            ColumnSampleGetter().get(df, "empty_col")


if __name__ == "__main__":
    unittest.main()
