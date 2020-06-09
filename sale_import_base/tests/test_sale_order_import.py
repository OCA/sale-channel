#  Copyright (c) Akretion 2020
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import json

from odoo.exceptions import ValidationError

from .common_sale_order_import import SaleImportCase


class TestSaleOrderImport(SaleImportCase):
    def setUp(self):
        super().setUp()
        self.sale_channel_ebay = self.env.ref("sale_channel.sale_channel_ebay")

    def test_invalid_json(self):
        """ An invalid input will stop the job """
        data = self.sale_data
        del data["address_customer"]["street"]
        with self.assertRaises(ValidationError):
            self.importer_component.run(json.dumps(data))

    def test_create_partner(self):
        """ Base scenario: create partner """
        data = self.sale_data
        partner_count = (
            self.env["res.partner"].with_context(active_test=False).search_count([])
        )
        self.importer_component.run(json.dumps(data))
        partner_count_after_import = (
            self.env["res.partner"].with_context(active_test=False).search_count([])
        )
        self.assertEqual(partner_count_after_import, partner_count + 3)

    def test_binding_created(self):
        """ When we create a partner, a binding is created """
        data = self.sale_data
        new_sale_order = self.importer_component.run(json.dumps(data))
        binding_count = self.env["sale.channel.partner"].search_count(
            [
                ("sale_channel_id", "=", self.sale_channel_ebay.id),
                ("partner_id", "=", new_sale_order.partner_id.id),
                ("external_id", "=", "ThomasJeanEbay"),
            ]
        )
        self.assertEqual(binding_count, 1)

    def test_import_existing_partner_match_external_id(self):
        """ During import, if a partner is matched on external_id/channel
        combination, his address is updated """
        data = self.sale_data
        partner = self.env.ref("base.res_partner_1")
        self.env["sale.channel.partner"].create(
            {
                "partner_id": partner.id,
                "external_id": "ThomasJeanEbay",
                "sale_channel_id": self.sale_channel_ebay.id,
            }
        )
        self.importer_component.run(json.dumps(data))
        self.assertEqual(partner.street, "1 rue de Jean")

    def test_import_existing_partner_match_email(self):
        """ During import, if a partner is matched on email,
        its address is updated """
        data = self.sale_data
        partner = self.env.ref("base.res_partner_3")
        partner.write({"email": "thomasjean@example.com"})
        data["address_customer"]["street"] = "new street"
        self.importer_component.run(json.dumps(data))
        self.assertEqual(partner.street, "new street")

    def test_import_existing_partner_match_email_disallowed(self):
        """ Test that if email match is disallowed, we just create a partner """
        partner_count = (
            self.env["res.partner"].with_context(active_test=False).search_count([])
        )
        data = self.sale_data
        partner = self.env.ref("base.res_partner_1")
        partner.write({"email": "thomasjean@example.com"})
        data["address_customer"]["street"] = "new street"
        self.sale_channel_ebay.allow_match_on_email = False
        self.importer_component.run(json.dumps(data))
        new_partner_count = (
            self.env["res.partner"].with_context(active_test=False).search_count([])
        )
        self.assertEqual(new_partner_count, partner_count + 3)

    def test_product_missing(self):
        """ Test product code validation effectively blocks the job """
        data = self.sale_data
        for line in data["lines"]:
            line["product_code"] = "doesn't exist"
        with self.assertRaises(ValidationError):
            self.importer_component.run(json.dumps(data))

    def test_product_search(self):
        """ Check we get the right product match on product code"""
        data = self.sale_data
        new_sale_order = self.importer_component.run(json.dumps(data))
        self.assertEqual(new_sale_order.order_line[0].product_id, self.product_order)
        self.assertEqual(new_sale_order.order_line[1].product_id, self.product_deliver)

    def test_wrong_total_amount(self):
        """ Test the sale.exception works as intended """
        data = self.sale_data
        data["amount"]["amount_total"] += 500.0
        new_sale_order = self.importer_component.run(json.dumps(data))
        exception_wrong_total_amount = self.env.ref(
            "sale_import_base.exc_wrong_total_amount"
        )
        self.assertEqual(
            new_sale_order.detect_exceptions(), [exception_wrong_total_amount.id]
        )

    def test_wrong_total_amount_untaxed(self):
        """ Test the sale.exception works as intended """
        data = self.sale_data
        data["amount"]["amount_untaxed"] += 500.0
        new_sale_order = self.importer_component.run(json.dumps(data))
        exception_wrong_untaxed_amount = self.env.ref(
            "sale_import_base.exc_wrong_untaxed_amount"
        )
        self.assertEqual(
            new_sale_order.detect_exceptions(), [exception_wrong_untaxed_amount.id]
        )

    def test_correct_amounts(self):
        """ Test the sale.exception works as intended """
        data = self.sale_data
        new_sale_order = self.importer_component.run(json.dumps(data))
        self.assertFalse(new_sale_order.detect_exceptions())

    def test_deliver_country_with_tax(self):
        """ Test fiscal position is applied correctly """
        data = self.sale_data
        data["address_shipping"]["country_code"] = "CH"
        new_sale_order = self.importer_component.run(json.dumps(data))
        self.assertEqual(new_sale_order.fiscal_position_id, self.fpos_swiss)
        self.assertEqual(new_sale_order.order_line[0].tax_id, self.tax_swiss)

    def test_order_line_description(self):
        """ Test that a description is taken into account, or
        default description is generated if none is provided """
        data = self.sale_data
        new_sale_order = self.importer_component.run(json.dumps(data))
        expected_desc = "Initial Line 1 import description"
        self.assertEqual(new_sale_order.order_line[0].name, expected_desc)
        expected_desc_2 = "[PROD_DEL] Switch, 24 ports"
        self.assertEqual(new_sale_order.order_line[1].name, expected_desc_2)

    def test_currency_code(self):
        data = self.sale_data
        errors = self.env.datamodels["sale.order"].validate(data)
        self.assertFalse(errors)
        data["currency_code"] = "EUR"
        errors = self.env.datamodels["sale.order"].validate(data)
        self.assertTrue(errors)

    def test_payment_create(self):
        data = self.sale_data
        new_sale_order = self.importer_component.run(json.dumps(data))
        new_payment = new_sale_order.transaction_ids
        self.assertEqual(new_payment.reference, "PMT-EXAMPLE-001")
