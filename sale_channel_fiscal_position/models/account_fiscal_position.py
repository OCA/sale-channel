from odoo import fields, models


class AccountFiscalPosition(models.Model):
    _name = "account.fiscal.position"
    _inherit = [_name, "sale.channel.owner"]

    channel_ids = fields.Many2many(
        comodel_name="sale.channel",
        relation="fiscal_position_sale_channel_rel",
        column1="fiscal_position_id",
        column2="sale_channel_id",
        string="Binded Sale Channels",
    )
