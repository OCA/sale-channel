from typing import List

import dateutil.parser
import pytz
from pydantic import BaseModel

from odoo import Command

from .mirakl_promotion import MiraklPromotion
from .mirakl_res_partner import MiraklResPartner
from .mirakl_sale_order_line import MiraklSaleOrderLine


class MiraklSaleOrder(BaseModel):

    acceptance_decision_date: str
    can_cancel: str
    channel: str
    commercial_id: str
    created_date: str
    currency_iso_code: str
    customer: MiraklResPartner
    customer_debited_date: str
    customer_notification_email: str = False
    has_customer_message: str
    has_incident: str
    has_invoice: str
    last_updated_date: str
    leadtime_to_ship: int
    order_additional_fields: List[str]
    order_id: str
    order_lines: List[MiraklSaleOrderLine]
    order_state: str
    order_state_reason_code: str
    order_state_reason_label: str
    paymentType: str
    payment_type: str
    payment_workflow: str
    price: float
    promotions: MiraklPromotion
    quote_id: str
    shipping_carrier_code: str
    shipping_company: str
    shipping_price: float
    shipping_tracking: str
    shipping_tracking_url: str
    shipping_type_code: str
    shipping_type_label: str
    shipping_zone_code: str = ""
    shipping_zone_label: str
    total_commission: float
    total_price: float
    transaction_date: str

    @classmethod
    def build_mirakl_sale_order(cls, data):
        return cls(**data)

    def build_date_order(self):
        date_order = dateutil.parser.parse(self.created_date)
        date_order = date_order.astimezone(pytz.utc).replace(tzinfo=None)
        return date_order

    def get_internal_partner(
        self, mirakl_channel, billing_partner_data, partner_mirakl_id
    ):  # TODO
        binding_model = "res.partner"

        if not partner_mirakl_id:
            partner_mirakl_id = mirakl_channel._generate_hash_key(billing_partner_data)
        partner = mirakl_channel._get_binding(partner_mirakl_id, binding_model)

        assert partner is not None, (
            "partner %s should have been imported in "
            "MiraklSaleOrderImporter._import_dependencies" % billing_partner_data
        )
        return partner

    def build_partner(self, mirakl_channel):
        partner_mirakl_id = False
        if self.customer.customer_id:
            partner_mirakl_id = self.customer.customer_id + "_billing"
        billing_partner_data = self.customer.billing_address
        billing_partner_data.customer_notification_email = (
            self.customer_notification_email
        )
        partner = self.get_internal_partner(
            mirakl_channel, billing_partner_data, partner_mirakl_id
        )
        return partner

    def get_partner_shipping_id(self, mirakl_channel):
        partner_mirakl_id = False
        if self.customer.customer_id:
            partner_mirakl_id = self.customer.customer_id + "_billing"
        partner = self.get_internal_partner(
            mirakl_channel, self.customer.shipping_address, partner_mirakl_id
        )
        return partner.id

    def _get_fiscal_position_id(self, mirakl_channel):
        country = self.customer.shipping_address.country
        fiscal_position = mirakl_channel.channel_id.fiscal_position_ids.filtered(
            lambda x: x.country_id.name == country
        )
        return fiscal_position

    def _get_pricelist_id(self):  # TODO
        return self.currency_iso_code
        # currency = self.env["res.currency"].search([("name", "=", currency_code)])

    def odoo_model_dump(self, mirakl_channel):
        partner = self.build_partner(mirakl_channel)
        return {
            "date_order": self.build_date_order(),
            "partner_id": partner.id,
            "partner_invoice_id": partner.id,
            "partner_shipping_id": self.get_partner_shipping_id(mirakl_channel),
            "user_id": False,
            # "analytic_account_id": mirakl_channel.analytic_account_id.id,  # TODO
            # "fiscal_position_id": self._get_fiscal_position_id(mirakl_channel).id,
            # "warehouse_id": mirakl_channel.warehouse_id.id ,  # TODO
            # "payment_mode_id": mirakl_channel.payment_mode_id.id,  # TODO
            "name": self.order_id,
            # "pricelit_id": self._get_pricelist_id(),
            "channel_ids": [Command.link(mirakl_channel.channel_id.id)],
        }
