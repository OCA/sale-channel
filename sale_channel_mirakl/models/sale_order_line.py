from odoo import models


class SaleOrderLine(models.Model):
    _name = "sale.order.line"
    _inherit = [
        _name,
        "mirakl.channel.relation",
    ]
