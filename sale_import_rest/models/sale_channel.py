#  Copyright (c) Akretion 2020
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

from odoo import fields, models


class SaleChannel(models.Model):
    _inherit = "sale.channel"

    api_key_id = fields.Many2one(
        "auth.api.key", string="REST Api Key", ondelete="set null"
    )
