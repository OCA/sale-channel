#  Copyright (c) Akretion 2020
#  License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

import requests

import odoo.tools
from odoo.tests import HttpCase

from odoo.addons.base_rest.tests.common import BaseRestCase
from odoo.addons.sale_import_base.tests.common_sale_order_import import SaleImportCase


@odoo.tests.common.at_install(False)
@odoo.tests.common.post_install(True)
class TestSaleOrderImport(SaleImportCase, HttpCase, BaseRestCase):
    def setUp(self):
        super().setUp()
        self.setUpRegistry()
        host = "127.0.0.1"
        port = odoo.tools.config["http_port"]
        self.url = "http://%s:%d/sale-import/import" % (host, port)
        # self.request_content = "{
        # \"api_key\": \"ASecureKeyEbay\",\"payload\": [\"%s\"]
        # }" % self.sale_data
        self.request_content = {
            "api_key": "ASecureKeyEbay",
            "payload": [self.sale_data],
        }

    # @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_chunks_created(self):
        chunk_count_initial = self.env["queue.job.chunk"].search_count([])
        requests.post(self.url, json=self.request_content)
        chunk_count_after = self.env["queue.job.chunk"].search_count([])
        self.assertEqual(chunk_count_initial + 1, chunk_count_after)

    def test_controller_create_function(self):
        pass
