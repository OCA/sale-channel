#  Copyright (c) Akretion 2020
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import datetime
from unittest import mock

from odoo.tests import tagged

from .common_sale_order_import import SaleImportCase


@tagged("-at_install", "post_install")
class TestSaleOrderImport(SaleImportCase):
    def setUp(self):
        super().setUp()
        self.env = self.env(
            context=dict(self.env.context, test_queue_job_no_delay=True)
        )
        self.pricelist = self.env["product.pricelist"].create({"name": "Test"})
        self.env.cr.commit = mock.Mock()

    def test_basic_all(self):
        """Base scenario: create a sale order"""
        payload = self._helper_create_payload(self.get_payload_vals("all"))
        self.assertEqual(
            payload.state, "done", f"{payload.state_info}\n{payload.stack_trace}"
        )
        self.assertTrue(self.get_created_sales().ids)

    def test_basic_mixed(self):
        """Base scenario: create a sale order"""
        payload = self._helper_create_payload(self.get_payload_vals("mixed"))
        self.assertEqual(
            payload.state, "done", f"{payload.state_info}\n{payload.stack_trace}"
        )
        self.assertTrue(self.get_created_sales().ids)

    def test_basic_minimum(self):
        """Base scenario: create a sale order"""
        payload = self._helper_create_payload(self.get_payload_vals("minimum"))
        self.assertEqual(
            payload.state, "done", f"{payload.state_info}\n{payload.stack_trace}"
        )
        self.assertTrue(self.get_created_sales().ids)
        self.assertEqual(payload.state, "done")

    def test_invalid_json(self):
        """An invalid input will stop the job"""
        payload_vals = self.get_payload_vals("all")
        del payload_vals["data_str"]["address_customer"]["name"]
        payload = self._helper_create_payload(payload_vals)
        self.assertEqual(payload.state, "fail")

    def test_name_clientref(self):
        self._helper_create_payload(self.get_payload_vals("minimum"))
        self.assertEqual(self.get_created_sales().name, "XX-0001")

    def test_name_native(self):
        self.sale_channel_ebay.internal_naming_method = "name"
        self._helper_create_payload(self.get_payload_vals("minimum"))
        self.assertEqual(
            self.get_created_sales().name[0], "S"
        )  # native name is S + padding length 5
        self.assertEqual(len(self.get_created_sales().name), 6)

    def test_create_partner(self):
        """
        Base scenario: import Sale Order with standard data
        -> Create partner
        -> Create delivery, shipping addresses in inactive state by default
        """
        partner_count = (
            self.env["res.partner"].with_context(active_test=False).search_count([])
        )
        self._helper_create_payload(self.get_payload_vals("all"))
        partner_count_after_import = (
            self.env["res.partner"].with_context(active_test=False).search_count([])
        )
        self.assertEqual(partner_count_after_import, partner_count + 3)
        sale = self.get_created_sales()
        self.assertEqual(sale.partner_shipping_id.type, "delivery")
        self.assertEqual(sale.partner_shipping_id.active, False)
        self.assertEqual(sale.partner_invoice_id.type, "invoice")
        self.assertEqual(sale.partner_invoice_id.active, False)

    def test_create_partner_no_archive(self):
        """
        Base scenario: import Sale Order with standard data
        -> Create partner
        -> Create delivery, shipping addresses remains active because
            it has been configured with archive_addresses = False
        """
        partner_count = (
            self.env["res.partner"].with_context(active_test=False).search_count([])
        )
        payload_vals = self.get_payload_vals("all")
        channel = self.env["sale.channel"].browse(payload_vals["sale_channel_id"])
        channel.archive_addresses = False
        self._helper_create_payload(payload_vals)
        partner_count_after_import = (
            self.env["res.partner"].with_context(active_test=False).search_count([])
        )
        self.assertEqual(partner_count_after_import, partner_count + 3)
        sale = self.get_created_sales()
        self.assertEqual(sale.partner_shipping_id.type, "delivery")
        self.assertEqual(sale.partner_shipping_id.active, True)
        self.assertEqual(sale.partner_invoice_id.type, "invoice")
        self.assertEqual(sale.partner_invoice_id.active, True)

    def test_create_addresses_identical(self):
        """
        Test if shipping and invoice addresses are the same,
        create only 1 res.partner for both
        """
        partner_count = (
            self.env["res.partner"].with_context(active_test=False).search_count([])
        )
        payload_vals = self.get_payload_vals("minimum")
        payload_vals["data_str"]["address_shipping"] = payload_vals["data_str"][
            "address_invoicing"
        ]
        self._helper_create_payload(payload_vals)
        new_partner_count = (
            self.env["res.partner"].with_context(active_test=False).search_count([])
        )
        self.assertEqual(new_partner_count, partner_count + 2)

    def test_create_addresses_multiple_times(self):
        """
        Test new invoice and shipping addresses are created
        during every import
        """
        partner_count = (
            self.env["res.partner"].with_context(active_test=False).search_count([])
        )
        self._helper_create_payload(self.get_payload_vals("minimum"))
        # change name else second payload won't generate any order
        payload_vals2 = self.get_payload_vals("minimum")
        payload_vals2["data_str"]["name"] = "XX-0002"
        self._helper_create_payload(payload_vals2)
        new_partner_count = (
            self.env["res.partner"].with_context(active_test=False).search_count([])
        )
        # 3 for 1st SO (partner + shipping + invoice)
        # + 2 (shipping + invoice) for 2nd SO
        self.assertEqual(new_partner_count, partner_count + 5)

    def test_binding_created(self):
        """When we create a partner, a binding is created"""
        self._helper_create_payload(self.get_payload_vals("all"))
        binding_count = self.env["sale.channel.partner"].search_count(
            [
                ("sale_channel_id", "=", self.sale_channel_ebay.id),
                ("partner_id", "=", self.get_created_sales().partner_id.id),
                ("external_id", "=", "ThomasJeanEbay"),
            ]
        )
        self.assertEqual(binding_count, 1)

    def test_import_existing_partner_match_external_id(self):
        """During import, if a partner is matched on external_id/channel
        combination, his address is updated"""
        partner = self.env.ref("base.res_partner_1")
        self.env["sale.channel.partner"].create(
            {
                "partner_id": partner.id,
                "external_id": "ThomasJeanEbay",
                "sale_channel_id": self.sale_channel_ebay.id,
            }
        )
        self._helper_create_payload(self.get_payload_vals("all"))
        self.assertEqual(partner.street, "1 rue de Jean")

    def test_import_existing_partner_match_email(self):
        """During import, if a partner is matched on email,
        its address is updated"""
        partner = self.env.ref("base.res_partner_3")
        partner.write({"email": "thomasjean@example.com"})
        self._helper_create_payload(self.get_payload_vals("all"))
        self.assertEqual(partner.street, "1 rue de Jean")

    def test_import_existing_partner_match_email_disallowed(self):
        """Test that if email match is disallowed, we just create a partner"""
        partner_count = (
            self.env["res.partner"].with_context(active_test=False).search_count([])
        )
        partner = self.env.ref("base.res_partner_1")
        partner.write({"email": "thomasjean@example.com"})
        self.sale_channel_ebay.allow_match_on_email = False
        self._helper_create_payload(self.get_payload_vals("all"))
        new_partner_count = (
            self.env["res.partner"].with_context(active_test=False).search_count([])
        )
        self.assertEqual(new_partner_count, partner_count + 3)

    def test_product_missing(self):
        """Test product code validation effectively blocks the job"""
        payload_vals_wrong_product_code = self.get_payload_vals("all")
        payload_vals_wrong_product_code["data_str"]["lines"][0][
            "product_code"
        ] = "doesn't exist"
        payload = self._helper_create_payload(payload_vals_wrong_product_code)
        self.assertEqual(payload.state, "fail")

    def test_product_search(self):
        """Check we get the right product match on product code"""
        self._helper_create_payload(self.get_payload_vals("all"))
        self.assertEqual(
            self.get_created_sales().order_line[0].product_id, self.product_a
        )
        self.assertEqual(
            self.get_created_sales().order_line[1].product_id, self.product_b
        )

    def test_wrong_total_amount(self):
        """Test the sale.exception works as intended"""
        payload_vals_wrong_amount = self.get_payload_vals("all")
        payload_vals_wrong_amount["data_str"]["amount"]["amount_total"] += 500.0
        self._helper_create_payload(payload_vals_wrong_amount)
        exception_wrong_total_amount = self.env.ref(
            "sale_import_base.exc_wrong_total_amount"
        )
        # rule is unactive by default
        exception_wrong_total_amount.sudo().write({"active": True})
        self.assertEqual(
            self.get_created_sales().detect_exceptions(),
            [exception_wrong_total_amount.id],
        )

    def test_correct_amounts(self):
        """Test the sale.exception works as intended"""
        self._helper_create_payload(self.get_payload_vals("all"))
        self.assertFalse(self.get_created_sales().detect_exceptions())

    def test_deliver_country_with_tax(self):
        """
        Test fiscal position is applied correctly
        - change source tax to 5%
        - don't change destination tax (should be 15%)
        Check in the end we correctly get 15% tax
        """
        self.tax_sale_a.amount = 5
        self.fiscal_pos_a.country_id = self.env.ref("base.ch")
        payload_vals_other_country = self.get_payload_vals("all")
        payload_vals_other_country["data_str"]["address_shipping"][
            "country_code"
        ] = "CH"
        del payload_vals_other_country["data_str"]["address_shipping"]["state_code"]
        self._helper_create_payload(payload_vals_other_country)
        self.assertEqual(self.get_created_sales().fiscal_position_id, self.fiscal_pos_a)
        self.assertEqual(self.get_created_sales().order_line[0].tax_id, self.tax_sale_b)

    def test_order_line_description(self):
        """Test that a description is taken into account, or
        default description is generated if none is provided"""
        self._helper_create_payload(self.get_payload_vals("mixed"))
        new_sale = self.get_created_sales()
        expected_desc = "[FURN_7777] Office Chair"
        # expected_desc = "[PROD_ORDER] Office Chair"
        self.assertEqual(new_sale.order_line[0].name, expected_desc)

    def test_payment_create(self):
        self._helper_create_payload(self.get_payload_vals("all"))
        new_payment = self.get_created_sales().transaction_ids
        self.assertEqual(new_payment.reference, "PMT-EXAMPLE-001")
        self.assertEqual(new_payment.provider_reference, "T123")
        self.assertEqual(new_payment.amount, 1173),
        self.assertEqual(new_payment.currency_id.name, "USD")

    def test_validators(self):
        wrong_data = list()
        for itr in range(4):
            data = self.get_payload_vals("all")
            data["data_str"]["payment"]["reference"] = "PMT-EXAMPLE-00%s" % str(itr)
            wrong_data.append(data)
        wrong_data[0]["data_str"]["address_customer"]["state_code"] = "somethingWrong"
        wrong_data[1]["data_str"]["address_customer"]["country_code"] = "somethingWrong"
        wrong_data[2]["data_str"]["lines"][0]["product_code"] = "somethingWrong"
        wrong_data[3]["data_str"]["payment"]["currency_code"] = "somethingWrong"
        for data in wrong_data:
            payload = self._helper_create_payload(data)
            self.assertEqual(payload.state, "fail")
            self.assertIn("ValidationError", payload.state_info)

    def test_pricelist_from_channel(self):
        self.sale_channel_ebay.pricelist_id = self.pricelist
        vals = self.get_payload_vals("all")
        vals["data_str"].pop("pricelist_id")
        payload = self._helper_create_payload(vals)
        self.assertEqual(payload.state, "done")
        sale = self.get_created_sales()
        self.assertEqual(sale.pricelist_id, self.pricelist)

    def test_pricelist_from_params(self):
        vals = self.get_payload_vals("all")
        vals["data_str"]["pricelist_id"] = self.pricelist.id
        payload = self._helper_create_payload(vals)
        self.assertEqual(payload.state, "done")
        sale = self.get_created_sales()
        self.assertEqual(sale.pricelist_id, self.pricelist)

    def test_pricelist_from_default(self):
        payload = self._helper_create_payload(self.get_payload_vals("all"))
        self.assertEqual(payload.state, "done")
        sale = self.get_created_sales()
        self.assertEqual(sale.pricelist_id, self.env.ref("product.list0"))

    def test_date_correct(self):
        self._helper_create_payload(self.get_payload_vals("all"))
        expected_date = datetime.datetime.strptime("2020-01-02", "%Y-%m-%d")
        self.assertEqual(self.get_created_sales().date_order, expected_date)

    def test_invoicing(self):
        self.env["product.template"].search([]).write({"invoice_policy": "order"})
        self.sale_channel_ebay.write({"invoice_order": True, "confirm_order": True})
        self._helper_create_payload(self.get_payload_vals("all"))
        sale = self.get_created_sales()
        self.assertEqual(sale.state, "sale")
        self.assertEqual(len(sale.invoice_ids), 1)
        invoice = sale.invoice_ids
        self.assertEqual(invoice.state, "draft")

        # Process transaction (normally done by a cron)
        sale.transaction_ids._cron_finalize_post_processing()
        self.assertEqual(invoice.state, "posted")
        self.assertEqual(invoice.payment_state, "paid")

    def test_create_duplicate_order(self):
        payload1 = self._helper_create_payload(self.get_payload_vals("minimum"))
        payload2 = self._helper_create_payload(self.get_payload_vals("minimum"))
        self.assertEqual(payload1.state, "done")
        self.assertEqual(payload2.state, "fail")
        self.assertIn(
            "Sale Order XX-0001 has already been created", payload2.state_info
        )

    def test_invalid_payload(self):
        payload = self._helper_create_payload(self.get_payload_vals("invalid"))
        self.assertEqual(payload.state, "fail")
        self.assertIn("ValidationError", payload.state_info)

    def test_vaccuum(self):
        payload = self._helper_create_payload(self.get_payload_vals("all"))
        old_date = datetime.datetime.now() - datetime.timedelta(days=370)
        payload.flush_model()
        self.env.cr.execute(
            "UPDATE sale_import_payload SET create_date = %s",
            (old_date.strftime("%Y-%m-%d %H:%M:%S"),),
        )
        self.env["sale.import.payload"].invalidate_model(["create_date"])
        # Enter test mode to run the autovacuum cron because `_run_vacuum_cleaner`
        # makes a commit
        self.registry.enter_test_mode(self.cr)
        self.addCleanup(self.registry.leave_test_mode)
        env = self.env(cr=self.registry.cursor())
        # Run the autovacuum cron
        env.ref("base.autovacuum_job").method_direct_trigger()
        self.assertFalse(payload.exists())
