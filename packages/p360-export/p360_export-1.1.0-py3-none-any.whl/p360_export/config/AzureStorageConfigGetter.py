import json
from pyspark.sql.session import SparkSession
import os

from p360_export.config.ConfigGetterInterface import ConfigGetterInterface


class AzureStorageConfigGetter(ConfigGetterInterface):
    def __init__(self, base_path: str, spark: SparkSession):
        self.__base_path = base_path
        self.__spark = spark

    def get(self, config_id: str) -> dict:
        json_path = os.path.join(self.__base_path, config_id + ".json")
        config_json = self.__spark.read.text(json_path, wholetext=True).first().value

        return json.loads(config_json)
