# Copyright 2022 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ProductProduct(models.Model):
    _inherit = [
        "product.product",
        "sale.channel.indexable.record",
    ]
    _name = "product.product"

    def write(self, vals):
        res = super().write(vals)
        if "active" in vals:
            self._synchronize_channel_index()
        return res
