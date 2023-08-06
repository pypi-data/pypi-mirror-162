from pyspark.sql import DataFrame


from p360_export.export.AudienceNameGetter import AudienceNameGetter
from p360_export.export.ExporterInterface import ExporterInterface
from p360_export.export.google.GoogleClientGetter import GoogleClientGetter
from p360_export.export.google.UserDataSender import UserDataSender
from p360_export.export.google.UserListGetter import UserListGetter
from p360_export.utils.ColumnHasher import ColumnHasher


class GoogleAdsExporter(ExporterInterface):
    def __init__(
        self,
        audience_name_getter: AudienceNameGetter,
        google_client_getter: GoogleClientGetter,
        user_data_sender: UserDataSender,
        user_list_getter: UserListGetter,
        column_hasher: ColumnHasher,
    ):
        self.__audience_name_getter = audience_name_getter
        self.__google_client_getter = google_client_getter
        self.__user_data_sender = user_data_sender
        self.__user_list_getter = user_list_getter
        self.__column_hasher = column_hasher

    @property
    def export_destination(self):
        return "google_ads"

    def export(self, df: DataFrame, config: dict):
        client = self.__google_client_getter.get(export_destination=self.export_destination)
        user_list_name = self.__audience_name_getter.get(config=config)

        hashed_df = self.__column_hasher.hash(df=df, columns=df.columns, converter=self.__column_hasher.sha256)
        hashed_emails = list(hashed_df.select("email").toPandas()["email"])

        user_list_resource_name = self.__user_list_getter.get(client=client, user_list_name=user_list_name)

        self.__user_data_sender.send(client=client, user_list_resource_name=user_list_resource_name, hashed_emails=hashed_emails)
