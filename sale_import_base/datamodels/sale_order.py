#  Copyright (c) Akretion 2020
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo.addons.datamodel import fields
from odoo.addons.datamodel.core import Datamodel


class SaleOrderDatamodel(Datamodel):
    _name = "sale.order"

    name = fields.Str(required=True)
    address_customer = fields.NestedModel("sale.order.customer", required=True)
    address_shipping = fields.NestedModel("sale.order.address", required=True)
    address_invoicing = fields.NestedModel("sale.order.address", required=True)
    lines = fields.NestedModel("sale.order.line", many=True, required=True)
    amount = fields.NestedModel("sale.order.amount", required=True)
    invoice = fields.NestedModel("sale.order.invoice")
    payment = fields.NestedModel("sale.order.payment")
    pricelist_id = fields.Integer(required=True)
