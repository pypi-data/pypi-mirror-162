from FuelSDK import ET_Client


class ImportDefinitionExecutor:
    def execute(self, sfmc_client: ET_Client, import_definition_id: str):
        request = sfmc_client.soap_client.factory.create("PerformRequestMsg")
        definition = sfmc_client.soap_client.factory.create("ImportDefinition")

        definition.ObjectID = import_definition_id

        request.Definitions.Definition = definition
        request.Action = "start"

        sfmc_client.soap_client.service.Perform(None, request)
