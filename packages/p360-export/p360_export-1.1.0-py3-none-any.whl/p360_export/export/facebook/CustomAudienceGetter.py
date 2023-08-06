from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.customaudience import CustomAudience

from p360_export.exceptions.exporter import UnableToReplaceAudience
from p360_export.export.AudienceNameGetter import AudienceNameGetter


class CustomAudienceGetter:
    def __init__(self, audience_name_getter: AudienceNameGetter):
        self.__audience_name_getter = audience_name_getter

    def __create_custom_audience(self, ad_account: AdAccount, audience_name: str) -> CustomAudience:
        parameters = {"name": audience_name, "subtype": "CUSTOM", "customer_file_source": "USER_PROVIDED_ONLY"}
        return ad_account.create_custom_audience(params=parameters)

    def __check_audience_availability(self, custom_audience: dict):
        if custom_audience["operation_status"]["code"] != 200:
            raise UnableToReplaceAudience("Unable to replace users, another user replacement is under process")

    def get(self, config: dict, ad_account: AdAccount) -> CustomAudience:
        audience_name = self.__audience_name_getter.get(config)

        custom_audiences = ad_account.get_custom_audiences(fields=["name", "operation_status"])
        for custom_audience in custom_audiences:
            if custom_audience["name"] == audience_name:
                self.__check_audience_availability(custom_audience=custom_audience)
                return custom_audience

        return self.__create_custom_audience(ad_account, audience_name)
