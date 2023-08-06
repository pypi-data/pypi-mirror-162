from dataclasses import dataclass


@dataclass(frozen=True)
class FacebookData:
    column_map = {
        "email": "EMAIL",
        "phone": "PHONE",
        "first name": "FN",
        "last name": "LN",
        "city": "CT",
        "state/province": "ST",
        "country": "COUNTRY",
        "date of birth": "DOBD",
        "year of birth": "DOBY",
        "zip/postal code": "ZIP",
        "gender": "GEN",
        "mobile advertiser id": "MADID",
    }
