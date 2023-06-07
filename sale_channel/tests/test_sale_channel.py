#  Copyright (c) Akretion 2020
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

from odoo.tests.common import TransactionCase


class TestSaleChannel(TransactionCase):
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
        # Force to recompute qty_to_invoice as we have change the product
        # invoice policy
        self.sale_order.order_line._compute_qty_to_invoice()
        self.sale_order._create_invoices()
        self.assertEqual(self.sale_order.invoice_ids.sale_channel_id, self.sale_channel)
