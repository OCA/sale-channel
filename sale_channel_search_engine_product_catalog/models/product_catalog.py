# Copyright 2023 Akretion (https://www.akretion.com).
# @author Raphaël Reverdy<raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ProductCatalog(models.Model):
    _inherit = [
        "product.catalog",
        "sale.channel.indexable.record",
    ]
    _name = "product.catalog"
    # _inherit = "product.catalog"

    def _on_sale_channel_modified(self):
        # ie added on a sale channel
        self._synchronize_channel_index_catalog()

    def _synchronize_channel_index_catalog(self):
        # specific implementation on catalog
        # only one catalog is linked to channel
        # but we synchronize all the products
        if "active" in self._fields:
            records = self.filtered("active")
        else:
            records = self

        # per channel
        channels = records.mapped("channel_ids")
        lkchannel = {
            channel: self.env["product.product"].browse(0) for channel in channels
        }
        for record in records:
            products = record.pp_effective_member_ids
            for channel in record.channel_ids:
                lkchannel[channel] |= products

        for channel, records in lkchannel.items():
            indexes = channel.search_engine_id.index_ids.filtered(
                lambda s: s.model_id.model == records._name
            )
            if indexes:
                records._add_to_index(indexes)

        # unlink is managed directly ?
