# Copyright 2026 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    channel_carrier_code = fields.Char(readonly=True, copy=False)
    channel_shipping_amount = fields.Monetary(readonly=True, copy=False)
