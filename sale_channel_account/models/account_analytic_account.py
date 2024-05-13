from odoo import fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    sale_channel_ids = fields.One2many(
        comodel_name="sale.channel", inverse_name="analytic_account_id"
    )
