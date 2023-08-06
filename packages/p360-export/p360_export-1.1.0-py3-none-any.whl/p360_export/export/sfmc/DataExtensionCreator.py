from typing import Dict, List
from FuelSDK import ET_Client, ET_DataExtension
from pyspark.sql import DataFrame

from p360_export.exceptions.exporter import UnableToCreateDataExtension
from p360_export.export.sfmc.DataExtensionFieldCreator import DataExtensionFieldCreator
from p360_export.export.sfmc.SFMCData import SFMCData


class DataExtensionCreator:
    def __init__(self, data_extension_field_creator: DataExtensionFieldCreator):
        self.__data_extension_field_creator = data_extension_field_creator

    def __get_subscriber_key_field(self, df: DataFrame, sfmc_data: SFMCData) -> Dict[str, str]:
        return self.__data_extension_field_creator.create_primary_key_field(df=df, field_name=sfmc_data.subscriber_key)

    def __get_additional_fields(self, df: DataFrame, sfmc_data: SFMCData) -> List[Dict[str, str]]:
        additional_fields = []

        for field_name in sfmc_data.export_columns:
            additional_fields.append(self.__data_extension_field_creator.create(df=df, field_name=field_name))

        return additional_fields

    def create(self, df: DataFrame, client: ET_Client, sfmc_data: SFMCData) -> str:
        data_extension = ET_DataExtension()
        data_extension.auth_stub = client
        data_extension.props = {
            "Name": sfmc_data.audience_name,
            "IsSendable": True,
            "SendableDataExtensionField": {"Name": sfmc_data.subscriber_key},
            "SendableSubscriberField": {"Name": "Subscriber Key"},
        }

        data_extension.columns = [self.__get_subscriber_key_field(df=df, sfmc_data=sfmc_data)]
        data_extension.columns.extend(self.__get_additional_fields(df=df, sfmc_data=sfmc_data))

        response = data_extension.post()

        if response.results[0]["StatusCode"] == "Error":
            raise UnableToCreateDataExtension(str(response.results))

        return response.results[0]["NewObjectID"]
