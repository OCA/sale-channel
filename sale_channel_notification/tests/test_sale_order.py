# Copyright 2024 Akretion (http://www.akretion.com).
# @author Mathieu DELVA <mathieu.delva@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestSaleOrder(TransactionCase):
    def setUp(self):
        super().setUp()
        partner_id = self.env.ref("base.res_partner_2")
        sale_channel_id = self.env.ref("sale_channel.sale_channel_amazon")
        model_id = self.env["ir.model"].search([("model", "=", "sale.order")])
        template_id = self.env.ref("sale.mail_template_sale_confirmation")
        product_id = self.env.ref("sale.product_product_4e")
        sale_channel_id.write(
            {
                "notification_ids": [
                    (
                        0,
                        0,
                        {
                            "notification_type": "sale_confirmation",
                            "model_id": model_id.id,
                            "template_id": template_id.id,
                        },
                    )
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

    def test_action_confirm(self):
        self.order_id.action_confirm()
        mail_id = self.env["mail.mail"].search(
            [("model", "=", "sale.order"), ("res_id", "=", self.order_id.id)]
        )
        self.assertTrue(mail_id)
