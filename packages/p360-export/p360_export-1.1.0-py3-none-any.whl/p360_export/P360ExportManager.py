from typing import List

from p360_export.data.pick.DataPickerInterface import DataPickerInterface
from p360_export.exceptions.manager import ExportDestinationNotSetException, InvalidExportDestinationException
from p360_export.export.ExporterInterface import ExporterInterface


class P360ExportManager:
    def __init__(
        self,
        data_pickers: List[DataPickerInterface],
        exporters: List[ExporterInterface],
    ):
        self.__data_pickers = data_pickers
        self.__exporters = exporters

    def __get_export_destination(self, config: dict) -> str:
        return config.get("destination_type")

    def __select_service(self, services: List, config: dict):
        export_destination = self.__get_export_destination(config)

        if not export_destination:
            raise ExportDestinationNotSetException("Export destination is not set.")

        for service in services:
            if service.export_destination == export_destination:
                return service

        raise InvalidExportDestinationException(f"No service with alias {export_destination} found.")

    def get_data_picker(self, config: dict):
        return self.__select_service(services=self.__data_pickers, config=config)

    def get_exporter(self, config: dict):
        return self.__select_service(services=self.__exporters, config=config)
