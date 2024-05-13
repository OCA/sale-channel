from odoo import fields, models


class SaleChannel(models.Model):
    _inherit = "sale.channel"

    fiscal_position_ids = fields.Many2many(
        comodel_name="account.fiscal.position",
    )

    analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Analytic account",
        help="If specified, this analytic account will be used to fill the "
        "field  on the sale order created by the connector.",
    )

    payment_mode_id = fields.Many2one(
        string="Payment Mode", comodel_name="account.payment.mode"
    )
