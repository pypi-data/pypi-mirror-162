import os

from p360_export.utils.SecretGetterInterface import SecretGetterInterface


class EnvVariableSecretGetter(SecretGetterInterface):
    def get(self, key: str) -> str:
        return os.getenv(key) or ""
