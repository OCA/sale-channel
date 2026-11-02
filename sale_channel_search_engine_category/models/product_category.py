# Copyright 2022 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import models


class ProductCategory(models.Model):
    _inherit = [
        "product.category",
        "se.indexable.record",
    ]
    _name = "product.category"

    def _on_sale_channel_modified(self):
        self._synchronize_channel_index()

    def _add_to_index(self, indexes):
        bindings = self.env["se.binding"]
        for index in indexes:
            channel = self.env["sale.channel"].search(
                [("search_engine_id", "=", index.backend_id.id)], limit=1
            )
            records = self
            if channel and not channel.should_publish_root:
                # don't publish root categ
                records = self.filtered("parent_id")
            if records:
                bindings |= super(ProductCategory, records)._add_to_index(index)
        return bindings
