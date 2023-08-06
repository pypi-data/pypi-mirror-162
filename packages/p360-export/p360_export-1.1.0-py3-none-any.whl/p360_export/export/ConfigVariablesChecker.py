from p360_export.exceptions.exporter import ConfigVariableNotSetException


class ConfigVariablesChecker:
    def check(self, export_destination, keys):
        for key_name, key_value in keys.items():
            if not key_value:
                raise ConfigVariableNotSetException(f"p360.{export_destination}.{key_name} not set")
