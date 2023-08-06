from p360_export.export.sfmc.SFMCData import SFMCData
from p360_export.utils.SecretGetterInterface import SecretGetterInterface
from p360_export.export.ConfigVariablesChecker import ConfigVariablesChecker


class SFMCDataGetter:
    def __init__(
        self,
        secret_getter: SecretGetterInterface,
        config_variables_checker: ConfigVariablesChecker,
        client_id: str,
        client_secret_key: str,
        ftp_username: str,
        ftp_password_key: str,
        tenant_url: str,
        account_id: str,
        file_location: str,
    ):
        self.__config_variables = {
            "client_id": client_id,
            "client_secret_key": client_secret_key,
            "ftp_username": ftp_username,
            "ftp_password_key": ftp_password_key,
            "tenant_url": tenant_url,
            "account_id": account_id,
            "file_location": file_location,
        }
        self.__secret_getter = secret_getter
        self.__config_variables_checker = config_variables_checker

    def __get_secret_value(self, key: str) -> str:
        return self.__secret_getter.get(key=self.__config_variables[key])

    def get(self, config: dict, export_destination: str):
        self.__config_variables_checker.check(export_destination=export_destination, keys=self.__config_variables)

        self.__config_variables["client_secret"] = self.__get_secret_value("client_secret_key")
        self.__config_variables["ftp_password"] = self.__get_secret_value("ftp_password_key")

        return SFMCData(
            client_id=self.__config_variables["client_id"],
            client_secret=self.__config_variables["client_secret"],
            ftp_username=self.__config_variables["ftp_username"],
            ftp_password=self.__config_variables["ftp_password"],
            tenant_url=self.__config_variables["tenant_url"],
            account_id=self.__config_variables["account_id"],
            file_location=self.__config_variables["file_location"],
            config=config,
        )
