#  Copyright (c) Akretion 2020
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    si_amount_untaxed = fields.Float("(technical) Untaxed amount from import")
    si_amount_tax = fields.Float("(technical) Tax amount from import")
    si_amount_total = fields.Float("(technical) Total amount from import")
    si_force_invoice_date = fields.Date("(technical) Forced invoice date")
    si_force_invoice_number = fields.Char("(technical) Forced invoice number")
