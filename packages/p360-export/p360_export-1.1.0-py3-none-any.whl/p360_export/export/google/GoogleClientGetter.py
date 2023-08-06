from google.ads.googleads.client import GoogleAdsClient

from p360_export.export.google.GoogleConfigVariablesGetter import GoogleConfigVariablesGetter


class GoogleClientGetter:
    def __init__(self, google_config_variables_getter: GoogleConfigVariablesGetter):
        self.__google_config_variables_getter = google_config_variables_getter

    def get(self, export_destination: str) -> GoogleAdsClient:
        config_variables = self.__google_config_variables_getter.get(export_destination=export_destination)

        credentials = {
            "developer_token": config_variables["developer_token"],
            "refresh_token": config_variables["refresh_token"],
            "client_id": config_variables["client_id"],
            "client_secret": config_variables["client_secret"],
            "use_proto_plus": True,
        }

        return GoogleAdsClient.load_from_dict(config_dict=credentials)
