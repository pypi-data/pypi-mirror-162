from google.ads.googleads.client import GoogleAdsClient


class UserListGetter:
    def __init__(self, customer_id: str):
        self.__customer_id = customer_id
        self.__page_size = 10000

    def __get_existing_user_lists(self, client: GoogleAdsClient) -> list:
        request = client.get_type(name="SearchGoogleAdsRequest")
        request.customer_id = self.__customer_id
        request.query = "SELECT user_list.id, user_list.name FROM user_list"
        request.page_size = self.__page_size

        response = client.get_service(name="GoogleAdsService").search(request=request)

        return response.results

    def __create_user_list(self, client: GoogleAdsClient, user_list_name: str) -> str:
        user_list_service = client.get_service(name="UserListService")
        user_list_operation = client.get_type(name="UserListOperation")

        user_list = user_list_operation.create
        user_list.name = user_list_name
        user_list.crm_based_user_list.upload_key_type = client.enums.CustomerMatchUploadKeyTypeEnum.CONTACT_INFO
        user_list.membership_life_span = 10

        response = user_list_service.mutate_user_lists(customer_id=self.__customer_id, operations=[user_list_operation])

        return response.results[0].resource_name

    def get(self, client: GoogleAdsClient, user_list_name: str) -> str:
        for user_list in self.__get_existing_user_lists(client=client):
            if user_list.user_list.name == user_list_name:
                return user_list.user_list.resource_name

        return self.__create_user_list(client=client, user_list_name=user_list_name)
