# Copyright 2026 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    sale_import_code = fields.Char(
        "Import code",
        index=True,
        help="Code sent by the sale channels for this carrier.",
    )
    sale_import_charge_freight = fields.Boolean(
        "Freight charged by the seller",
        default=True,
        help="The seller delivers the imported orders of this carrier and "
        "charges the customer for it: the shipping amount sent by the channel "
        "is added to the order. Uncheck it when the sale channel delivers and "
        "keeps the shipping amount.",
    )
