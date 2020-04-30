#  Copyright (c) Akretion 2020
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

from odoo.addons.sale.tests.test_sale_common import TestCommonSaleNoChart


class TestSaleChannel(TestCommonSaleNoChart):
    def setUp(self):
        super().setUp()
        self.sale_channel = self.env.ref("sale_channel.sale_channel_amazon")
        self.sale_order = self.env.ref("sale.sale_order_4")
        self.partner = self.env.ref("base.res_partner_4")

    def test_sale_channel(self):
        self.sale_order.sale_channel_id = self.sale_channel
        self.sale_order.order_line.mapped("product_id").write(
            {"invoice_policy": "order"}
        )
        self.sale_order.action_invoice_create()
        self.assertEqual(
            self.sale_order.invoice_ids[0].sale_channel_id, self.sale_channel
        )
