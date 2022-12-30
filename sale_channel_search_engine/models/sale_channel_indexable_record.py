# Copyright 2022 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleChannelIndexableRecord(models.AbstractModel):
    _name = "sale.channel.indexable.record"
    _inherit = "se.indexable.record"
    _description = "Sale Channel Indexable Record"

    def _synchronize_channel_index(self):
        bindings = self.env["se.binding"]
        for channel in self.channel_ids:
            index = channel.search_engine_id.index_ids.filtered(
                lambda s: s.model_id.model == self._name
            )
            if index:
                bindings |= self._add_to_index(index)
        (self.index_bind_ids - bindings).write({"state": "to_delete"})
