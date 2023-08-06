from pyspark.sql import DataFrame

from p360_export.export.ExporterInterface import ExporterInterface
from p360_export.export.sfmc.DataExtensionGetter import DataExtensionGetter
from p360_export.export.sfmc.SFTPUploader import SFTPUploader
from p360_export.export.sfmc.ImportDefinitionGetter import ImportDefinitionGetter
from p360_export.export.sfmc.ImportDefinitionExecutor import ImportDefinitionExecutor
from p360_export.export.sfmc.SFMCClientGetter import SFMCClientGetter
from p360_export.export.sfmc.SFMCDataGetter import SFMCDataGetter


class SFMCExporter(ExporterInterface):
    def __init__(
        self,
        sfmc_data_getter: SFMCDataGetter,
        sftp_uploader: SFTPUploader,
        sfmc_client_getter: SFMCClientGetter,
        data_extension_getter: DataExtensionGetter,
        import_definition_getter: ImportDefinitionGetter,
        import_definition_executor: ImportDefinitionExecutor,
    ):
        self.__sfmc_data_getter = sfmc_data_getter
        self.__sftp_uploader = sftp_uploader
        self.__sfmc_client_getter = sfmc_client_getter
        self.__data_extension_getter = data_extension_getter
        self.__import_definition_getter = import_definition_getter
        self.__import_definition_executor = import_definition_executor

    @property
    def export_destination(self):
        return "sfmc"

    def export(self, df: DataFrame, config: dict):
        sfmc_data = self.__sfmc_data_getter.get(config=config, export_destination=self.export_destination)
        sfmc_client = self.__sfmc_client_getter.get(sfmc_data)

        self.__sftp_uploader.upload(df, sfmc_data)

        data_extension_id = self.__data_extension_getter.get(df, sfmc_client, sfmc_data)

        import_definition_id = self.__import_definition_getter.get(sfmc_client, sfmc_data, data_extension_id)

        self.__import_definition_executor.execute(sfmc_client, import_definition_id)
