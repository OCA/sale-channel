from marshmallow_objects import ValidationError, validates

from odoo import _

from odoo.addons.datamodel import fields
from odoo.addons.datamodel.datamodels.base import BaseDatamodel


class SaleOrderPaymentDatamodel(BaseDatamodel):
    _name = "sale.order.payment"

    @validates("mode")
    def _validate_mode(self, mode):
        acquirer = self._env["payment.acquirer"].search([("name", "=", mode)])
        if not acquirer:
            raise ValidationError(_("No payment type found for given mode"))

    @validates("currency_code")
    def _validate_currency_id(self, code):
        currency_id = self._env["res.currency"].search([("name", "=", code)])
        if code and not currency_id:
            raise ValidationError(_("No currency type found for given code"))

    mode = fields.Str(required=True)
    amount = fields.Decimal()
    reference = fields.Str()
    currency_code = fields.Str()
