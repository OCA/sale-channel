# Copyright 2024 Akretion (https://www.akretion.com).
# @author Mathieu Delva <mathieu.delva@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.onchange("carrier_id", "sale_id.sale_channel_id")
    def onchange_carrier_id(self):
        if self.carrier_id and self.sale_id.sale_channel_id:
            self.sale_id.sale_channel_id._send_notification("picking_shipped", self)
