from odoo import fields, models


class AccountPaymentMode(models.Model):
    _inherit = "account.payment.mode"

    sale_channel_ids = fields.One2many(
        comodel_name="sale.channel", inverse_name="payment_mode_id"
    )
