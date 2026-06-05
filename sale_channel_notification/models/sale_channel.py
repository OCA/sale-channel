# Copyright 2026 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Mathieu Delva <mathieu.delva@akretion.com>
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleChannel(models.Model):
    _inherit = "sale.channel"

    custom_notifications = fields.Boolean(
        help="Enable custom notifications for this channel",
    )

    notification_ids = fields.One2many(
        "sale.channel.notification",
        "sale_channel_id",
        "Notification",
        help="Send mail for predefined events",
    )

    def _send_notification(self, notification, record):
        notif = self.env["sale.channel.notification"].search(
            [
                ("sale_channel_id", "=", self.id),
                ("notification_type", "=", notification),
            ],
            limit=1,
        )
        if not notif:
            return False
        notif.send(record)
        return True
