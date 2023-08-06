from typing import List

from pyspark.sql import DataFrame
from FuelSDK import ET_Delete, ET_Patch, ET_DataExtension_Column, ET_Client
from p360_export.export.sfmc.SFMCData import SFMCData

from p360_export.export.sfmc.DataExtensionFieldCreator import DataExtensionFieldCreator


class DataExtensionFieldUpdater:
    def __init__(self, data_extension_field_creator: DataExtensionFieldCreator):
        self.__data_extension_field_creator = data_extension_field_creator

    def __get_data_extension_fields(self, sfmc_client: ET_Client, data_extension_customer_key: str) -> List[dict]:
        data_extension_column = ET_DataExtension_Column()
        data_extension_column.auth_stub = sfmc_client
        data_extension_column.props = ["Name", "CustomerKey", "ObjectID"]
        data_extension_column.search_filter = {"Property": "CustomerKey", "SimpleOperator": "like", "Value": data_extension_customer_key}

        response = data_extension_column.get()

        return response.results

    def __get_removable_fields(self, sfmc_data: SFMCData, existing_fields: List[dict]) -> List[dict]:
        removable_fields = []

        for field in existing_fields:
            if field["Name"] not in sfmc_data.new_field_names:
                removable_fields.append({"Field": {"ObjectID": field["ObjectID"]}})

        return removable_fields

    def __remove_data_extension_fields(self, removable_fields: List[dict], sfmc_client: ET_Client, data_extension_customer_key: str):
        if removable_fields:
            props = {"CustomerKey": data_extension_customer_key, "Fields": removable_fields}
            ET_Delete(auth_stub=sfmc_client, obj_type="DataExtension", props=props)

    def __get_addable_fields(self, df: DataFrame, sfmc_data: SFMCData, existing_fields: List[dict]) -> List[dict]:
        addable_fields = []
        existing_field_names = [field["Name"] for field in existing_fields]

        for field_name in sfmc_data.new_field_names:
            if field_name not in existing_field_names:
                field_properties = self.__data_extension_field_creator.create(df, field_name)
                addable_fields.append({"Field": field_properties})

        return addable_fields

    def __add_data_extension_fields(self, addable_fields: List[dict], sfmc_client: ET_Client, data_extension_customer_key: str):
        if addable_fields:
            props = {"CustomerKey": data_extension_customer_key, "Fields": addable_fields}
            ET_Patch(auth_stub=sfmc_client, obj_type="DataExtension", props=props)

    def update(self, df: DataFrame, sfmc_client: ET_Client, sfmc_data: SFMCData, data_extension_customer_key: str):
        existing_fields = self.__get_data_extension_fields(sfmc_client, data_extension_customer_key)

        addable_fields = self.__get_addable_fields(df, sfmc_data, existing_fields)
        self.__add_data_extension_fields(addable_fields, sfmc_client, data_extension_customer_key)

        removable_fields = self.__get_removable_fields(sfmc_data, existing_fields)
        self.__remove_data_extension_fields(removable_fields, sfmc_client, data_extension_customer_key)
