from typing import List
from dataclasses import dataclass


@dataclass
class SFMCData:  # pylint: disable=R0902
    client_id: str
    client_secret: str
    ftp_username: str
    ftp_password: str
    tenant_url: str
    account_id: str
    file_location: str
    config: dict

    @property
    def export_columns(self) -> List[str]:
        return self.config["params"]["export_columns"]

    @property
    def subscriber_key(self) -> str:
        return self.config["params"]["mapping"]["subscriber_key"]

    @property
    def audience_name(self) -> str:
        persona = self.config["personas"][0]

        return f"{persona['persona_name']}-{persona['persona_id']}"

    @property
    def new_field_names(self) -> List[str]:
        return self.export_columns + [self.subscriber_key]
