from odoo import models


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = ["mirakl.binding", _name]
