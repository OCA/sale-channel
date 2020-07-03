#  Copyright (c) Akretion 2020
#  License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

from unittest.mock import patch

from odoo.exceptions import ValidationError

from odoo.addons.base_rest.controllers.main import _PseudoCollection
from odoo.addons.component.core import WorkContext
from odoo.addons.sale_import_base.tests.common_sale_order_import import SaleImportCase


class TestSaleOrderImport(SaleImportCase):
    @property
    def payload_multi_sale(self):
        chunks_data = [self.chunk_vals["data_str"], self.chunk_vals["data_str"]]
        chunks_data[1]["payment"]["reference"] = "PMT-EXAMPLE-002"
        result = self.env.datamodels["sale.import.input"].load(
            {"sale_orders": chunks_data}
        )
        return result

    def setUp(self):
        super().setUp()
        self.api_key = "ASecureKeyEbay"
        collection = _PseudoCollection("sale.import.rest.services", self.env)
        self.sale_import_service_env = WorkContext(
            model_name="sale.order", collection=collection
        )

    def test_chunks_created(self):
        chunk_count_initial = self.env["queue.job.chunk"].search_count([])
        import_service = self.sale_import_service_env.component(usage="import")
        with patch(
            "odoo.addons.sale_import_rest.components.sale_import_service."
            "SaleImportService._get_api_key",
            return_value="ASecureKeyEbay",
        ):
            import_service.create(self.payload_multi_sale)
        chunk_count_after = self.env["queue.job.chunk"].search_count([])
        self.assertEqual(chunk_count_initial + 2, chunk_count_after)

    def test_wrong_key(self):
        import_service = self.sale_import_service_env.component(usage="import")
        with self.assertRaises(ValidationError), patch(
            "odoo.addons.sale_import_rest.components.sale_import_service."
            "SaleImportService._get_api_key",
            return_value="WrongKey",
        ):
            import_service.create(self.payload_multi_sale)

    def test_key_not_mapped_to_channel(self):
        self.env["auth.api.key"].create(
            {"name": "aName", "key": "ASecureKey", "user_id": 1}
        )
        import_service = self.sale_import_service_env.component(usage="import")
        with self.assertRaises(ValidationError), patch(
            "odoo.addons.sale_import_rest.components.sale_import_service."
            "SaleImportService._get_api_key",
            return_value="ASecureKey",
        ):
            import_service.create(self.payload_multi_sale)
