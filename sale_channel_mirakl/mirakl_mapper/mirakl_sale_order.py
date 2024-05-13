from typing import List

import dateutil.parser
import pytz

from odoo import Command

from .mirakl_customer import MiraklCustomer
from .mirakl_import_mapper import MiraklImportMapper
from .mirakl_promotion import MiraklPromotion
from .mirakl_sale_order_line import MiraklSaleOrderLine


class MiraklSaleOrder(MiraklImportMapper):
    _odoo_model = "sale.order"
    _identity_key = "order_id"

    acceptance_decision_date: str
    can_cancel: str
    channel: str
    commercial_id: str
    created_date: str
    currency_iso_code: str
    customer: MiraklCustomer
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

    def get_fiscal_position(self, mirakl_channel):
        country = self.customer.shipping_address.country
        fiscal_position = mirakl_channel.channel_id.fiscal_position_ids.filtered(
            lambda x: x.country_id.name == country
        )
        return fiscal_position

    def get_pricelist(self, mirakl_channel):

        domain = [("name", "=", self.currency_iso_code)]
        currency = mirakl_channel.env["res.currency"].search(domain, limit=1)

        product_pricelist = mirakl_channel.channel_id.pricelist_ids.filtered(
            lambda x: x.currency_id == currency
        )
        return product_pricelist

    def get_order_lines(self, mirakl_channel):
        order_lines_values = []
        for order_line in self.order_lines:
            order_lines_values.append(
                Command.create(order_line.odoo_model_dump(mirakl_channel))
            )
        return order_lines_values

    def odoo_model_dump(self, mirakl_channel):
        return {
            "date_order": self.build_date_order(),
            "partner_id": self.customer.billing_address._get_internal_id(),
            "partner_invoice_id": self.customer.billing_address._get_internal_id(),
            "partner_shipping_id": self.customer.shipping_address._get_internal_id(),
            "user_id": False,
            "fiscal_position_id": self.get_fiscal_position(mirakl_channel).id,
            "name": self.order_id,
            "channel_ids": [Command.link(mirakl_channel.channel_id.id)],
            "analytic_account_id": mirakl_channel.channel_id.analytic_account_id.id,
            # "warehouse_id": mirakl_channel.warehouse_id.id,
            # "payment_mode_id": mirakl_channel.channel_id.payment_mode_id.id,
            "pricelist_id": self.get_pricelist(mirakl_channel).id,
            "order_line": self.get_order_lines(mirakl_channel),
        }
