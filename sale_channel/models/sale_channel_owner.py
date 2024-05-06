# Copyright 2022 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleChannelOwner(models.AbstractModel):
    _name = "sale.channel.owner"
    _description = "Mixin to attach record on several channel"

    channel_ids = fields.Many2many(
        "sale.channel",
        string="Sale Channel",
    )

    def write(self, vals):
        res = super().write(vals)
        if "channel_ids" in vals or "active" in vals:
            self._on_sale_channel_modified()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records.filtered("channel_ids")._on_sale_channel_modified()
        return records

    def _on_sale_channel_modified(self):
        """Hook for customisation when sale channel change"""
