#  Copyright (c) Akretion 2020
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo.addons.datamodel import fields
from odoo.addons.datamodel.core import Datamodel


class SaleOrderInvoiceDatamodel(Datamodel):
    _name = "sale.order.invoice"

    date = fields.Date(required=True)
    number = fields.Str(required=True)
