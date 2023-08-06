import unittest
from pyspark.sql import DataFrame

from pysparkbundle.test.PySparkTestCase import PySparkTestCase

from p360_export.data.pick.ColumnMappingGetter import ColumnMappingGetter
from p360_export.data.pick.DataPlatformDataPicker import DataPlatformDataPicker
from p360_export.data.pick.FacebookDataPicker import FacebookDataPicker
from p360_export.data.pick.GoogleAdsDataPicker import GoogleAdsDataPicker

TABLE_ID = "table_12345"
QUERY = f"SELECT email_col, gen_col, phone_col from {TABLE_ID}"

CONFIG = {"params": {"mapping": {"Email": "email_col", "Gender": "gen_col", "Phone": "phone_col"}}}

BASE_DF_DATA = [
    ["client_id1", "email1", "m", "unwanted", "phone1", "unwanted2"],
    ["client_id2", "email2", "f", "unwanted", "phone2", "unwanted2"],
    ["client_id3", "email3", "m", "unwanted", "phone3", "unwanted2"],
]
BASE_DF_SCHEMA = ["client_id", "email_col", "gen_col", "unwanted_col", "phone_col", "emailo_col"]

EXPECTED_DF_DATA = [
    ["email1", "m", "phone1"],
    ["email2", "f", "phone2"],
    ["email3", "m", "phone3"],
]
EXPECTED_LIST_BASED_SCHEMA = ["email_col", "gen_col", "phone_col"]
EXPECTED_MAPPING_BASED_SCHEMA = ["EMAIL", "GEN", "PHONE"]


class DataPickerTest(PySparkTestCase):
    @property
    def base_df(self) -> DataFrame:
        return self.spark.createDataFrame(BASE_DF_DATA, BASE_DF_SCHEMA)

    def expected_df(self, schema: list) -> DataFrame:
        return self.spark.createDataFrame(EXPECTED_DF_DATA, schema)

    def test_data_platform_data_frame_builder(self):
        data_picker = DataPlatformDataPicker(self.spark)
        df = data_picker.pick(df=self.base_df, query=QUERY, table_id=TABLE_ID, config=CONFIG)
        self.compare_dataframes(df, self.expected_df(EXPECTED_LIST_BASED_SCHEMA), ["email_col"])

    def test_facebook_data_picker(self):
        data_picker = FacebookDataPicker(self.spark, ColumnMappingGetter())
        df = data_picker.pick(df=self.base_df, query=QUERY, table_id=TABLE_ID, config=CONFIG)
        self.compare_dataframes(df, self.expected_df(EXPECTED_MAPPING_BASED_SCHEMA), ["EMAIL"])

    def test_google_ads_data_picker(self):
        data_picker = GoogleAdsDataPicker(self.spark, ColumnMappingGetter())
        df = data_picker.pick(df=self.base_df, query=QUERY, table_id=TABLE_ID, config=CONFIG)
        self.compare_dataframes(df, self.expected_df(EXPECTED_LIST_BASED_SCHEMA), ["email_col"])


if __name__ == "__main__":
    unittest.main()
