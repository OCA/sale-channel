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
        cls.template_picking.subject = "Your order has been shipped"
        cls.template_picking_ready = cls.template_picking.copy(
            {
                "name": "Outgoing picking ready",
            }
        )
        cls.template_picking_ready.subject = "Your order is ready to be shipped"
        cls.sale_channel_1.notification_ids |= cls.env[
            "sale.channel.notification"
        ].create(
            {
                "notification_type": "outgoing_picking_shipped",
                "template_id": cls.template_picking.id,
            }
        ) | cls.env[
            "sale.channel.notification"
        ].create(
            {
                "notification_type": "outgoing_picking_ready",
                "template_id": cls.template_picking_ready.id,
            }
        )
        cls.default_capture_domain = [
            ("model", "=", "stock.picking"),
        ]
        cls.order_id.company_id.stock_move_email_validation = True

    def test_action_outgoing_picking_ready_send_stock(self):
        with self.capture_mails_messages() as (new_mails, new_messages):
            self.order_id.action_confirm()
        self.assertEqual(len(new_mails.records), 1)
        self.assertEqual(len(new_messages.records), 2)
        self.assertEqual(new_mails.records.subject, "Your order is ready to be shipped")

        with self.capture_mails_messages() as (new_mails, new_messages):
            picking_id = self.order_id.picking_ids
            picking_id.action_confirm()
            for move in picking_id.move_ids:
                move.quantity_done = move.product_uom_qty

            self.assertEqual(picking_id.action_assign(), True)
            picking_id.flush_recordset()

        self.assertEqual(len(new_mails.records), 0)
        self.assertEqual(len(new_messages.records), 0)

    def test_action_outgoing_picking_ready_send_no_stock(self):
        product = self.order_id.order_line.product_id
        # Empty stock
        reserving_all_order = self.order_id.copy()
        reserving_all_order.order_line.product_uom_qty = product.qty_available
        reserving_all_order.action_confirm()

        with self.capture_mails_messages() as (new_mails, new_messages):
            self.order_id.action_confirm()
            picking_id = self.order_id.picking_ids
            picking_id.action_confirm()

        self.assertEqual(len(new_mails.records), 0)
        self.assertEqual(len(new_messages.records), 1)

        # Replenish stock
        self.env["stock.quant"].create(
            {
                "product_id": product.id,
                "product_uom_id": self.order_id.order_line.product_uom.id,
                "location_id": self.env.ref("stock.stock_location_stock").id,
                "quantity": 50,
            }
        )

        with self.capture_mails_messages() as (new_mails, new_messages):
            for move in picking_id.move_ids:
                move.quantity_done = move.product_uom_qty

            self.assertEqual(picking_id.action_assign(), True)
            picking_id.flush_recordset()

        self.assertEqual(len(new_mails.records), 1)
        self.assertEqual(len(new_messages.records), 1)
        self.assertEqual(new_mails.records.subject, "Your order is ready to be shipped")

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
            picking_id.flush_recordset()

        self.assertEqual(len(new_mails.records), 1)
        self.assertEqual(len(new_messages.records), 1)
        self.assertEqual(new_mails.records.subject, "Your order has been shipped")

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
            picking_id.flush_recordset()

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
            picking_id.flush_recordset()

        self.assertEqual(len(new_mails.records), 0)
        self.assertEqual(len(new_messages.records), 0)
