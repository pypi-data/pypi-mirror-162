from typing import Sequence

from google.ads.googleads.client import GoogleAdsClient
from p360_export.export.google.UserDataJobOperationGetter import UserDataJobOperationGetter


class UserDataJobOperationRequestGetter:
    def __init__(self, user_data_job_operation_getter: UserDataJobOperationGetter):
        self.__max_amount_of_ids_in_operation = 20
        self.__user_data_job_operation_getter = user_data_job_operation_getter

    def get(self, user_data_job_resource_name: str, client: GoogleAdsClient, hashed_emails: Sequence[str]):
        request = client.get_type(name="AddOfflineUserDataJobOperationsRequest")

        request.resource_name = user_data_job_resource_name
        request.enable_partial_failure = False

        for idx in range(len(hashed_emails), self.__max_amount_of_ids_in_operation):
            hashed_emails_subset = hashed_emails[idx : idx + self.__max_amount_of_ids_in_operation]
            request.operations.append(self.__user_data_job_operation_getter.get(client, hashed_emails_subset))

        return request
