# Copyright 2022 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SEIndexableRecord(models.AbstractModel):
    _inherit = "se.indexable.record"

    def _se_mark_to_update(self, indexes=None):
        """Avoid to update bindings that should be deleted because the records
        are not linked to the sale channel."""
        if "channel_ids" not in self._fields:
            return super()._se_mark_to_update(indexes)
        for channel in self.mapped("channel_ids"):
            indexes_to_update = channel.mapped("search_engine_id.index_ids")
            if indexes:
                indexes_to_update = indexes_to_update & indexes
            if indexes_to_update:
                records_to_update = self.filtered(
                    lambda rec: channel in rec.channel_ids
                )
                super(SEIndexableRecord, records_to_update)._se_mark_to_update(
                    indexes_to_update
                )
        return None

    def _synchronize_channel_index(self):
        """For a given record depending of the channels linked, the index binding
        will be created or deleted."""
        if "channel_ids" not in self._fields:
            return
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
