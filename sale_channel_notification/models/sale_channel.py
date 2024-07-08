# Copyright 2024 Akretion (https://www.akretion.com).
# @author Mathieu Delva <mathieu.delva@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleChannel(models.Model):
    _inherit = "sale.channel"

    notification_ids = fields.One2many(
        "sale.channel.notification",
        "sale_channel_id",
        "Notification",
        help="Send mail for predefined events",
    )

    def _send_notification(self, notification, record):
        self.ensure_one()
        record.ensure_one()
        notifs = self.env["sale.channel.notification"].search(
            [
                ("sale_channel_id", "=", self.id),
                ("notification_type", "=", notification),
            ]
        )
        for notif in notifs:
            notif.send(record.id)
        return True
