#  Copyright (c) Akretion 2020
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.datamodel import fields
from odoo.addons.datamodel.core import Datamodel


class SaleOrderLineDatamodel(Datamodel):
    _name = "sale.order.line"

    product_code = fields.Str(required=True)
    qty = fields.Decimal(required=True)
    price_unit = fields.Decimal(required=True)
    description = fields.Str()
    discount = fields.Decimal()
