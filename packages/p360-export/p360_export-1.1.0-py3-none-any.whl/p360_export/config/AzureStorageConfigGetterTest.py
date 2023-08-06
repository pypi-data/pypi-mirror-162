import unittest
from unittest.mock import patch
from pysparkbundle.test.PySparkTestCase import PySparkTestCase

from p360_export.config.AzureStorageConfigGetter import AzureStorageConfigGetter


class AzureStorageConfigGetterTest(PySparkTestCase):
    @patch("pyspark.sql.DataFrameReader.text")
    def test_file_content_matches(self, mock_spark_read_text):
        mock_spark_read_text.return_value = self.spark.createDataFrame([['{"key": "value"}']], ["value"])

        config_getter = AzureStorageConfigGetter(base_path="test/base/path", spark=self.spark)

        config = config_getter.get("123")

        self.assertEqual(config, {"key": "value"})


if __name__ == "__main__":
    unittest.main()
