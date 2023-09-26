#  Copyright (c) Akretion 2020
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

import mock
from fastapi.testclient import TestClient

from odoo import SUPERUSER_ID
from odoo.tests import tagged

from odoo.addons.fastapi.context import odoo_env_ctx
from odoo.addons.sale_import_base.tests.common_sale_order_import import SaleImportCase


@tagged("-at_install", "post_install")
class TestSaleOrderImport(SaleImportCase):
    @property
    def payload_multi_sale(self):
        chunks_data = [
            self.get_chunk_vals("all")["data_str"],
            self.get_chunk_vals("all")["data_str"],
        ]
        chunks_data[1]["payment"]["reference"] = "PMT-EXAMPLE-002"
        return {"sale_orders": chunks_data}

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.cr.commit = mock.Mock()
        # Switch to Superuser, so we can check api result and configure everything
        cls.env = cls.env(user=SUPERUSER_ID)
        cls.api_key = "ASecureKeyApiRest"
        cls.fastapi_sale_import_app = cls.env.ref(
            "sale_import_rest.fastapi_endpoint_sale_import_demo"
        )
        cls.app = cls.fastapi_sale_import_app._get_app()
        cls.client = TestClient(cls.app, raise_server_exceptions=True)
        cls._ctx_token = odoo_env_ctx.set(cls.env)

    @classmethod
    def tearDownClass(cls) -> None:
        odoo_env_ctx.reset(cls._ctx_token)
        cls.fastapi_sale_import_app._reset_app()
        super().tearDownClass()

    def _get_path(self, path):
        return path

    def _call_path(self, path, vals, allow_error=False):
        with mock.patch.object(self.env.cr.__class__, "rollback"):
            res = self.client.post(
                self._get_path(path), json=vals, headers={"API-KEY": self.api_key}
            )
            if not allow_error:
                self.assertEqual(res.status_code, 200, res.text)
            return res

    def _service_create(self, vals, allow_error=False):
        return self._call_path("/sale/create", vals, allow_error=allow_error)

    def _service_cancel(self, vals, allow_error=False):
        return self._call_path("/sale/cancel", vals, allow_error=allow_error)

    def test_chunks_created(self):
        chunk_count_initial = self.env["queue.job.chunk"].search_count([])
        self._service_create(self.payload_multi_sale)
        chunk_count_after = self.env["queue.job.chunk"].search_count([])
        self.assertEqual(chunk_count_initial + 2, chunk_count_after)

    def test_wrong_key(self):
        self.api_key = "WrongKey"
        res = self._service_create(self.payload_multi_sale, allow_error=True)
        # TODO we should raise a 401 here
        # but the method "_retrieve_api_key" raise an error
        # see code in models/fastapi_endpoint.py
        self.assertEqual(res.status_code, 400, res.text)
        self.assertEqual(res.json(), {"detail": "The key WrongKey is not allowed"})

    def test_key_not_mapped_to_endpoint(self):
        self.env["auth.api.key"].create(
            {"name": "aName", "key": "ASecureKey", "user_id": 1}
        )
        self.api_key = "ASecureKey"
        res = self._service_create(self.payload_multi_sale, allow_error=True)
        self.assertEqual(res.status_code, 401, res.text)
        self.assertEqual(res.json(), {"detail": "Incorrect API Key"})

    def test_cancel_sale(self):
        sale = self.env.ref("sale.sale_order_1")
        sale.write(
            {
                "sale_channel_id": self.fastapi_sale_import_app.channel_id.id,
                "company_id": self.company_data["company"].id,
                "client_order_ref": "CLIENTREF",
            }
        )
        res = self._service_cancel({"sale_name": "CLIENTREF"})
        self.assertEqual(sale.state, "cancel")
        self.assertEqual(res.json(), {"success": True})

    def test_cancel_sale_missing(self):
        res = self._service_cancel({"sale_name": "does not exist"}, allow_error=True)
        self.assertEqual(res.status_code, 404, res.text)
        self.assertEqual(res.json(), {"detail": "MissingError"})
