from odoo import fields, models


class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = ["mirakl.binding", _name]

    sale_channel_id = fields.Many2one("sale.channel", ondelete="restrict")
