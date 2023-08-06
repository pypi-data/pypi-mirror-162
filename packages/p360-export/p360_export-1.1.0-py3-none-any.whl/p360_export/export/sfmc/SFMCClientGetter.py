from FuelSDK import ET_Client

from p360_export.export.sfmc.SFMCData import SFMCData


class SFMCClientGetter:
    def get(self, sfmc_data: SFMCData) -> ET_Client:
        client_config = {
            "clientid": sfmc_data.client_id,
            "clientsecret": sfmc_data.client_secret,
            "authenticationurl": f"https://{sfmc_data.tenant_url}.auth.marketingcloudapis.com/",
            "useOAuth2Authentication": "True",
            "accountId": sfmc_data.account_id,
            "scope": "data_extensions_read data_extensions_write automations_write automations_read",
            "applicationType": "server",
        }

        return ET_Client(params=client_config)
