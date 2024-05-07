from pydantic import BaseModel


class MiraklPartnerAddress(BaseModel):
    _odoo_model = "res.partner"
    _identity_key = "customer_id"

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
    customer_id: str = ""
