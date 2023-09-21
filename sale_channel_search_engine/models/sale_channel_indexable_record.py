# Copyright 2022 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleChannelIndexableRecord(models.AbstractModel):
    _name = "sale.channel.indexable.record"
    _inherit = "se.indexable.record"
    _description = "Sale Channel Indexable Record"

    def _synchronize_channel_index(self):
        """For a given record depending of the channels linked, the index binding
        will be created or deleted."""
        self = self.sudo()
        existing_bindings = self._get_bindings()
        bindings = self.env["se.binding"]
        if "active" in self._fields:
            records = self.filtered("active")
        else:
            records = self
        # Be carefull when using this mixin your model required to have
        # the field "channel_ids" defined
        # in most of case just inherit of sale.channel.owner
        for channel in records.channel_ids:
            items = records.filtered(lambda s: channel in s.channel_ids)
            indexes = channel.search_engine_id.index_ids.filtered(
                lambda s: s.model_id.model == self._name
            )
            bindings |= items._add_to_index(indexes)
        (existing_bindings - bindings).write({"state": "to_delete"})
