# Copyright 2023 Akretion (https://www.akretion.com).
# @author Raphaël Reverdy<raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ProductProduct(models.Model):
    _inherit = [
        "product.product",
        "se.indexable.record",
    ]
    _name = "product.product"
