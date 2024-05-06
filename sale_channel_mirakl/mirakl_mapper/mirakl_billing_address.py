from pydantic import BaseModel


class MiraklBillingAddress(BaseModel):
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
    customer_notification_email: str = ""
