# Copyright 2026 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, models


class SaleChannelNotification(models.Model):
    _inherit = "sale.channel.notification"

    def _get_all_notification(self):
        return {
            **super()._get_all_notification(),
            "outgoing_picking_shipped": {
                "name": _("Outgoing picking shipped"),
                "model": "stock.picking",
            },
        }
