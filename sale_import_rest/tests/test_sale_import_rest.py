#  Copyright (c) Akretion 2020
#  License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

from unittest.mock import patch

from odoo import SUPERUSER_ID
from odoo.exceptions import MissingError, ValidationError

from odoo.addons.base_rest.controllers.main import _PseudoCollection
from odoo.addons.component.core import WorkContext
from odoo.addons.sale_import_base.tests.common_sale_order_import import SaleImportCase


class TestSaleOrderImport(SaleImportCase):
    @property
    def payload_multi_sale(self):
        chunks_data = [
            self.get_chunk_vals("all")["data_str"],
            self.get_chunk_vals("all")["data_str"],
        ]
        chunks_data[1]["payment"]["reference"] = "PMT-EXAMPLE-002"
        return {"sale_orders": chunks_data}

    def setUp(self):
        super().setUp()
        # As the env.user is superuser anyways for our controllers,
        # for now we neglect it for tests
        superuser = self.env["res.users"].browse([SUPERUSER_ID])
        self.env = self.env(user=superuser)
        self.cr = self.env.cr
        self.api_key = "ASecureKeyEbay"
        collection = _PseudoCollection("sale.import.rest.services", self.env)
        self.sale_import_service_env = WorkContext(
            model_name="sale.order", collection=collection
        )
        self.service = self.sale_import_service_env.component(usage="sale")
        self.api_key = "ASecureKeyEbay"

    def _service_create(self, vals):
        with patch(
            "odoo.addons.sale_import_rest.components.sale_import_service."
            "SaleImportService._get_api_key",
            return_value=self.api_key,
        ):
            return self.service.dispatch("create", params=vals)

    def _service_cancel(self, params):
        with patch(
            "odoo.addons.sale_import_rest.components.sale_import_service."
            "SaleImportService._get_api_key",
            return_value=self.api_key,
        ):
            return self.service.dispatch("cancel", params=params)

    def test_chunks_created(self):
        chunk_count_initial = self.env["queue.job.chunk"].search_count([])
        self._service_create(self.payload_multi_sale)
        chunk_count_after = self.env["queue.job.chunk"].search_count([])
        self.assertEqual(chunk_count_initial + 2, chunk_count_after)

    def test_wrong_key(self):
        self.api_key = "WrongKey"
        with self.assertRaises(ValidationError):
            return self._service_create(self.payload_multi_sale)

    def test_key_not_mapped_to_channel(self):
        self.env["auth.api.key"].create(
            {"name": "aName", "key": "ASecureKey", "user_id": 1}
        )
        self.api_key = "ASecureKey"
        with self.assertRaises(ValidationError):
            return self._service_create(self.payload_multi_sale)

    def test_cancel_sale(self):
        channel = self.env.ref("sale_channel.sale_channel_ebay")
        sale = self.env.ref("sale.sale_order_1")
        sale.sale_channel_id = channel
        res = self._service_cancel({"sale_name": sale.name})
        self.assertEqual(sale.state, "cancel")
        self.assertEqual(res, {"success": True})

    def test_cancel_sale_missing(self):
        sale = self.env.ref("sale.sale_order_1")
        with self.assertRaises(MissingError):
            self._service_cancel({"sale_name": sale.name})
        self.assertEqual(sale.state, "draft")
