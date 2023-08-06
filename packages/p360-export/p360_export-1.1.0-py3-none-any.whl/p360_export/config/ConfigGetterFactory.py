from p360_export.config.ConfigGetterInterface import ConfigGetterInterface


class ConfigGetterFactory:
    def __init__(self, config_getter: ConfigGetterInterface):
        self.__config_getter = config_getter

    def get(self):
        return self.__config_getter
