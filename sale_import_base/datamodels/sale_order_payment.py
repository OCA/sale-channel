#  Copyright (c) Akretion 2020
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.datamodel import fields
from odoo.addons.datamodel.core import Datamodel


class SaleOrderPaymentDatamodel(Datamodel):
    _name = "sale.order.payment"

    mode = fields.Str(required=True)
    amount = fields.Decimal(required=True)
    reference = fields.Str(required=True)
    currency_code = fields.Str(required=True)
    transaction_id = fields.Integer(required=True)
