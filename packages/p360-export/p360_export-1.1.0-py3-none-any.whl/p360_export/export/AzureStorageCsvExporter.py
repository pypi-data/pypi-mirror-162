from pyspark.sql import DataFrame, SparkSession
from pyspark.dbutils import DBUtils
import os

from p360_export.export.ExporterInterface import ExporterInterface


class AzureStorageCsvExporter(ExporterInterface):
    def __init__(self, exports_base_path: str, spark: SparkSession):
        self.__exports_base_path = exports_base_path
        self.__spark = spark

    @property
    def export_destination(self):
        return "dataplatform"

    def export(self, df: DataFrame, config: dict):
        config_id = config.get("id")
        df.toPandas().to_csv("/dbfs/tmp/tmpxol6w4xe.csv")  # pyre-ignore[16]
        dbutils = DBUtils(self.__spark)
        dbutils.fs.mv("dbfs:/tmp/tmpxol6w4xe.csv", os.path.join(self.__exports_base_path, config_id + ".csv"))
