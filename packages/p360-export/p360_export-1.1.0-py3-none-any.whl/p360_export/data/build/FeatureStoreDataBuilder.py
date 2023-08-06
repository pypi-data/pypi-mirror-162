from pyspark.sql import DataFrame
from featurestorebundle.entity.getter import get_entity
from featurestorebundle.feature.FeatureStore import FeatureStore
from typing import List, Set

from p360_export.data.build.DataBuilderInterface import DataBuilderInterface


class FeatureStoreDataBuilder(DataBuilderInterface):
    def __init__(self, feature_store: FeatureStore) -> None:
        self.__feature_store = feature_store

    @property
    def data_location(self):
        return "feature_store"

    def build(self, config: dict) -> DataFrame:
        entity = get_entity()
        attributes = self._get_required_attribute_names(config=config)

        return self.__feature_store.get_latest_attributes(entity.name, attributes=attributes)

    def _get_required_attribute_names(self, config: dict) -> List[str]:
        attributes_from_export_columns = set(config.get("params", {}).get("export_columns", []))
        attributes_from_mapping = set(config.get("params", {}).get("mapping", {}).values())
        personas = config.get("personas", [])
        attributes_from_condition = self._get_attributes_from_personas(personas)

        return list(attributes_from_export_columns | attributes_from_mapping | attributes_from_condition)

    def _get_attributes_from_personas(self, personas: List[dict]) -> Set[str]:
        attributes = set()
        for persona in personas:
            attributes.update(self._get_attributes_from_definition_persona(persona["definition_persona"]))

        return attributes

    def _get_attributes_from_definition_persona(self, definition_persona: List[dict]) -> Set[str]:
        attributes = set()
        for definition_part in definition_persona:
            attributes.update(self._get_attribute_ids(definition_part["attributes"]))

        return attributes

    def _get_attribute_ids(self, attributes: List[dict]) -> Set[str]:
        return {attribute["id"] for attribute in attributes}
