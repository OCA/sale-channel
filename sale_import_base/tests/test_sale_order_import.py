# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import json

from odoo.exceptions import ValidationError

from .common_sale_order_import import SaleImportCase


class TestSaleOrderImport(SaleImportCase):
    def setUp(self):
        super().setUp()
        self.sale_channel_ebay = self.env.ref("sale_channel.sale_channel_ebay")

    def test_invalid_json(self):
        """ An invalid input will stop the job """
        json_import = self.sale_data
        del json_import["address_customer"]["street"]
        with self.assertRaises(ValidationError):
            self.importer_component.run(json.dumps(json_import))

    def test_create_partner(self):
        """ Base scenario: create partner """
        json_import = self.sale_data
        partner_count = self.env["res.partner"].search_count([])
        self.importer_component.run(json.dumps(json_import))
        partner_count_after_import = self.env["res.partner"].search_count([])
        self.assertEqual(partner_count_after_import, partner_count + 3)

    def test_binding_created(self):
        """ When we create a partner, a binding is created """
        json_import = self.sale_data
        new_sale_order = self.importer_component.run(json.dumps(json_import))
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
        json_import = self.sale_data
        partner_colleen = self.env.ref("base.res_partner_address_28")
        del json_import["address_customer"]["email"]
        json_import["address_customer"]["street"] = "new street"
        json_import["address_customer"]["external_id"] = "id_from_ebay1"
        self.importer_component.run(json.dumps(json_import))
        self.assertEqual(partner_colleen.street, "new street")

    def test_import_existing_partner_match_email(self):
        """ During import, if a partner is matched on email,
        its address is updated """
        json_import = self.sale_data
        partner_gemini = self.env.ref("base.res_partner_3")
        json_import["address_customer"]["email"] = "gemini.furniture39@example.com"
        json_import["address_customer"]["street"] = "new street"
        self.importer_component.run(json.dumps(json_import))
        self.assertEqual(partner_gemini.street, "new street")

    def test_import_existing_partner_match_email_disallowed(self):
        """ Test that if email match is disallowed, we just create a partner """
        partner_count = self.env["res.partner"].search_count([])
        json_import = self.sale_data
        json_import["address_customer"]["email"] = "gemini.furniture39@example.com"
        json_import["address_customer"]["street"] = "new street"
        self.sale_channel_ebay.allow_match_on_email = False
        self.importer_component.run(json.dumps(json_import))
        new_partner_count = self.env["res.partner"].search_count([])
        self.assertEqual(partner_count + 3, new_partner_count)

    def test_product_missing(self):
        """ Test product code validation effectively blocks the job """
        json_import = self.sale_data
        for line in json_import["lines"]:
            line["product_code"] = "doesn't exist"
        with self.assertRaises(ValidationError):
            self.importer_component.run(json.dumps(json_import))

    def test_product_search(self):
        """ Check we get the right product match on product code"""
        json_import = self.sale_data
        new_sale_order = self.importer_component.run(json.dumps(json_import))
        self.assertEqual(new_sale_order.order_line[0].product_id, self.product_order)
        self.assertEqual(new_sale_order.order_line[1].product_id, self.product_deliver)

    def test_wrong_total_amount(self):
        """ Test the sale.exception works as intended """
        json_import = self.sale_data
        json_import["amount"]["amount_total"] += 500.0
        new_sale_order = self.importer_component.run(json.dumps(json_import))
        exception_wrong_total_amount = self.env.ref(
            "sale_import_base.exc_wrong_total_amount"
        )
        self.assertEqual(
            new_sale_order.detect_exceptions(), [exception_wrong_total_amount.id]
        )

    def test_wrong_total_amount_untaxed(self):
        """ Test the sale.exception works as intended """
        json_import = self.sale_data
        json_import["amount"]["amount_untaxed"] += 500.0
        new_sale_order = self.importer_component.run(json.dumps(json_import))
        exception_wrong_untaxed_amount = self.env.ref(
            "sale_import_base.exc_wrong_untaxed_amount"
        )
        self.assertEqual(
            new_sale_order.detect_exceptions(), [exception_wrong_untaxed_amount.id]
        )

    def test_correct_amounts(self):
        """ Test the sale.exception works as intended """
        json_import = self.sale_data
        new_sale_order = self.importer_component.run(json.dumps(json_import))
        self.assertFalse(new_sale_order.detect_exceptions())

    def test_deliver_country_with_tax(self):
        """ Test fiscal position is applied correctly """
        json_import = self.sale_data
        json_import["address_shipping"]["country_code"] = "CH"
        new_sale_order = self.importer_component.run(json.dumps(json_import))
        self.assertEqual(new_sale_order.fiscal_position_id, self.fpos_swiss)
        self.assertEqual(new_sale_order.order_line[0].tax_id, self.tax_swiss)

    def test_order_line_description(self):
        """ Test that a description is taken into account, or
        default description is generated if none is provided """
        json_import = self.sale_data
        new_sale_order = self.importer_component.run(json.dumps(json_import))
        expected_desc = "Initial Line 1 import description"
        self.assertEqual(new_sale_order.order_line[0].name, expected_desc)
        expected_desc_2 = "[PROD_DEL] Switch, 24 ports"
        self.assertEqual(new_sale_order.order_line[1].name, expected_desc_2)

    def test_currency_code(self):
        json_import = self.sale_data
        errors = self.env.datamodels["sale.order"].validate(json_import)
        self.assertFalse(errors)
        json_import["currency_code"] = "EUR"
        errors = self.env.datamodels["sale.order"].validate(json_import)
        self.assertTrue(errors)

    def test_payment_create(self):
        json_import = self.sale_data
        new_sale_order = self.importer_component.run(json.dumps(json_import))
        new_payment = new_sale_order.transaction_ids
        self.assertEqual(new_payment.reference, "PMT-EXAMPLE-001")
