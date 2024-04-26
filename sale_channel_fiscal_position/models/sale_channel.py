from odoo import fields, models


class SaleChannel(models.Model):
    _inherit = "sale.channel"

    fiscal_position_ids = fields.Many2many(
        comodel_name="account.fiscal.position",
        relation="fiscal_position_sale_channel_rel",
        column1="sale_channel_id",
        column2="account_fiscal_position_id",
    )
