from pyspark.sql import DataFrame
from pyspark.sql.session import SparkSession

from p360_export.data.pick.DataPickerInterface import DataPickerInterface


class DataPlatformDataPicker(DataPickerInterface):
    def __init__(self, spark: SparkSession):
        self.__spark = spark

    @property
    def export_destination(self):
        return "dataplatform"

    def pick(self, df: DataFrame, query: str, table_id: str, config: dict) -> DataFrame:
        df.createOrReplaceTempView(table_id)

        return self.__spark.sql(query)
