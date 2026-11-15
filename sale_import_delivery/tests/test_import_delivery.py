# Copyright 2026 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
from datetime import datetime
from unittest.mock import patch

from odoo.tests import TransactionCase, tagged

from odoo.addons.extendable.tests.common import ExtendableMixin

ADDRESS = {
    "name": "Thomas Jean",
    "street": "1 rue de Jean",
    "zip": "69100",
    "city": "Lyon",
    "country_code": "FR",
}


@tagged("post_install", "-at_install")
class TestImportDelivery(TransactionCase, ExtendableMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context, tracking_disable=True, queue_job__no_delay=True
            )
        )
        cls.init_extendable_registry()
        cls.addClassCleanup(cls.reset_extendable_registry)
        cls.channel = cls.env["sale.channel"].create(
            {"name": "Delivery import", "pricelist_id": cls.env.ref("product.list0").id}
        )
        cls.env["product.product"].create(
            {"name": "Item", "default_code": "DLV-ITEM", "list_price": 10}
        )
        cls.shipping_product = cls.env["product.product"].create(
            {"name": "Shipping", "type": "service", "default_code": "SHIP"}
        )
        cls.carrier = cls.env["delivery.carrier"].create(
            {
                "name": "Own delivery",
                "product_id": cls.shipping_product.id,
                "sale_import_code": "own",
            }
        )

    def import_order(self, name, shipping):
        data = {
            "name": name,
            "address_customer": dict(ADDRESS, external_id="buyer"),
            "address_shipping": dict(ADDRESS),
            "address_invoicing": dict(ADDRESS),
            "lines": [{"product_code": "DLV-ITEM", "qty": 1, "price_unit": 10.0}],
            "shipping": shipping,
        }
        payload = self.env["sale.import.payload"].create(
            {"sale_channel_id": self.channel.id, "data_str": json.dumps(data)}
        )
        self.assertEqual(payload.state, "done", payload.state_info)
        return self.env["sale.order"].search([("client_order_ref", "=", name)])

    def test_carrier_by_code_adds_shipping_line(self):
        order = self.import_order(
            "DLV-1",
            {
                "carrier_code": "own",
                "amount": 20.0,
                "promised_date": "2026-09-25T12:00:00Z",
            },
        )
        self.assertEqual(order.carrier_id, self.carrier)
        line = order.order_line.filtered("is_delivery")
        self.assertEqual(line.price_unit, 20.0)
        self.assertEqual(order.channel_carrier_code, "own")
        self.assertEqual(order.channel_shipping_amount, 20.0)
        self.assertEqual(order.commitment_date, datetime(2026, 9, 25, 12, 0))

    def test_carrier_without_amount_sets_carrier_only(self):
        order = self.import_order("DLV-2", {"carrier_code": "own"})
        self.assertEqual(order.carrier_id, self.carrier)
        self.assertFalse(order.order_line.filtered("is_delivery"))

    def test_unknown_code_uses_channel_default(self):
        self.channel.sale_import_carrier_id = self.carrier
        order = self.import_order("DLV-3", {"carrier_code": "other", "amount": 12})
        self.assertEqual(order.carrier_id, self.carrier)
        self.assertEqual(order.order_line.filtered("is_delivery").price_unit, 12.0)

    def test_platform_code_skips_channel_default(self):
        self.channel.sale_import_carrier_id = self.carrier
        with patch.object(
            type(self.env["sale.channel.importer"]),
            "_platform_carrier_codes",
            return_value=("platform",),
        ):
            order = self.import_order(
                "DLV-4", {"carrier_code": "platform", "amount": 8}
            )
        self.assertFalse(order.carrier_id)
        self.assertFalse(order.order_line.filtered("is_delivery"))
        self.assertEqual(order.channel_shipping_amount, 8.0)

    def test_carrier_not_charged_by_the_seller(self):
        fulfillment = self.env["delivery.carrier"].create(
            {
                "name": "Channel fulfillment",
                "product_id": self.shipping_product.id,
                "sale_import_code": "fulfillment",
                "sale_import_charge_freight": False,
            }
        )
        order = self.import_order(
            "DLV-5", {"carrier_code": "fulfillment", "amount": 15.0}
        )
        self.assertEqual(order.carrier_id, fulfillment)
        self.assertFalse(order.order_line.filtered("is_delivery"))
        self.assertEqual(order.channel_shipping_amount, 15.0)

    def test_no_carrier_keeps_amount_only(self):
        order = self.import_order("DLV-6", {"carrier_code": "other", "amount": 15.0})
        self.assertFalse(order.carrier_id)
        self.assertFalse(order.order_line.filtered("is_delivery"))
        self.assertEqual(order.channel_shipping_amount, 15.0)
