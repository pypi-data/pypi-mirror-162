from p360_export.P360ExportManager import P360ExportManager
from p360_export.config.ConfigGetterInterface import ConfigGetterInterface
from p360_export.data.build.FeatureStoreDataBuilder import FeatureStoreDataBuilder
from p360_export.query.QueryBuilder import QueryBuilder


class P360ExportRunner:
    def __init__(
        self,
        manager: P360ExportManager,
        config_getter: ConfigGetterInterface,
        query_builder: QueryBuilder,
        data_builder: FeatureStoreDataBuilder,
    ):
        self.__manager = manager
        self.__config_getter = config_getter
        self.__query_builder = query_builder
        self.__data_builder = data_builder

    def __get_config_id(self, config_url: str):
        return config_url.split("/")[-1].replace(".json", "")

    def export(self, config_url: str):
        config = self.__config_getter.get(config_id=self.__get_config_id(config_url))

        query, table_id = self.__query_builder.build(config)

        base_df = self.__data_builder.build(config)

        df = self.__manager.get_data_picker(config).pick(df=base_df, query=query, table_id=table_id, config=config)

        self.__manager.get_exporter(config).export(df, config)
