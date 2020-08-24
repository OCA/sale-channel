#  Copyright (c) Akretion 2020
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from .common_sale_order_import import SaleImportCase


class TestSaleOrderImport(SaleImportCase):
    def setUp(self):
        super().setUp()
        self.sale_channel_ebay = self.env.ref("sale_channel.sale_channel_ebay")
        self.env = self.env(
            context=dict(self.env.context, test_queue_job_no_delay=True)
        )
        self.pricelist = self.env["product.pricelist"].create({"name": "Test"})

    def test_basic_all(self):
        """ Base scenario: create a sale order"""
        chunk = self._helper_create_chunk(self.get_chunk_vals("all"))
        self.assertTrue(self.get_created_sales().ids)
        self.assertEqual(chunk.state, "done")

    def test_basic_mixed(self):
        """ Base scenario: create a sale order"""
        chunk = self._helper_create_chunk(self.get_chunk_vals("mixed"))
        self.assertTrue(self.get_created_sales().ids)
        self.assertEqual(chunk.state, "done")

    def test_basic_minimum(self):
        """ Base scenario: create a sale order"""
        chunk = self._helper_create_chunk(self.get_chunk_vals("minimum"))
        self.assertTrue(self.get_created_sales().ids)
        self.assertEqual(chunk.state, "done")

    def test_invalid_json(self):
        """ An invalid input will stop the job """
        chunk_vals = self.get_chunk_vals("all")
        del chunk_vals["data_str"]["address_customer"]["name"]
        chunk = self._helper_create_chunk(chunk_vals)
        self.assertEqual(chunk.state, "fail")

    def test_create_partner(self):
        """ Base scenario: create partner, delivery, shipping addresses"""
        partner_count = (
            self.env["res.partner"].with_context(active_test=False).search_count([])
        )
        self._helper_create_chunk(self.get_chunk_vals("all"))
        partner_count_after_import = (
            self.env["res.partner"].with_context(active_test=False).search_count([])
        )
        self.assertEqual(partner_count_after_import, partner_count + 3)

    def test_binding_created(self):
        """ When we create a partner, a binding is created """
        self._helper_create_chunk(self.get_chunk_vals("all"))
        binding_count = self.env["sale.channel.partner"].search_count(
            [
                ("sale_channel_id", "=", self.sale_channel_ebay.id),
                ("partner_id", "=", self.get_created_sales().partner_id.id),
                ("external_id", "=", "ThomasJeanEbay"),
            ]
        )
        self.assertEqual(binding_count, 1)

    def test_import_existing_partner_match_external_id(self):
        """ During import, if a partner is matched on external_id/channel
        combination, his address is updated """
        partner = self.env.ref("base.res_partner_1")
        self.env["sale.channel.partner"].create(
            {
                "partner_id": partner.id,
                "external_id": "ThomasJeanEbay",
                "sale_channel_id": self.sale_channel_ebay.id,
            }
        )
        self._helper_create_chunk(self.get_chunk_vals("all"))
        self.assertEqual(partner.street, "1 rue de Jean")

    def test_import_existing_partner_match_email(self):
        """ During import, if a partner is matched on email,
        its address is updated """
        partner = self.env.ref("base.res_partner_3")
        partner.write({"email": "thomasjean@example.com"})
        self._helper_create_chunk(self.get_chunk_vals("all"))
        self.assertEqual(partner.street, "1 rue de Jean")

    def test_import_existing_partner_match_email_disallowed(self):
        """ Test that if email match is disallowed, we just create a partner """
        partner_count = (
            self.env["res.partner"].with_context(active_test=False).search_count([])
        )
        partner = self.env.ref("base.res_partner_1")
        partner.write({"email": "thomasjean@example.com"})
        self.sale_channel_ebay.allow_match_on_email = False
        self._helper_create_chunk(self.get_chunk_vals("all"))
        new_partner_count = (
            self.env["res.partner"].with_context(active_test=False).search_count([])
        )
        self.assertEqual(new_partner_count, partner_count + 3)

    def test_product_missing(self):
        """ Test product code validation effectively blocks the job """
        chunk_vals_wrong_product_code = self.get_chunk_vals("all")
        chunk_vals_wrong_product_code["data_str"]["lines"][0][
            "product_code"
        ] = "doesn't exist"
        chunk = self._helper_create_chunk(chunk_vals_wrong_product_code)
        self.assertEqual(chunk.state, "fail")

    def test_product_search(self):
        """ Check we get the right product match on product code"""
        self._helper_create_chunk(self.get_chunk_vals("all"))
        self.assertEqual(
            self.get_created_sales().order_line[0].product_id, self.product_order
        )
        self.assertEqual(
            self.get_created_sales().order_line[1].product_id, self.product_deliver
        )

    def test_wrong_total_amount(self):
        """ Test the sale.exception works as intended """
        chunk_vals_wrong_amount = self.get_chunk_vals("all")
        chunk_vals_wrong_amount["data_str"]["amount"]["amount_total"] += 500.0
        self._helper_create_chunk(chunk_vals_wrong_amount)
        exception_wrong_total_amount = self.env.ref(
            "sale_import_base.exc_wrong_total_amount"
        )
        self.assertEqual(
            self.get_created_sales().detect_exceptions(),
            [exception_wrong_total_amount.id],
        )

    def test_correct_amounts(self):
        """ Test the sale.exception works as intended """
        self._helper_create_chunk(self.get_chunk_vals("all"))
        self.assertFalse(self.get_created_sales().detect_exceptions())

    def test_deliver_country_with_tax(self):
        """ Test fiscal position is applied correctly """
        chunk_vals_other_country = self.get_chunk_vals("all")
        chunk_vals_other_country["data_str"]["address_shipping"]["country_code"] = "CH"
        del chunk_vals_other_country["data_str"]["address_shipping"]["state_code"]
        self._helper_create_chunk(chunk_vals_other_country)
        self.assertEqual(self.get_created_sales().fiscal_position_id, self.fpos_swiss)
        self.assertEqual(self.get_created_sales().order_line[0].tax_id, self.tax_swiss)

    def test_order_line_description(self):
        """ Test that a description is taken into account, or
        default description is generated if none is provided """
        self._helper_create_chunk(self.get_chunk_vals("mixed"))
        new_sale = self.get_created_sales()
        expected_desc = "[PROD_ORDER] Zed+ Antivirus"
        self.assertEqual(new_sale.order_line[0].name, expected_desc)

    def test_payment_create(self):
        self._helper_create_chunk(self.get_chunk_vals("all"))
        new_payment = self.get_created_sales().transaction_ids
        self.assertEqual(new_payment.reference, "PMT-EXAMPLE-001")
        self.assertEqual(new_payment.acquirer_reference, "T123")
        self.assertEqual(new_payment.amount, 640),
        self.assertEqual(new_payment.currency_id.name, "USD")

    def test_invoice_values(self):
        self._helper_create_chunk(self.get_chunk_vals("all"))
        invoice = self.get_created_sales()
        self.assertEqual(str(invoice.si_force_invoice_date), "1900-12-30")
        self.assertEqual(invoice.si_force_invoice_number, "IN-123")

    def test_validators(self):
        wrong_data = list()
        for itr in range(4):
            data = self.get_chunk_vals("all")
            data["data_str"]["payment"]["reference"] = "PMT-EXAMPLE-00%s" % str(itr)
            wrong_data.append(data)
        wrong_data[0]["data_str"]["address_customer"]["state_code"] = "somethingWrong"
        wrong_data[1]["data_str"]["address_customer"]["country_code"] = "somethingWrong"
        wrong_data[2]["data_str"]["lines"][0]["product_code"] = "somethingWrong"
        wrong_data[3]["data_str"]["payment"]["currency_code"] = "somethingWrong"
        for data in wrong_data:
            chunk = self._helper_create_chunk(data)
            self.assertEqual(chunk.state, "fail")
            self.assertIn("ValidationError", chunk.state_info)

    def test_pricelist_from_channel(self):
        self.sale_channel_ebay.pricelist_id = self.pricelist
        vals = self.get_chunk_vals("all")
        vals["data_str"].pop("pricelist_id")
        chunk = self._helper_create_chunk(vals)
        self.assertEqual(chunk.state, "done")
        sale = self.get_created_sales()
        self.assertEqual(sale.pricelist_id, self.pricelist)

    def test_pricelist_from_params(self):
        vals = self.get_chunk_vals("all")
        vals["data_str"]["pricelist_id"] = self.pricelist.id
        chunk = self._helper_create_chunk(vals)
        self.assertEqual(chunk.state, "done")
        sale = self.get_created_sales()
        self.assertEqual(sale.pricelist_id, self.pricelist)

    def test_pricelist_from_default(self):
        chunk = self._helper_create_chunk(self.get_chunk_vals("all"))
        self.assertEqual(chunk.state, "done")
        sale = self.get_created_sales()
        self.assertEqual(sale.pricelist_id, self.env.ref("product.list0"))
