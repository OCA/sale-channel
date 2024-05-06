from odoo import fields, models


class SaleChannel(models.Model):
    _inherit = "sale.channel"

    fiscal_position_ids = fields.Many2many(
        comodel_name="account.fiscal.position",
    )
