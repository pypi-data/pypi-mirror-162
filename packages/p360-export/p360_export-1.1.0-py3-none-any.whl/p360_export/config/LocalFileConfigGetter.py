import json
import os

from p360_export.config.ConfigGetterInterface import ConfigGetterInterface


class LocalFileConfigGetter(ConfigGetterInterface):
    def __init__(self, base_path: str):
        self.__base_path = base_path

    def get(self, config_id: str) -> dict:
        with open(os.path.join(self.__base_path, config_id + ".json"), encoding="utf8") as file_handler:
            config_json = file_handler.read()
        return json.loads(config_json)
