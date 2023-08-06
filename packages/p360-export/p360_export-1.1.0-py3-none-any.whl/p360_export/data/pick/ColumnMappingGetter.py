from typing import Dict
from p360_export.exceptions.data_picker import EmptyColumnMappingException


class ColumnMappingGetter:
    def get(self, config: dict) -> Dict[str, str]:
        column_mapping = config.get("params", {}).get("mapping", {})
        if not column_mapping:
            raise EmptyColumnMappingException("No column mapping specified. The params.mapping value in the configuration file is empty.")

        return column_mapping
