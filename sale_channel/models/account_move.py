#  Copyright (c) Akretion 2020
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

from odoo import models


class AccountMove(models.Model):
    _name = "account.move"
    _inherit = [_name, "sale.channel.owner"]
