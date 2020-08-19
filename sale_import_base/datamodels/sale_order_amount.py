#  Copyright (c) Akretion 2020
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo.addons.datamodel import fields
from odoo.addons.datamodel.core import Datamodel


class SaleOrderAmountDatamodel(Datamodel):
    _name = "sale.order.amount"

    amount_tax = fields.Decimal()
    amount_untaxed = fields.Decimal()
    amount_total = fields.Decimal()
