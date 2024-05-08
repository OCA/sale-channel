from .res_partner_builder import ResPartnerBuilder


class MiraklPartnerAddress(ResPartnerBuilder):
    _odoo_model = "res.partner"
    _identity_key = "customer_id"

    city: str
    country: str
    phone: str
    phone_secondary: str
    state: str
    street_1: str
    street_2: str
    zip_code: str
    email: str = ""
