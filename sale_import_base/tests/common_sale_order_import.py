#  Copyright (c) Akretion 2020
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import json
from copy import deepcopy

from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.addons.extendable.tests.common import ExtendableMixin

from .data import full, invalid, minimum, mixed


@tagged("post_install", "-at_install")
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


@tagged("post_install", "-at_install")
class SaleImportCase(TestSaleCommonNoDuplicates, ExtendableMixin):
    @classmethod
    def setUpClass(cls):
        super(SaleImportCase, cls).setUpClass()
        cls.init_extendable_registry()
        account_user = cls.env.user
        cls.env = cls.env(user=cls.env.ref("base.user_root"))
        cls.setUpPaymentProvider()
        cls.env = cls.env(user=account_user)
        cls.setUpMisc()
        cls.setUpProducts()
        cls.fiscal_pos_a.auto_apply = True
        cls.sale_order_example_vals_all = full
        cls.sale_order_example_vals_all["pricelist_id"] = cls.env.ref(
            "product.list0"
        ).id
        cls.sale_order_example_vals_minimum = minimum
        cls.sale_order_example_vals_mixed = mixed
        cls.sale_order_example_vals_invalid = invalid
        cls.last_sale_id = (
            cls.env["sale.order"].search([], order="id desc", limit=1).id or 0
        )
        cls.sale_channel_ebay = cls.env.ref("sale_channel.sale_channel_ebay")

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
    def setUpPaymentProvider(cls):
        # Create manual provider
        cls.env["payment.provider"]._fields["code"].selection.append(
            ("credit_card", "Credit Card")
        )
        cls.env["payment.provider"].create(
            {
                "name": "Credit Card",
                "ref": "credit_card",
                "code": "credit_card",
                "company_id": cls.company_data["company"].id,
            }
        )
        method = cls.env["account.payment.method"].create(
            {
                "code": "credit_card",
                "name": "Credit Card",
                "payment_type": "inbound",
            }
        )
        cls.env["account.payment.method.line"].create(
            [
                {
                    "name": method.code,
                    "payment_method_id": method.id,
                    "journal_id": cls.company_data["default_journal_bank"].id,
                }
            ]
        )

    @classmethod
    def setUpMisc(cls):
        cls.env = cls.env(context=dict(cls.env.context, test_queue_job_no_delay=True))

    @classmethod
    def get_payload_vals(cls, which_data):
        """
        :param which_data: all | mixed | minimum
        see data.py
        """
        return {
            "data_str": deepcopy(getattr(cls, "sale_order_example_vals_" + which_data)),
            "sale_channel_id": cls.env.ref("sale_channel.sale_channel_ebay").id,
        }

    @classmethod
    def _helper_create_payload(cls, vals_dict):
        """Converts data_str content to appropriate JSON format"""
        vals_dict["data_str"] = json.dumps(vals_dict["data_str"])
        return cls.env["sale.import.payload"].sudo().create(vals_dict)
