# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from copy import deepcopy

from odoo.addons.component.tests.common import SavepointComponentCase
from odoo.addons.datamodel.tests.common import SavepointDatamodelCase
from odoo.addons.sale.tests.test_sale_common import TestCommonSaleNoChart


class SaleImportCase(
    SavepointDatamodelCase, TestCommonSaleNoChart, SavepointComponentCase
):
    @classmethod
    def setUpClass(cls):
        super(SaleImportCase, cls).setUpClass()
        cls.setUpClassicProducts()
        cls.setUpAddresses()
        cls.setUpLines()
        cls.setUpImport()
        cls.setUpTaxes()
        cls.setUpFpos()
        cls.setUpPayment()
        cls.setUpMisc()

    @classmethod
    def setUpAddresses(cls):
        cls.addr_customer_example = {
            "name": "Thomas Jean",
            "street": "1 rue de Jean",
            "street2": "bis",
            "zip": "69100",
            "city": "Lyon",
            "email": "thomasjean@gmail.com",
            "country_code": "FR",
            "external_id": "ThomasJeanEbay",
        }
        cls.addr_shipping_example = {
            "name": "shipping contact name",
            "street": "2 rue de shipping",
            "street2": "bis",
            "zip": "69100",
            "city": "Lyon",
            "email": "not-required@not-required.com",
            "country_code": "FR",
        }
        cls.addr_invoicing_example = {
            "name": "invoicing contact name",
            "street": "3 rue de invoicing",
            "street2": "bis",
            "zip": "69100",
            "city": "Lyon",
            "email": "whatever@whatever.io",
            "country_code": "FR",
        }

    @classmethod
    def setUpLines(cls):
        cls.line_valid_1 = {
            "product_code": "PROD_ORDER",
            "qty": 5,
            "price_unit": 1111.1,
            "description": "Initial Line 1 import description",
            "discount": 10.0,
        }
        cls.line_valid_2 = {
            "product_code": "PROD_DEL",
            "qty": 2,
            "price_unit": 2222.2,
            # description: missing
            "discount": 0.0,
        }
        cls.line_invalid = {
            "product_code": "DOES NOT EXIST",
            "qty": "should not happen",
            "price_unit": "wrong input",
            "description": "",
            "discount": 0.0,
        }

    @classmethod
    def setUpImport(cls):
        amt_untaxed_1 = (
            cls.line_valid_1["price_unit"]
            * cls.line_valid_1["qty"]
            * (1 - cls.line_valid_1["discount"] / 100)
        )
        amt_tax_1 = amt_untaxed_1 * 0.09
        amt_total_1 = amt_untaxed_1 + amt_tax_1
        amt_untaxed_2 = cls.line_valid_2["price_unit"] * cls.line_valid_2["qty"]
        amt_tax_2 = amt_untaxed_2 * 0.00
        amt_total_2 = amt_untaxed_2 + amt_tax_2
        cls.amount_valid = {
            "amount_tax": amt_tax_1 + amt_tax_2,
            "amount_untaxed": amt_untaxed_1 + amt_untaxed_2,
            "amount_total": amt_total_1 + amt_total_2,
        }
        cls.amount_invalid = {
            "amount_tax": "this should not",
            "amount_untaxed": "happen",
            "amount_total": dict(),
        }
        cls.sale_order_invoice_example = {"date": "1900-12-30", "number": "IN-123"}
        cls.sale_channel_ebay = cls.env.ref("sale_channel.sale_channel_ebay")
        cls.sale_order_example_vals = {
            "address_customer": cls.addr_customer_example,
            "address_shipping": cls.addr_shipping_example,
            "address_invoicing": cls.addr_invoicing_example,
            "lines": [cls.line_valid_1, cls.line_valid_2],
            "amount": cls.amount_valid,
            "transaction_id": 123,
            "invoice": cls.sale_order_invoice_example,
            "sale_channel": cls.sale_channel_ebay.name,
            "currency_code": "USD",
            "pricelist_id": cls.env.ref("product.list0").id,
        }

    @classmethod
    def setUpTaxes(cls):
        Tax = cls.env["account.tax"]
        tax_vals = {
            "name": "Fictional tax 9%",
            "amount": "9.00",
            "type_tax_use": "sale",
            "company_id": cls.env.ref("base.main_company").id,
        }
        cls.tax = Tax.create(tax_vals)
        cls.product_order.taxes_id = cls.tax

    @classmethod
    def setUpFpos(cls):
        Tax = cls.env["account.tax"]
        Fpos = cls.env["account.fiscal.position"]
        FposLine = cls.env["account.fiscal.position.tax"]

        # CH
        fpos_vals_swiss = {
            "name": "Swiss Fiscal Position",
            "country_id": cls.env.ref("base.ch").id,
            "zip_from": 0,
            "zip_to": 0,
            "auto_apply": True,
        }
        cls.fpos_swiss = Fpos.create(fpos_vals_swiss)
        tax_vals_swiss = {
            "name": "Swiss Export Tax",
            "amount": "0.00",
            "type_tax_use": "sale",
            "company_id": cls.env.ref("base.main_company").id,
        }
        cls.tax_swiss = Tax.create(tax_vals_swiss)
        fpos_line_vals = {
            "position_id": cls.fpos_swiss.id,
            "tax_src_id": cls.tax.id,
            "tax_dest_id": cls.tax_swiss.id,
        }
        FposLine.create(fpos_line_vals)

    @classmethod
    def setUpPayment(cls):
        PaymentAcquirer = cls.env["payment.acquirer"]

        # Acquirer and mode of payment
        acquirer_vals = {
            "name": "credit_card",
            "provider": "manual",
            "company_id": cls.env.ref("base.main_company").id,
            "environment": "test",
            "payment_flow": "s2s",
        }
        PaymentAcquirer.create(acquirer_vals)

        # Payment values
        payment_vals = {
            "mode": "credit_card",
            "amount": 640.00,
            "reference": "PMT-EXAMPLE-001",
            "currency_code": "USD",
        }
        cls.sale_order_example_vals["payment"] = payment_vals

    @classmethod
    def setUpMisc(cls):
        cls.env = cls.env(context=dict(cls.env.context, test_queue_job_no_delay=True))
        collection = cls.env[
            "collection.base"
        ].new()  # DISCUSSION: peut pas mettre queue.job.chunk
        # Collection obligé d'être un record
        with collection.work_on("sale.order") as work:
            cls.importer_component = work.component(usage="import")

    @property
    def sale_data(self):
        return deepcopy(self.sale_order_example_vals)

    @property
    def sale_data_multi(self):
        result = [
            deepcopy(self.sale_order_example_vals),
            deepcopy(self.sale_order_example_vals),
        ]
        result[1]["payment"]["reference"] = "PMT-EXAMPLE-002"
        return result
