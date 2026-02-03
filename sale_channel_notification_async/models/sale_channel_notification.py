# Copyright 2026 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, fields, models


class SaleChannelNotification(models.Model):
    _inherit = "sale.channel.notification"

    use_async = fields.Boolean(default=False)

    def send(self, record):
        if self.use_async:
            self.with_delay(
                description=_(
                    "Sale Channel {name} {type} Notification for {record}"
                ).format(
                    name=self.sale_channel_id.name,
                    type=self.notification_type,
                    record=record.name,
                )
            )._send(record, **self._get_template_context())
        else:
            return super().send(record)
