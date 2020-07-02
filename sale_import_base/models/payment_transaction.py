#  Copyright (c) Akretion 2020
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import fields, models


class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    si_transaction_identifier = fields.Integer("Transaction import identifier")
