from pyspark.sql import DataFrame
from pyspark.sql.session import SparkSession

from p360_export.data.pick.ColumnMappingGetter import ColumnMappingGetter
from p360_export.data.pick.DataPickerInterface import DataPickerInterface
from p360_export.exceptions.data_picker import InvalidFacebookColumnException
from p360_export.data.extra.FacebookData import FacebookData


class FacebookDataPicker(DataPickerInterface):
    def __init__(self, spark: SparkSession, column_mapping_getter: ColumnMappingGetter):
        self.__column_mapping_getter = column_mapping_getter
        self.__spark = spark

    @property
    def export_destination(self):
        return "facebook"

    def pick(self, df: DataFrame, query: str, table_id: str, config: dict) -> DataFrame:
        column_mapping = self.__column_mapping_getter.get(config)

        df.createOrReplaceTempView(table_id)

        result_df = self.__spark.sql(query)

        for new_name, old_name in column_mapping.items():
            mapped_name = FacebookData.column_map.get(new_name.lower())
            if not mapped_name:
                raise InvalidFacebookColumnException(f"Column {new_name} is not accepted by Facebook API.")
            result_df = result_df.withColumnRenamed(old_name, mapped_name)

        return result_df
