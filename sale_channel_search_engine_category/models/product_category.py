# Copyright 2022 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import models


class ProductCategory(models.Model):
    _inherit = [
        "product.category",
        "sale.channel.indexable.record",
    ]
    _name = "product.category"

    def _on_sale_channel_modified(self):
        self._synchronize_channel_index()
