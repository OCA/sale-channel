from odoo import models


class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = [_name, "mirakl.binding", "sale.channel.owner"]
