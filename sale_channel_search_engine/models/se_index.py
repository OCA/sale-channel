# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class SeIndex(models.Model):
    _inherit = "se.index"

    def _add_bindings_from_sale_channel(self):
        for index in self:
            index_model = index.model_id.model
            if "channel_ids" not in self.env[index_model]._fields:
                continue
            sale_channel = self.env["sale.channel"].search(
                [("search_engine_id", "=", index.backend_id.id)]
            )
            if not sale_channel:
                continue
            records = self.env[index_model].search(
                [("channel_ids", "in", sale_channel.id)]
            )
            records._add_to_index(index)

    @api.model_create_multi
    def create(self, vals_list):
        indexes = super().create(vals_list)
        indexes.sudo()._add_bindings_from_sale_channel()
        return indexes
