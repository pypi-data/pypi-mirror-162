from typing import Sequence

from google.ads.googleads.client import GoogleAdsClient
from p360_export.export.google.UserDataJobCreator import UserDataJobCreator

from p360_export.export.google.UserDataJobOperationRequestGetter import UserDataJobOperationRequestGetter


class UserDataSender:
    def __init__(
        self, user_data_job_operation_request_getter: UserDataJobOperationRequestGetter, user_data_job_creator: UserDataJobCreator
    ):
        self.__user_data_job_operation_request_getter = user_data_job_operation_request_getter
        self.__user_data_job_creator = user_data_job_creator

    def send(self, client: GoogleAdsClient, user_list_resource_name: str, hashed_emails: Sequence[str]):
        user_data_service = client.get_service(name="OfflineUserDataJobService")

        user_data_job_resource_name = self.__user_data_job_creator.create(
            client=client, user_data_service=user_data_service, user_list_resource_name=user_list_resource_name
        )

        request = self.__user_data_job_operation_request_getter.get(
            user_data_job_resource_name=user_data_job_resource_name, client=client, hashed_emails=hashed_emails
        )

        user_data_service.add_offline_user_data_job_operations(request=request)
        user_data_service.run_offline_user_data_job(resource_name=user_data_job_resource_name)
