# Copyright 2023 Akretion (https://www.akretion.com).
# @author Raphaël Reverdy<raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleChannel(models.Model):
    _inherit = "sale.channel"

    def _synchronize_channel_index(self):
        super()._synchronize_channel_index()
        self.root_category_id._synchronize_channel_index_category()
        return
