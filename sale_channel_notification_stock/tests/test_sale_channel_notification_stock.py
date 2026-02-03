# Copyright 2026 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.sale_channel_notification.tests.common import Common


class TestSaleChannelNotificationStock(Common):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.template_picking = cls.env.ref(
            "stock.mail_template_data_delivery_confirmation"
        )
        cls.sale_channel_1.notification_ids |= cls.env[
            "sale.channel.notification"
        ].create(
            {
                "notification_type": "outgoing_picking_shipped",
                "template_id": cls.template_picking.id,
            }
        )
        cls.default_capture_domain = [
            ("model", "=", "stock.picking"),
        ]
        cls.order_id.company_id.stock_move_email_validation = True

    def test_action_outgoing_picking_shipped_send(self):
        self.order_id.action_confirm()
        picking_id = self.order_id.picking_ids
        picking_id.action_confirm()
        for move in picking_id.move_ids:
            move.quantity_done = move.product_uom_qty
        with self.capture_mails_messages() as (new_mails, new_messages):
            self.assertEqual(
                picking_id.with_context(skip_immediate=True).button_validate(), True
            )

        self.assertEqual(len(new_mails.records), 1)
        self.assertEqual(len(new_messages.records), 1)

    def test_action_outgoing_picking_shipped_not_enabled(self):
        self.sale_channel_1.custom_notifications = False
        self.order_id.action_confirm()
        picking_id = self.order_id.picking_ids
        picking_id.action_confirm()
        for move in picking_id.move_ids:
            move.quantity_done = move.product_uom_qty
        with self.capture_mails_messages() as (new_mails, new_messages):
            self.assertEqual(
                picking_id.with_context(skip_immediate=True).button_validate(), True
            )

        self.assertEqual(len(new_mails.records), 0)
        # Normal notification is sent
        self.assertEqual(len(new_messages.records), 1)

    def test_action_outgoing_picking_shipped_no_notifications(self):
        self.sale_channel_1.notification_ids = [(5,)]

        self.order_id.action_confirm()
        picking_id = self.order_id.picking_ids
        picking_id.action_confirm()
        for move in picking_id.move_ids:
            move.quantity_done = move.product_uom_qty
        with self.capture_mails_messages() as (new_mails, new_messages):
            self.assertEqual(
                picking_id.with_context(skip_immediate=True).button_validate(), True
            )

        self.assertEqual(len(new_mails.records), 0)
        self.assertEqual(len(new_messages.records), 0)
