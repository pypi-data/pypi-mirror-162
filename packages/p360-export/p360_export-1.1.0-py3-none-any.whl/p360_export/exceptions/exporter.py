class ExporterException(Exception):
    pass


class ConfigVariableNotSetException(ExporterException):
    pass


class UnableToReplaceAudience(ExporterException):
    pass


class UnableToCreateImportDefinition(ExporterException):
    pass


class UnableToCreateDataExtension(ExporterException):
    pass
