from odoo import models


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = ["mirakl.binding", "sale.channel.relation", _name]
