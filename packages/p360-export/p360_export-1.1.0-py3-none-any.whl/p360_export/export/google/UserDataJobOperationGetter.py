from typing import List, Sequence

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.v10.common.types.offline_user_data import UserIdentifier


class UserDataJobOperationGetter:
    def __prepare_user_ids(self, client: GoogleAdsClient, hashed_emails: Sequence[str]) -> List[UserIdentifier]:
        user_ids = []
        for hashed_email in hashed_emails:
            user_id = client.get_type(name="UserIdentifier")
            user_id.hashed_email = hashed_email
            user_ids.append(user_id)

        return user_ids

    def get(self, client: GoogleAdsClient, hashed_emails: Sequence[str]):
        user_ids = self.__prepare_user_ids(client=client, hashed_emails=hashed_emails)

        user_data_job_operation = client.get_type(name="OfflineUserDataJobOperation")
        user_data_job_operation.remove_all = True
        user_data_job_operation.create.user_identifiers.extend(user_ids)

        return user_data_job_operation
