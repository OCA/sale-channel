from .mirakl_json import MiraklJson


class MiraklShippingAddress(MiraklJson):
    additional_info: str
    city: str
    civility: str
    company: str
    country: str
    country_iso_code: str | None
    firstname: str
    lastname: str
    phone: str
    phone_secondary: str
    state: str
    street_1: str
    street_2: str
    zip_code: str
    email: str = ""
