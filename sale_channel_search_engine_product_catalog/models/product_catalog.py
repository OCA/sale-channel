# Copyright 2023 Akretion (https://www.akretion.com).
# @author Raphaël Reverdy<raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ProductCatalog(models.Model):
    _inherit = "product.catalog"

    def _on_sale_channel_modified(self):
        # ie added on a sale channel
        self._synchronize_channel_index_catalog()

    def _synchronize_channel_index_catalog(self):
        # specific implementation on catalog
        # only one catalog is linked to a channel
        # a catalog can be linked to multiple channels
        # we synchronize all the effective members of the catalog
        # = we synchronize products not catalog
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

        bindings_to_rm = self.env["se.binding"].browse(0)
        bindings_to_update = self.env["se.binding"].browse(0)
        for channel, records in lkchannel.items():
            # remove from all indexes
            bindings_to_rm |= self.env["se.binding"].search(
                [
                    ["channel_id", "=", channel.id],
                    ["res_model", "=", "product.product"],
                    ["res_id", "not in", records.ids],
                    ["state", "!=", "to_delete"],
                ]
            )

            bindings_to_update |= self.env["se.binding"].search(
                [
                    ["channel_id", "=", channel.id],
                    ["res_model", "=", "product.product"],
                    ["res_id", "in", records.ids],
                ]
            )

            indexes = channel.search_engine_id.index_ids.filtered(
                lambda s: s.model_id.model == records._name
            )
            for index in indexes:
                # add_to_index mark existing bindings as "to update"
                records._add_to_index(index)
        bindings_to_rm.write({"state": "to_delete"})
        bindings_to_update.write({"state": "to_recompute"})

    def open_se_binding(self):
        # TODO: exclude bindings from other
        # channels / indexes
        return self.with_context(
            active_test=False
        ).pp_effective_member_ids.open_se_binding()

    def synchronize_channel_index_action(self):
        self._synchronize_channel_index_catalog()
        return self.open_se_binding()
