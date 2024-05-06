from odoo import fields, models


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = ["mirakl.binding", _name]

    mirakl_code = fields.Char()
