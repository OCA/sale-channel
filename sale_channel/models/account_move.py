#  Copyright (c) Akretion 2020
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    sale_channel_id = fields.Many2one(
        "sale.channel", string="Sale Channel", ondelete="restrict"
    )
