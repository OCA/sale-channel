#  Copyright (c) Akretion 2020
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class SaleChannel(models.Model):
    _inherit = "sale.channel"

    allow_match_on_email = fields.Boolean("Allow customer match on email")
    sale_orders_check_amounts_untaxed = fields.Boolean(
        "(technical) Check untaxed amounts against imported values"
    )
    sale_orders_check_amounts_total = fields.Boolean(
        "(technical) Check total amounts against imported values"
    )
    pricelist_id = fields.Many2one("product.pricelist", string="Pricelist")
