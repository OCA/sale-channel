#  Copyright (c) Akretion 2020
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.datamodel import fields
from odoo.addons.datamodel.core import Datamodel


class SaleOrderCustomerDatamodel(Datamodel):
    _inherit = "sale.order.address"
    _name = "sale.order.customer"

    external_id = fields.Str(required=True)
