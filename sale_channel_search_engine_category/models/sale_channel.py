# Copyright 2025 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleChannel(models.Model):
    _inherit = "sale.channel"

    def write(self, vals):
        res = super().write(vals)
        if "search_engine_id" in vals:
            categs = self.root_categ_ids
            while categs:
                categs._synchronize_channel_index()
                categs = categs.child_id
        return res
