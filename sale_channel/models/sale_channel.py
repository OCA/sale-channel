#  Copyright (c) Akretion 2020
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

from odoo import fields, models


class SaleChannel(models.Model):
    _name = "sale.channel"
    _description = "Sale Channel"

    name = fields.Char("Name", required=True)
    active = fields.Boolean(default=True)
    partner_id = fields.Many2one("res.partner")
