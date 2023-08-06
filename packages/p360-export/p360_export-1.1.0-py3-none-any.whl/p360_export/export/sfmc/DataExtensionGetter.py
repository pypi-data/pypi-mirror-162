from pyspark.sql import DataFrame
from FuelSDK import ET_Client, ET_DataExtension

from p360_export.export.sfmc.DataExtensionCreator import DataExtensionCreator
from p360_export.export.sfmc.SFMCData import SFMCData
from p360_export.export.sfmc.DataExtensionFieldUpdater import DataExtensionFieldUpdater


class DataExtensionGetter:
    def __init__(self, data_extension_field_updater: DataExtensionFieldUpdater, data_extension_creator: DataExtensionCreator):
        self.__data_extension_field_updater = data_extension_field_updater
        self.__data_extension_creator = data_extension_creator

    def __get_existing_data_extension(self, sfmc_client: ET_Client, sfmc_data: SFMCData) -> dict:
        data_extension = ET_DataExtension()
        data_extension.auth_stub = sfmc_client
        data_extension.props = ["ObjectID", "CustomerKey"]
        data_extension.search_filter = {"Property": "Name", "SimpleOperator": "equals", "Value": sfmc_data.audience_name}

        response = data_extension.get()
        if response.results:
            return response.results[0]

        return {}

    def get(self, df: DataFrame, sfmc_client: ET_Client, sfmc_data: SFMCData) -> str:
        data_extension = self.__get_existing_data_extension(sfmc_client=sfmc_client, sfmc_data=sfmc_data)
        if data_extension:
            self.__data_extension_field_updater.update(
                df=df, sfmc_client=sfmc_client, sfmc_data=sfmc_data, data_extension_customer_key=data_extension["CustomerKey"]
            )

            return data_extension["ObjectID"]

        return self.__data_extension_creator.create(df, sfmc_client, sfmc_data)
