# Copyright 2024 Akretion (http://www.akretion.com).
# @author Mathieu DELVA <mathieu.delva@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .common import Common


class TestSaleChannelNotification(Common):
    def test_selection_notification_type(self):
        notification_type_ids = self.env[
            "sale.channel.notification"
        ]._selection_notification_type()
        self.assertEqual(len(notification_type_ids), 1)
        self.assertEqual(notification_type_ids[0][0], "sale_confirmation")

    def test_get_all_notification(self):
        notifications = self.env["sale.channel.notification"]._get_all_notification()
        self.assertEqual(
            notifications,
            {
                "sale_confirmation": {
                    "name": "Sale Confirmation",
                    "model": "sale.order",
                },
            },
        )

    def test_model(self):
        notif = self.sale_channel_1.notification_ids
        self.assertEqual(notif.model_id.model, "sale.order")
