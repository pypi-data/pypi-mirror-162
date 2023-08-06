import unittest
from unittest.mock import patch

from p360_export.utils.EnvVariableSecretGetter import EnvVariableSecretGetter


class EnvVariableConfigGetterTest(unittest.TestCase):
    @patch("os.getenv")
    def test_env_variable_secret_getter(self, mock_os_getenv):
        def getenv(key):
            return {"AZURE_STORAGE_CONNECTION_STRING": "secret"}.get(key)

        mock_os_getenv.side_effect = getenv

        secret_getter = EnvVariableSecretGetter()
        self.assertEqual(secret_getter.get("AZURE_STORAGE_CONNECTION_STRING"), "secret")


if __name__ == "__main__":
    unittest.main()
