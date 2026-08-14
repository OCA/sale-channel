#  Copyright (c) Akretion 2020
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

from odoo import Command

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


class TestSaleChannel(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # AccountTestInvoicingCommon runs as a restricted accounting user; grant
        # sales rights so it can manage sale channels and confirm sale orders.
        cls.env.user.group_ids |= cls.env.ref("sales_team.group_sale_manager")
        cls.sale_channel = cls.env["sale.channel"].create({"name": "Amazon"})
        cls.product = cls.product_a
        cls.product.invoice_policy = "order"
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner_a.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": cls.product.id,
                            "product_uom_qty": 1,
                        }
                    )
                ],
            }
        )

    def test_sale_channel(self):
        self.sale_order.sale_channel_id = self.sale_channel
        self.sale_order.action_confirm()
        self.sale_order._create_invoices()
        self.assertEqual(self.sale_order.invoice_ids.sale_channel_id, self.sale_channel)
