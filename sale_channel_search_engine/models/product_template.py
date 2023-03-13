# Copyright 2022 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ProductTemplate(models.Model):
    _inherit = ["product.template", "sale.channel.owner"]
    _name = "product.template"

    def _on_sale_channel_modified(self):
        self.product_variant_ids._synchronize_channel_index()
