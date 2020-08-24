#  Copyright (c) Akretion 2020
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import json
from copy import deepcopy

from odoo.addons.component.tests.common import SavepointComponentCase
from odoo.addons.datamodel.tests.common import SavepointDatamodelCase
from odoo.addons.sale.tests.test_sale_common import TestCommonSaleNoChart

from .data import full, minimum, mixed


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
        cls.sale_order_example_vals_all = full
        cls.sale_order_example_vals_all["pricelist_id"] = cls.env.ref(
            "product.list0"
        ).id
        cls.sale_order_example_vals_minimum = minimum
        cls.sale_order_example_vals_mixed = mixed
        cls.last_sale_id = cls.env["sale.order"].search([], order="id desc", limit=1).id

    @classmethod
    def get_created_sales(cls):
        return cls.env["sale.order"].search(
            [("id", ">", cls.last_sale_id)], order="id desc"
        )

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
            "name": "Swiss Export",
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
