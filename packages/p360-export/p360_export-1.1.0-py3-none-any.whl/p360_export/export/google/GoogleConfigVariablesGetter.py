from typing import Dict
from p360_export.export.ConfigVariablesChecker import ConfigVariablesChecker
from p360_export.utils.SecretGetterInterface import SecretGetterInterface


class GoogleConfigVariablesGetter:
    def __init__(
        self,
        config_variables_checker: ConfigVariablesChecker,
        secret_getter: SecretGetterInterface,
        developer_token_key: str,
        refresh_token_key: str,
        client_secret_key: str,
        client_id: str,
    ):
        self.__config_variables_checker = config_variables_checker
        self.__secret_getter = secret_getter
        self.__config_variables = {
            "developer_token_key": developer_token_key,
            "refresh_token_key": refresh_token_key,
            "client_secret_key": client_secret_key,
            "client_id": client_id,
        }

    def __get_secret_value(self, key: str) -> str:
        return self.__secret_getter.get(key=self.__config_variables.pop(key))

    def get(self, export_destination) -> Dict[str, str]:
        self.__config_variables_checker.check(export_destination=export_destination, keys=self.__config_variables)

        self.__config_variables["developer_token"] = self.__get_secret_value("developer_token_key")
        self.__config_variables["refresh_token"] = self.__get_secret_value("refresh_token_key")
        self.__config_variables["client_secret"] = self.__get_secret_value("client_secret_key")

        return self.__config_variables
