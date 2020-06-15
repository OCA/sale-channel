#  Copyright (c) Akretion 2020
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from marshmallow_objects import ValidationError, validates, validates_schema

from odoo import _

from odoo.addons.datamodel import fields
from odoo.addons.datamodel.core import Datamodel


class SaleOrderDatamodel(Datamodel):
    _name = "sale.order"

    def run_data_validators(self):
        """ Runs all the validations against in-db data """
        errors = {}
        for addr in ("address_customer", "address_shipping", "address_invoicing"):
            self._validate_address(addr, errors)
        for line in self.lines:
            self._validate_line(line, errors)
        if hasattr(self, "payment"):
            self._validate_payment(self.payment, errors)
        self._validate_misc(errors)
        return errors

    def _validate_address(self, address, errors_sum):
        errors = []
        if hasattr(address, "state_code"):
            state = self._env["res.country.state"].search(
                [("code", "=", address.state_code)]
            )
            if len(state.ids) != 1:
                errors += [_("Could not determine one state from state code")]
        country = self._env["res.country"].search([("code", "=", address.country_code)])
        if len(country.ids) != 1:
            errors += _("Could not determine one country from country code")
        errors_sum["address"] = errors

    def _validate_line(self, line, errors_sum):
        if not errors_sum.get("lines"):
            errors_sum["lines"] = list()
        product = self._env["product.product"].search(
            [("default_code", "=", line.product_code)]
        )
        if len(product.ids) != 1:
            errors_sum["lines"] += [
                _("Could not find one product with supplied product code")
            ]

    def _validate_payment(self, payment, errors_sum):
        errors = []
        acquirer = self._env["payment.acquirer"].search([("name", "=", payment.mode)])
        if not acquirer:
            errors += [_("No payment type found for given mode")]

        if hasattr(payment, "currency_code"):
            currency_id = self._env["res.currency"].search(
                [("name", "=", payment.currency_code)]
            )
            if not currency_id:
                errors += [_("No currency type found for given code")]
        errors_sum["payment"] = errors

    def _validate_misc(self, errors_sum):
        errors = []
        currency_code = self.currency_code
        pricelist = self.pricelist_id
        currency_id = self._env["res.currency"].search([("name", "=", currency_code)])
        pricelist_id = self._env["product.pricelist"].browse(pricelist)
        if currency_id != pricelist_id.currency_id:
            errors += [_("Currency code and pricelist currency do not match")]
        if not hasattr(self.address_customer, "external_id"):
            errors += [_("Missing external ID for customer address")]
        errors_sum["sale_order"] = errors

    address_customer = fields.NestedModel("sale.order.address", required=True)
    address_shipping = fields.NestedModel("sale.order.address", required=True)
    address_invoicing = fields.NestedModel("sale.order.address", required=True)
    lines = fields.NestedModel("sale.order.line", many=True, required=True)
    amount = fields.NestedModel("sale.order.amount", required=True)
    invoice = fields.NestedModel("sale.order.invoice")
    sale_channel = fields.Str()
    payment = fields.NestedModel("sale.order.payment")
    currency_code = fields.Str(required=True)
    pricelist_id = fields.Integer(required=True)
