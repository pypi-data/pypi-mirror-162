from p360_export.utils.SecretGetterInterface import SecretGetterInterface


class SecretGetterFactory:
    def __init__(self, secret_getter: SecretGetterInterface):
        self.__secret_getter = secret_getter

    def get(self):
        return self.__secret_getter
