# Copyright 2023 Akretion (https://www.akretion.com).
# @author Raphaël Reverdy<raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ProductCategory(models.Model):
    _inherit = [
        "product.category",
        "sale.channel.indexable.record",
    ]
    _name = "product.category"

    def _me_and_all_the_children(self):
        return self.search([["parent_path", "like", f"{self.parent_path}%"]])

    def _on_sale_channel_modified(self):
        # triggered only on root category
        self._synchronize_channel_index_category()

    def _synchronize_channel_index_category(self):
        # specific implementation on categories
        # only one category is linked to channel
        # but we synchronize the category's sub tree
        if "active" in self._fields:
            records = self.filtered("active")
        else:
            records = self

        # per channel
        channels = records.mapped("channel_ids")
        lkchannel = {channel: records.browse(0) for channel in channels}
        for record in records:
            categories = record._me_and_all_the_children()
            for channel in record.channel_ids:
                lkchannel[channel] |= categories

        for channel, records in lkchannel.items():
            indexes = channel.search_engine_id.index_ids.filtered(
                lambda s: s.model_id.model == self._name
            )
            if indexes:
                records._add_to_index(indexes)

        # unlink is managed directly ?
