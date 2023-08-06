from pyspark.dbutils import DBUtils

from p360_export.utils.SecretGetterInterface import SecretGetterInterface


class DbutilsSecretsSecretGetter(SecretGetterInterface):
    def __init__(self, scope: str, dbutils: DBUtils):
        self.__dbutils = dbutils
        self.__scope = scope

    def get(self, key: str):
        return self.__dbutils.secrets.get(scope=self.__scope, key=key)
