from FuelSDK import ET_Client, ET_Post, ET_Get

from p360_export.exceptions.exporter import UnableToCreateImportDefinition
from p360_export.export.sfmc.SFMCData import SFMCData


class ImportDefinitionGetter:
    def __create_import_definition_properties(self, sfmc_data: SFMCData, data_extension_id: str) -> dict:
        return {
            "Name": sfmc_data.audience_name,
            "DestinationObject": {"ObjectID": data_extension_id},
            "RetrieveFileTransferLocation": {"CustomerKey": sfmc_data.file_location},
            "AllowErrors": True,
            "UpdateType": "Overwrite",
            "FileSpec": f"{sfmc_data.audience_name}.csv",
            "FileType": "CSV",
            "FieldMappingType": "InferFromColumnHeadings",
        }

    def __create_import_definition(self, sfmc_client: ET_Client, import_definition_properties: dict) -> str:
        response = ET_Post(auth_stub=sfmc_client, obj_type="ImportDefinition", props=import_definition_properties)

        if response.results[0]["StatusCode"] == "Error":
            raise UnableToCreateImportDefinition(str(response.results))

        return response.results[0]["NewObjectID"]

    def get(self, sfmc_client: ET_Client, sfmc_data: SFMCData, data_extension_id: str) -> str:
        props = ["ObjectID"]
        search_filter = {"Property": "Name", "SimpleOperator": "equals", "Value": sfmc_data.audience_name}

        response = ET_Get(auth_stub=sfmc_client, obj_type="ImportDefinition", props=props, search_filter=search_filter)
        if response.results:
            return response.results[0]["ObjectID"]

        import_definition_properties = self.__create_import_definition_properties(sfmc_data, data_extension_id)

        return self.__create_import_definition(sfmc_client, import_definition_properties)
