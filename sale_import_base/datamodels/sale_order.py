from marshmallow_objects import ValidationError, validates, validates_schema

from odoo import _

from odoo.addons.datamodel import fields
from odoo.addons.datamodel.datamodels.base import BaseDatamodel

FIELDS_REQUIRED_address_customer = ["email"]


class SaleOrderDatamodel(BaseDatamodel):
    _name = "sale.order"

    @validates("sale_channel")
    def _validate_sale_channel(self, channel_name):
        if not channel_name:
            return
        channel = self._env["sale.channel"].search([("name", "=", channel_name)])
        if len(channel.ids) != 1:
            raise ValidationError(
                _("Could not determine one channel from channel name")
            )

    @validates_schema
    def _validate_import(self, data, **kwargs):
        currency_code = data["currency_code"]
        pricelist = data["pricelist_id"]
        currency_id = self._env["res.currency"].search([("name", "=", currency_code)])
        pricelist_id = self._env["product.pricelist"].browse(pricelist)
        if currency_id != pricelist_id.currency_id:
            raise ValidationError(
                _("Currency code and pricelist currency do not match")
            )
        if not data["address_customer"].external_id:
            raise ValidationError(_("Missing external ID for customer address"))

    address_customer = fields.NestedModel("sale.order.address", required=True)
    address_shipping = fields.NestedModel("sale.order.address", required=True)
    address_invoicing = fields.NestedModel("sale.order.address", required=True)
    lines = fields.NestedModel("sale.order.line", many=True, required=True)
    amount = fields.NestedModel("sale.order.amount", required=True)
    transaction_id = fields.Integer()  # DISCUSSION: intégré dans payment ?
    invoice = fields.NestedModel("sale.order.invoice")
    sale_channel = fields.Str()
    delivery_carrier = fields.NestedModel("delivery.carrier")
    payment = fields.NestedModel("sale.order.payment")
    currency_code = fields.Str(required=True)
    pricelist_id = fields.Integer(required=True)
