# Copyright 2024 Akretion (http://www.akretion.com).
# @author Mathieu DELVA <mathieu.delva@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestSaleOrder(TransactionCase):
    def setUp(self):
        super().setUp()
        partner_id = self.env.ref("base.res_partner_2")
        sale_channel_id = self.env.ref("sale_channel.sale_channel_amazon")
        sale_model_id = self.env["ir.model"].search([("model", "=", "sale.order")])
        picking_model_id = self.env["ir.model"].search(
            [("model", "=", "stock.picking")]
        )
        sale_template_id = self.env.ref("sale.mail_template_sale_confirmation")
        picking_template_id = self.env.ref(
            "stock.mail_template_data_delivery_confirmation"
        )
        product_id = self.env.ref("sale.product_product_4e")
        sale_channel_id.write(
            {
                "notification_ids": [
                    (
                        0,
                        0,
                        {
                            "notification_type": "sale_confirmation",
                            "model_id": sale_model_id.id,
                            "template_id": sale_template_id.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "notification_type": "picking_shipped",
                            "model_id": picking_model_id.id,
                            "template_id": picking_template_id.id,
                        },
                    ),
                ]
            }
        )

        self.order_id = self.env["sale.order"].create(
            {
                "partner_id": partner_id.id,
                "sale_channel_id": sale_channel_id.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product_id.id,
                            "product_uom_qty": 1,
                        },
                    )
                ],
            }
        )

    def test_onchange_carrier_id(self):
        carrier_id = self.env.ref("delivery.free_delivery_carrier")
        self.order_id.action_confirm()
        picking_id = self.order_id.picking_ids
        picking_id.carrier_id = carrier_id
        picking_id.onchange_carrier_id()

        mail_id = self.env["mail.mail"].search(
            [("model", "=", "stock.picking"), ("res_id", "=", picking_id.id)]
        )

        self.assertTrue(mail_id)
