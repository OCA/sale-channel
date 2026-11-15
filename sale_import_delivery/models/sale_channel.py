# Copyright 2026 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleChannel(models.Model):
    _inherit = "sale.channel"

    sale_import_carrier_id = fields.Many2one(
        "delivery.carrier",
        "Default carrier",
        help="Carrier of the imported orders when no carrier matches the code "
        "sent by the channel. Without a carrier the shipping amount is only "
        "kept on the order.",
    )
