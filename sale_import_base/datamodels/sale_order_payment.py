#  Copyright (c) Akretion 2020
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from marshmallow_objects import ValidationError, validates

from odoo import _

from odoo.addons.datamodel import fields
from odoo.addons.datamodel.core import Datamodel


class SaleOrderPaymentDatamodel(Datamodel):
    _name = "sale.order.payment"

    mode = fields.Str(required=True)
    amount = fields.Decimal()
    reference = fields.Str()
    currency_code = fields.Str()
    transaction_id = fields.Integer()
