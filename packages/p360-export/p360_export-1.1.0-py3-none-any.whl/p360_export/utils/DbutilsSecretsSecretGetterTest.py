import unittest
from unittest.mock import patch

from p360_export.utils.DbutilsSecretsSecretGetter import DbutilsSecretsSecretGetter


class DbutilsSecretsSecretGetterTest(unittest.TestCase):
    @patch("pyspark.dbutils.DBUtils.secrets.get")
    @patch("pyspark.dbutils.DBUtils")
    def test_secret_matches(self, mock_dbutils, mock_secrets_get):
        def get(scope, key):  # pylint: disable=W0613
            return "test_secret"

        mock_secrets_get.side_effect = get

        secret_getter = DbutilsSecretsSecretGetter(scope="test_scope", dbutils=mock_dbutils)

        self.assertEqual(secret_getter.get(key="test_key"), "test_secret")


if __name__ == "__main__":
    unittest.main()
