import logging
from contextlib import contextmanager

from . import common

_logger = logging.getLogger(__name__)

EXPECTED_PRODUCT_URL = "http://anyurl.com/api/products/imports?shop_id=11"
EXPECTED_OFFER_URL = "http://anyurl.com/api/offers/imports?shop_id=25"
EXPECTED_HEADERS = {"Authorization": "azerty", "Accept": "application/json"}
REQUEST_POST = "post"
CAT_CODE = "All > Saleable > Office Furniture"


class TestSProductExporter(common.SetUpMiraklBase):
    def test_make_product_file(self):

        attachment = self.mirakl_sc_for_product._create_and_fill_csv_file(
            [self.product1, self.product2]
        )
        filename = attachment.name
        reader = self._read_filename(filename)
        linesByID = {}
        for line in reader:
            linesByID[line["sku"]] = line

        self.assertEqual(2, len(linesByID))

        lineDict = linesByID["29182572"]
        expectedDict = {
            "sku": "29182572",
            "ean": "4004764782703",
            "PRODUCT_TITLE": "Conference Chair",
            "PRODUCT_DESCRIPTION": "<p>A smart description</p>",
            "PRODUCT_CAT_CODE": "All > Saleable > Office Furniture",
        }
        self.assertDictEqual(lineDict, expectedDict)

    def test_make_offers_file(self):

        attachment = self.mirakl_sc_for_offer._create_and_fill_csv_file(
            [self.product1, self.product2]
        )
        filename = attachment.name

        self.assertEqual("Offer_offers.csv", filename)

        reader = self._read_filename(filename)
        linesByID = {}
        for line in reader:
            linesByID[line["sku"]] = line

        self.assertEqual(2, len(linesByID))

        lineDict = linesByID["29182572"]
        expectedDict = {
            "sku": "29182572",
            "product-id": "4004764782703",
            "product-id-type": "EAN",
            "state": "11",
        }
        self.assertDictEqual(lineDict, expectedDict)

    def test_make_catalog_file(self):

        attachment = self.mirakl_sc_for_catalog._create_and_fill_csv_file(
            [self.product1, self.product2]
        )
        filename = attachment.name
        reader = self._read_filename(filename)
        linesByID = {}
        for line in reader:
            linesByID[line["sku"]] = line

        self.assertEqual(2, len(linesByID))

        lineDict = linesByID["29182572"]
        expectedDict = {
            "sku": "29182572",
            "ean": "4004764782703",
            "PRODUCT_TITLE": "Conference Chair",
            "PRODUCT_DESCRIPTION": "<p>A smart description</p>",
            "PRODUCT_CAT_CODE": "All > Saleable > Office Furniture",
            "product-id": "4004764782703",
            "product-id-type": "EAN",
            "state": "11",
        }
        self.assertDictEqual(lineDict, expectedDict)

    def _check_parameters_test(self, url, files, request_type):
        self.assertEqual(self.url, url)
        self.assertDictEqual(self.headers, EXPECTED_HEADERS)
        self.assertDictEqual(self.files, files)
        self.assertEqual(self.request_type, request_type)

    @contextmanager
    def _patch_process_request(self):
        def _mock_process_request(
            self_local,
            url,
            headers=None,
            params=None,
            data=None,
            files=None,
            ignore_result=False,
            request_type=None,
        ):
            self.url = url
            self.headers = headers
            self.files = files
            self.request_type = request_type

        self.mirakl_sc_for_product._patch_method(
            "_process_request", _mock_process_request
        )
        yield
        self.mirakl_sc_for_product._revert_method("_process_request")

    def test_post_products_file_on_mirakl(self):

        expected_filename = "{}_{}".format(
            "Product", self.mirakl_sc_for_product.offer_filename
        )
        expected_file_content = (
            '"sku";"ean";"PRODUCT_TITLE";"PRODUCT_DESCRIPTION";"PRODUCT_CAT_CODE"\r\n'
            '"{}";"{}";"{}";"{}";"{}"{}'.format(
                self.product2.default_code,
                self.product2.barcode,
                self.product2.name,
                self.product2.description,
                CAT_CODE,
                "\r\n",
            )
            + '"{}";"{}";"{}";"{}";"{}"{}'.format(
                self.product1.default_code,
                "",
                self.product1.name,
                self.product1.name,
                CAT_CODE,
                "\r\n",
            )
        )

        with self._patch_process_request():

            self.mirakl_sc_for_product._export_data([self.product1, self.product2])
            # self.mirakl_sc_for_product.channel_id._scheduler_export()

            self._check_parameters_test(
                EXPECTED_PRODUCT_URL,
                {"file": (expected_filename, expected_file_content)},
                REQUEST_POST,
            )

    def test_post_offers_file_on_mirakl(self):

        expected_filename = "{}_{}".format(
            "Offer", self.mirakl_sc_for_offer.offer_filename
        )
        expected_file_content = (
            '"sku";"product-id";"product-id-type";"state"\r\n'
            '"29491209";"29491209";"SHOP_SKU";"11"\r\n'
            '"29182572";"4004764782703";"EAN";"11"\r\n'
        )

        with self._patch_process_request():

            attachment = self.mirakl_sc_for_offer._create_and_fill_csv_file(
                [self.product1, self.product2]
            )
            self.mirakl_sc_for_offer.post(attachment)

            self._check_parameters_test(
                EXPECTED_OFFER_URL,
                {
                    "file": (expected_filename, expected_file_content),
                    "import_mode": "NORMAL",
                },
                REQUEST_POST,
            )

    def test_post_catalog_file_on_mirakl(self):

        expected_filename = self.mirakl_sc_for_offer.offer_filename
        expected_file_content = (
            '"sku";"ean";"PRODUCT_TITLE";"PRODUCT_DESCRIPTION";'
            '"PRODUCT_CAT_CODE";"product-id";"product-id-type";"state"\r\n'
            '"29491209";"";"Pedal Bin";"Pedal Bin";'
            '"All > Saleable > Office Furniture";"29491209";"SHOP_SKU";"11"\r\n'
            '"29182572";"4004764782703";"Conference Chair";'
            '"<p>A smart description</p>";"All > Saleable > Office Furniture";'
            '"4004764782703";"EAN";"11"\r\n'
        )

        with self._patch_process_request():
            attachment = self.mirakl_sc_for_catalog._create_and_fill_csv_file(
                [self.product1, self.product2]
            )
            self.mirakl_sc_for_catalog.post(attachment)

            self._check_parameters_test(
                EXPECTED_OFFER_URL,
                {
                    "file": (expected_filename, expected_file_content),
                    "import_mode": "NORMAL",
                    "with_products": "true",
                },
                REQUEST_POST,
            )

    def test_make_pydantic_sale_orders(self):
        sale_orders = self.mirakl_sc_for_catalog._make_mirakl_sale_order(self.orders)
        return sale_orders

    @contextmanager
    def _patch_call_request(self):
        def _make_sale_orders(
            self_local,
            url,
            headers=None,
            params=None,
            data=None,
            files=None,
            ignore_result=False,
            request_type=None,
        ):

            return {"orders": self.orders}

        self.mirakl_sc_for_product._patch_method("_process_request", _make_sale_orders)
        yield
        self.mirakl_sc_for_product._revert_method("_process_request")

    def test_map_data(self):
        with self._patch_call_request():
            self.mirakl_sc_for_product._import_sale_orders()
