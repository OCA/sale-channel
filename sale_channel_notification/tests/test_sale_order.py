# Copyright 2026 Akretion (http://www.akretion.com).
# @author Mathieu Delva <mathieu.delva@akretion.com>
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import Common


class TestSaleOrder(Common):
    def test_action_confirm_not_enabled(self):
        self.sale_channel_1.custom_notifications = False

        with self.capture_mails_messages() as (new_mails, new_messages):
            self.order_id.action_confirm()
        self.assertEqual(len(new_mails.records), 0)
        self.assertEqual(len(new_messages.records), 0)
        # Regular notification is still working
        with self.capture_mails_messages() as (_, new_messages):
            self.order_id._send_order_confirmation_mail()
        self.assertEqual(len(new_messages.records), 1)

    def test_action_confirm_notification(self):
        with self.capture_mails_messages() as (new_mails, new_messages):
            self.order_id.action_confirm()
        self.assertEqual(len(new_mails.records), 1)
        self.assertEqual(len(new_messages.records), 1)
        # Regular notification is not sent
        with self.capture_mails_messages() as (_, new_messages):
            self.order_id._send_order_confirmation_mail()
        self.assertEqual(len(new_messages.records), 0)

    def test_action_confirm_no_notification(self):
        self.sale_channel_1.notification_ids = [(5,)]

        with self.capture_mails_messages() as (new_mails, new_messages):
            self.order_id.action_confirm()
        self.assertEqual(len(new_mails.records), 0)
        self.assertEqual(len(new_messages.records), 0)
        # Regular notification is not sent
        with self.capture_mails_messages() as (_, new_messages):
            self.order_id._send_order_confirmation_mail()
        self.assertEqual(len(new_messages.records), 0)
