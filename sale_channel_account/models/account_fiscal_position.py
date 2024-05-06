from odoo import fields, models


class AccountFiscalPosition(models.Model):
    _name = "account.fiscal.position"
    _inherit = [_name, "sale.channel.owner"]

    channel_ids = fields.Many2many(
        comodel_name="sale.channel",
        string="Binded Sale Channels",
    )
