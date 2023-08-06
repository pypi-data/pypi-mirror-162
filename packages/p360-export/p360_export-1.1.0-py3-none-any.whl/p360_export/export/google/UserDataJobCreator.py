from google.ads.googleads.client import GoogleAdsClient


class UserDataJobCreator:
    def __init__(self, customer_id: str):
        self.__customer_id = customer_id

    def create(self, client: GoogleAdsClient, user_data_service, user_list_resource_name: str) -> str:
        user_data_job = client.get_type(name="OfflineUserDataJob")

        user_data_job.type_ = client.enums.OfflineUserDataJobTypeEnum.CUSTOMER_MATCH_USER_LIST
        user_data_job.customer_match_user_list_metadata.user_list = user_list_resource_name

        response = user_data_service.create_offline_user_data_job(customer_id=self.__customer_id, job=user_data_job)

        return response.resource_name
