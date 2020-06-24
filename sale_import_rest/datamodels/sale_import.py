#  Copyright (c) Akretion 2020
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.datamodel import fields
from odoo.addons.datamodel.core import Datamodel


class SaleImportInput(Datamodel):
    _name = "sale.import.input"

    sale_orders = fields.NestedModel("sale.order", required=True, many=True)


class SaleImportOutput(Datamodel):
    _name = "sale.import.output"

    chunk_id = fields.Integer()
