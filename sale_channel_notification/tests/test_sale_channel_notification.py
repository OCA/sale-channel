# Copyright 2024 Akretion (http://www.akretion.com).
# @author Mathieu DELVA <mathieu.delva@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.tools.translate import _

from .common import Common


class TestSaleChannelNotification(Common):
    def test_onchange_notification_type(self):
        notification_type_ids = self.env[
            "sale.channel.notification"
        ]._selection_notification_type()
        model_id = self.env["ir.model"].search([("model", "=", "sale.order")])
        template_id = self.env.ref("sale.mail_template_sale_confirmation")
        sale_channel_notification_id = self.env["sale.channel.notification"].create(
            {
                "notification_type": notification_type_ids[0][0],
                "model_id": model_id.id,
                "template_id": template_id.id,
            }
        )
        sale_channel_notification_id.notification_type = notification_type_ids[1][0]
        sale_channel_notification_id.on_notification_type_change()
        self.assertEqual(sale_channel_notification_id.model_id.name, "Transfer")

    def test_selection_notification_type(self):
        notification_type_ids = self.env[
            "sale.channel.notification"
        ]._selection_notification_type()
        self.assertEqual(len(notification_type_ids), 2)
        self.assertEqual(notification_type_ids[0][0], "sale_confirmation")

    def test_get_all_notification(self):
        notifications = self.env["sale.channel.notification"]._get_all_notification()
        self.assertEqual(
            notifications,
            {
                "sale_confirmation": {
                    "name": _("Sale Confirmation"),
                    "model": "sale.order",
                },
                "picking_shipped": {
                    "name": _("Picking Shipped"),
                    "model": "stock.picking",
                },
            },
        )
