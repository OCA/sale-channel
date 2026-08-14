#  Copyright (c) Akretion 2020
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)
from odoo import fields, models


class SaleChannelPartner(models.Model):
    _name = "sale.channel.partner"
    _description = "Sale Channel Partner"

    sale_channel_id = fields.Many2one(
        "sale.channel", "Sale Channel", required=True, ondelete="cascade"
    )
    partner_id = fields.Many2one(
        "res.partner", "Contact", required=True, ondelete="cascade"
    )
    external_id = fields.Char(
        "External ID", help="The user ID from the external sale channel", required=True
    )

    _partner_channel_uniq = models.Constraint(
        "unique(partner_id, sale_channel_id)",
        "partner-channel pairs for sale channel partners are unique",
    )
    _external_id_channel_uniq = models.Constraint(
        "unique(external_id, sale_channel_id)",
        "external_id-channel pairs for sale channel partners are unique",
    )
