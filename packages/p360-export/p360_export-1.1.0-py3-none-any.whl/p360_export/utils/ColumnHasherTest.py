import unittest
from pysparkbundle.test.PySparkTestCase import PySparkTestCase

import hashlib
from p360_export.utils.ColumnHasher import ColumnHasher


class ColumnHasherTest(PySparkTestCase):
    def test_hashing_external_converter(self):
        df = self.spark.createDataFrame([["a", "b"], ["b", "c"], ["c", "d"]], ["col1", "col2"])

        def hashing_function(original: str) -> str:
            return hashlib.sha256(original.encode()).hexdigest()

        df_hashed = ColumnHasher().hash(df=df, columns=["col1"], converter=hashing_function)

        df_expected = self.spark.createDataFrame(
            [
                ["ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb", "b"],
                ["3e23e8160039594a33894f6564e1b1348bbd7a0088d42c4acb73eeaed59c009d", "c"],
                ["2e7d2c03a9507ae265ecf5b5356885a53393a2029d241394997265a1a25aefc6", "d"],
            ],
            ["col1", "col2"],
        )

        self.compare_dataframes(df_expected, df_hashed, ["col1"])

    def test_hashing_internal_converter(self):
        df = self.spark.createDataFrame([["a", "b"], ["b", "c"], ["c", "d"]], ["col1", "col2"])

        column_hasher = ColumnHasher()

        df_hashed = column_hasher.hash(df=df, columns=["col1"], converter=column_hasher.sha256)

        df_expected = self.spark.createDataFrame(
            [
                ["ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb", "b"],
                ["3e23e8160039594a33894f6564e1b1348bbd7a0088d42c4acb73eeaed59c009d", "c"],
                ["2e7d2c03a9507ae265ecf5b5356885a53393a2029d241394997265a1a25aefc6", "d"],
            ],
            ["col1", "col2"],
        )

        self.compare_dataframes(df_expected, df_hashed, ["col1"])


if __name__ == "__main__":
    unittest.main()
