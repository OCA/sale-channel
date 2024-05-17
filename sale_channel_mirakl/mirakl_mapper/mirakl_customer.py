from typing import Optional

from .mirakl_billing_address import MiraklBillingAddress
from .mirakl_import_mapper import MiraklImportMapper
from .mirakl_shipping_address import MiraklShippingAddress
from .res_partner_builder import ResPartnerBuilder


class MiraklCustomer(MiraklImportMapper, ResPartnerBuilder):
    _odoo_model = "res.partner"
    _identity_key = "customer_id"

    billing_address: MiraklBillingAddress
    locale: str = ""
    shipping_address: MiraklShippingAddress
    shipping_zone_code: Optional[str] = None

    def __init__(self, **kwargs):
        """
        allows you to update the data for the construction of
        the billing_address and shipping_address objects
        which are also partners

        :param kwargs: dictionary containing values for constructing the
        customer including subdictionaries for its object attributes
        """
        billing_address = kwargs.get("billing_address", {})
        billing_address["customer_id"] = kwargs.get("customer_id", "") + "_billing"
        kwargs["billing_address"] = billing_address

        shipping_address = kwargs.get("shipping_address", {})
        shipping_address["customer_id"] = kwargs.get("customer_id", "") + "_shipping"
        kwargs["shipping_address"] = shipping_address
        super().__init__(**kwargs)
