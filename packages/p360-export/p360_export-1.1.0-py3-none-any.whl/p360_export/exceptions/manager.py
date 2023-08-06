class ManagerException(Exception):
    pass


class ExportDestinationNotSetException(ManagerException):
    pass


class InvalidExportDestinationException(ManagerException):
    pass
