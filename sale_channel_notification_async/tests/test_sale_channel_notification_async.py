# Copyright 2026 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.sale_channel_notification.tests.common import Common


class TestSaleChannelNotificationAsync(Common):
    def test_action_confirm_notification(self):
        with self.capture_mails_messages() as (new_mails, new_messages):
            self.order_id.action_confirm()
        self.assertEqual(len(new_mails.records), 1)
        self.assertEqual(len(new_messages.records), 1)
        # Regular notification is not sent
        with self.capture_mails_messages() as (_, new_messages):
            self.order_id._send_order_confirmation_mail()
        self.assertEqual(len(new_messages.records), 0)

    def test_sale_channel_notification_async(self):
        self.sale_channel_1.notification_ids.use_async = True

        with self.capture_mails_messages() as (new_mails, new_messages):
            self.order_id.action_confirm()
        self.assertEqual(len(new_mails.records), 0)
        self.assertEqual(len(new_messages.records), 0)
        # Regular notification is not sent
        with self.capture_mails_messages() as (_, new_messages):
            self.order_id._send_order_confirmation_mail()
        self.assertEqual(len(new_messages.records), 0)

        last_job = self.env["queue.job"].search([], order="id desc", limit=1)
        self.assertEqual(
            last_job.name,
            f"Sale Channel Amazon sale_confirmation Notification for {self.order_id.name}",
        )

    def test_sale_channel_notification_async_sync(self):
        self.sale_channel_1.notification_ids.use_async = True
        with self.capture_mails_messages() as (new_mails, new_messages):
            self.order_id.with_context(queue_job__no_delay=True).action_confirm()
        self.assertEqual(len(new_mails.records), 1)
        self.assertEqual(len(new_messages.records), 1)
