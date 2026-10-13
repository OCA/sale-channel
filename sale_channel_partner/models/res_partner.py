#  Copyright (c) Akretion 2020
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    sale_channel_partner_ids = fields.One2many(
        "sale.channel.partner", "partner_id", string="Sale Channel Bindings"
    )
