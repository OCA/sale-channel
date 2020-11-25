#  Copyright (c) Akretion 2020
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import json
from copy import deepcopy

from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.addons.component.tests.common import SavepointComponentCase
from odoo.addons.datamodel.tests.common import SavepointDatamodelCase

from .data import full, minimum, mixed


class TestSaleCommonNoDuplicates(AccountTestInvoicingCommon):
    """
    TestSaleCommon has duplicate products, thus we must create a new class
    This one is similar to Odoo's base with some parts cut out
    TODO delete this class or clean it up
    """

    @classmethod
    def setup_sale_configuration_for_company(cls, company):
        cls.env["res.users"].with_context(no_reset_password=True)

        company_data = {
            # Sales Team
            "default_sale_team": cls.env["crm.team"]
            .with_context(tracking_disable=True)
            .create(
                {
                    "name": "Test Channel",
                    "company_id": company.id,
                }
            ),
            # Pricelist
            "default_pricelist": cls.env["product.pricelist"]
            .with_company(company)
            .create(
                {
                    "name": "default_pricelist",
                    "currency_id": company.currency_id.id,
                }
            ),
            # Product category
            "product_category": cls.env["product.category"]
            .with_company(company)
            .create(
                {
                    "name": "Test category",
                }
            ),
        }
        return company_data

    @classmethod
    def setup_company_data(cls, company_name, chart_template=None, **kwargs):
        company_data = super().setup_company_data(
            company_name, chart_template=chart_template, **kwargs
        )
        company_data.update(
            cls.setup_sale_configuration_for_company(company_data["company"])
        )
        company_data["product_category"].write(
            {
                "property_account_income_categ_id": company_data[
                    "default_account_revenue"
                ].id,
                "property_account_expense_categ_id": company_data[
                    "default_account_expense"
                ].id,
            }
        )
        return company_data


class SaleImportCase(
    TestSaleCommonNoDuplicates, SavepointDatamodelCase, SavepointComponentCase
):
    @classmethod
    def setUpClass(cls):
        super(SaleImportCase, cls).setUpClass()
        cls.setUpPaymentAcquirer()
        cls.setUpMisc()
        cls.setUpProducts()
        cls.fiscal_pos_a.auto_apply = True
        cls.sale_order_example_vals_all = full
        cls.sale_order_example_vals_all["pricelist_id"] = cls.env.ref(
            "product.list0"
        ).id
        cls.sale_order_example_vals_minimum = minimum
        cls.sale_order_example_vals_mixed = mixed
        cls.last_sale_id = (
            cls.env["sale.order"].search([], order="id desc", limit=1).id or 0
        )

    @classmethod
    def get_created_sales(cls):
        return cls.env["sale.order"].search(
            [("id", ">", cls.last_sale_id)], order="id desc"
        )

    @classmethod
    def setUpProducts(cls):  # TODO clear this out with TestSaleCommonNoDuplicates
        cls.product_a.default_code = "SKU_A"
        cls.product_b.default_code = "SKU_B"

    @classmethod
    def setUpPaymentAcquirer(cls):
        PaymentAcquirer = cls.env["payment.acquirer"]

        # Acquirer and mode of payment
        acquirer_vals = {
            "name": "credit_card",
            "provider": "manual",
            "company_id": cls.env.ref("base.main_company").id,
            "payment_flow": "s2s",
        }
        PaymentAcquirer.create(acquirer_vals)

    @classmethod
    def setUpMisc(cls):
        cls.env = cls.env(context=dict(cls.env.context, test_queue_job_no_delay=True))

    @classmethod
    def get_chunk_vals(cls, which_data):
        """
        :param which_data: all | mixed | minimum
        see data.py
        """
        return {
            "apply_on_model": "sale.order",
            "data_str": deepcopy(getattr(cls, "sale_order_example_vals_" + which_data)),
            "usage": "json_import",
            "model_name": "sale.channel",
            "record_id": cls.env.ref("sale_channel.sale_channel_ebay").id,
        }

    @classmethod
    def _helper_create_chunk(cls, vals_dict):
        """ Converts data_str content to appropriate JSON format """
        vals_dict["data_str"] = json.dumps(vals_dict["data_str"])
        return cls.env["queue.job.chunk"].create(vals_dict)
