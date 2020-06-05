# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from copy import deepcopy

from odoo.addons.component.tests.common import SavepointComponentCase
from odoo.addons.datamodel.tests.common import SavepointDatamodelCase
from odoo.addons.sale.tests.test_sale_common import TestCommonSaleNoChart

from .data import data


class SaleImportCase(
    SavepointDatamodelCase, TestCommonSaleNoChart, SavepointComponentCase
):
    @classmethod
    def setUpClass(cls):
        super(SaleImportCase, cls).setUpClass()
        cls.setUpClassicProducts()
        cls.setUpTaxes()
        cls.setUpFpos()
        cls.setUpPaymentAcquirer()
        cls.setUpMisc()
        cls.sale_order_example_vals = data
        cls.sale_order_example_vals["pricelist_id"] = cls.env.ref("product.list0").id

    @classmethod
    def setUpTaxes(cls):
        tax_obj = cls.env["account.tax"]
        tax_vals = {
            "name": "Fictional tax 9%",
            "amount": "9.00",
            "type_tax_use": "sale",
            "company_id": cls.env.ref("base.main_company").id,
        }
        cls.tax = tax_obj.create(tax_vals)
        cls.product_order.taxes_id = cls.tax

    @classmethod
    def setUpFpos(cls):
        tax_obj = cls.env["account.tax"]
        fiscal_pos_obj = cls.env["account.fiscal.position"]
        fiscal_pos_line_obj = cls.env["account.fiscal.position.tax"]

        # CH
        fpos_vals_swiss = {
            "name": "Swiss Fiscal Position",
            "country_id": cls.env.ref("base.ch").id,
            "zip_from": 0,
            "zip_to": 0,
            "auto_apply": True,
        }
        cls.fpos_swiss = fiscal_pos_obj.create(fpos_vals_swiss)
        tax_vals_swiss = {
            "name": "Swiss Export tax_obj",
            "amount": "0.00",
            "type_tax_use": "sale",
            "company_id": cls.env.ref("base.main_company").id,
        }
        cls.tax_swiss = tax_obj.create(tax_vals_swiss)
        fpos_line_vals = {
            "position_id": cls.fpos_swiss.id,
            "tax_src_id": cls.tax.id,
            "tax_dest_id": cls.tax_swiss.id,
        }
        fiscal_pos_line_obj.create(fpos_line_vals)

    @classmethod
    def setUpPaymentAcquirer(cls):
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

    @classmethod
    def setUpMisc(cls):
        cls.env = cls.env(context=dict(cls.env.context, test_queue_job_no_delay=True))
        dummy_chunk = cls.env["queue.job.chunk"].create(
            {
                "usage": "basic_create",
                "apply_on_model": "res.partner",
                "data_str": '{"name": "Dummy Partner"}',
            }
        )
        with dummy_chunk.work_on("sale.order") as work:
            cls.importer_component = work.component(usage="json_import")

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
