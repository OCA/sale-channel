import logging
from contextlib import contextmanager

from ..models.sale_channel_mirakl import SALE_ORDER
from . import common
from .common import MIRAKL_CODE2

_logger = logging.getLogger(__name__)

EXPECTED_PRODUCT_URL = "http://anyurl.com/api/products/imports?shop_id=11"
EXPECTED_OFFER_URL = "http://anyurl.com/api/offers/imports?shop_id=25"
EXPECTED_HEADERS = {"Authorization": "azerty", "Accept": "application/json"}
REQUEST_POST = "post"
CAT_CODE = "All > Saleable > Office Furniture"
EAN = "EAN"
STATE = "11"
PROD_ID_TYPE = "SHOP_SKU"
EMPTY_STRING = ""
CARRIAGE_RETURN = "\r\n"


class TestProductOfferExporter(common.SetUpMiraklBase):
    def test_make_product_file(self):

        struct_key = self.mirakl_sc_for_product.data_to_export
        mapped_products = self.mirakl_sc_for_product.channel_id._map_items(
            struct_key, [self.product1, self.product2]
        )

        attachment = self.mirakl_sc_for_product._create_and_fill_csv_file(
            mapped_products
        )

        filename = attachment.name
        reader = self._read_filename(filename)
        linesByID = {}
        for line in reader:
            linesByID[line["sku"]] = line

        self.assertEqual(2, len(linesByID))

        lineDict = linesByID[MIRAKL_CODE2]
        expectedDict = {
            "sku": MIRAKL_CODE2,
            "ean": self.product2.barcode,
            "PRODUCT_TITLE": self.product2.name,
            "PRODUCT_DESCRIPTION": self.product2.description,
            "PRODUCT_CAT_CODE": "All > Saleable > Office Furniture",
        }
        self.assertDictEqual(lineDict, expectedDict)

    def test_make_offers_file(self):

        struct_key = self.mirakl_sc_for_offer.data_to_export
        mapped_products = self.mirakl_sc_for_offer.channel_id._map_items(
            struct_key, [self.product1, self.product2]
        )

        attachment = self.mirakl_sc_for_offer._create_and_fill_csv_file(mapped_products)
        filename = attachment.name

        self.assertEqual("Offer_offers.csv", filename)

        reader = self._read_filename(filename)
        linesByID = {}
        for line in reader:
            linesByID[line["sku"]] = line

        self.assertEqual(2, len(linesByID))

        lineDict = linesByID[MIRAKL_CODE2]
        expectedDict = {
            "sku": MIRAKL_CODE2,
            "product-id": self.product2.barcode,
            "product-id-type": EAN,
            "state": STATE,
        }
        self.assertDictEqual(lineDict, expectedDict)

    def test_make_catalog_file(self):
        struct_key = self.mirakl_sc_for_catalog.data_to_export
        mapped_products = self.mirakl_sc_for_catalog.channel_id._map_items(
            struct_key, [self.product1, self.product2]
        )

        attachment = self.mirakl_sc_for_catalog._create_and_fill_csv_file(
            mapped_products
        )
        filename = attachment.name
        reader = self._read_filename(filename)
        linesByID = {}
        for line in reader:
            linesByID[line["sku"]] = line

        self.assertEqual(2, len(linesByID))

        lineDict = linesByID[MIRAKL_CODE2]
        expectedDict = {
            "sku": MIRAKL_CODE2,
            "ean": self.product2.barcode,
            "PRODUCT_TITLE": self.product2.name,
            "PRODUCT_DESCRIPTION": self.product2.description,
            "PRODUCT_CAT_CODE": "All > Saleable > Office Furniture",
            "product-id": self.product2.barcode,
            "product-id-type": EAN,
            "state": STATE,
        }
        self.assertDictEqual(lineDict, expectedDict)

    def _check_parameters_test(self, url, files, request_type):
        self.assertEqual(self.url, url)
        self.assertDictEqual(self.headers, EXPECTED_HEADERS)
        self.assertDictEqual(self.files, files)
        self.assertEqual(self.request_type, request_type)

    @contextmanager
    def _patch_process_request(self, sale_channel):
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

        sale_channel._patch_method("_process_request", _mock_process_request)
        yield
        sale_channel._revert_method("_process_request")

    def test_post_products_file_on_mirakl(self):
        expected_filename = "{}_{}".format(
            "Product", self.mirakl_sc_for_product.offer_filename
        )
        expected_file_content = (
            '"sku";"ean";"PRODUCT_TITLE";"PRODUCT_DESCRIPTION";"PRODUCT_CAT_CODE"\r\n'
            '"{p2_dfl}";"{p2_brcd}";"{p2_name}";"{p2_desc}";"{cat}"{car_return}'
            '"{p1_dfl}";"{empty}";"{p1_name}";"{p1_name}";"{cat}"{car_return}'.format(
                p2_dfl=self.product2.default_code,
                p2_brcd=self.product2.barcode,
                p2_name=self.product2.name,
                p2_desc=self.product2.description,
                cat=CAT_CODE,
                car_return=CARRIAGE_RETURN,
                p1_dfl=self.product1.default_code,
                empty=EMPTY_STRING,
                p1_name=self.product1.name,
            )
        )

        with self._patch_process_request(self.mirakl_sc_for_product):
            self.mirakl_sc_for_product.channel_id._scheduler_export()
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
            '"{p2_dfl}";"{p2_brcd}";"{ean}";"{state}"{car_return}'
            '"{p1_dfl}";"{p1_dfl}";"{prod_id_type}";"{state}"{car_return}'.format(
                p2_dfl=self.product2.default_code,
                p2_brcd=self.product2.barcode,
                ean=EAN,
                state=STATE,
                car_return=CARRIAGE_RETURN,
                p1_dfl=self.product1.default_code,
                prod_id_type=PROD_ID_TYPE,
            )
        )

        with self._patch_process_request(self.mirakl_sc_for_offer):
            self.mirakl_sc_for_offer.channel_id._scheduler_export()
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
            '"sku";"ean";"PRODUCT_TITLE";"PRODUCT_DESCRIPTION";"PRODUCT_CAT_CODE"'
            ';"product-id";"product-id-type";"state"\r\n'
            '"{p2_dfl}";"{p2_brcd}";"{p2_name}";"{p2_desc}";"{cat}";"{p2_brcd}";'
            '"{ean}";"{state}"{car_return}'
            '"{p1_dfl}";"{empty}";"{p1_name}";"{p1_name}";"{cat}";"{p1_dfl}";'
            '"{prod_id_type}";"{state}"{car_return}'.format(
                p2_dfl=self.product2.default_code,
                p2_brcd=self.product2.barcode,
                p2_name=self.product2.name,
                p2_desc=self.product2.description,
                cat=CAT_CODE,
                ean=EAN,
                state=STATE,
                car_return=CARRIAGE_RETURN,
                p1_dfl=self.product1.default_code,
                empty=EMPTY_STRING,
                p1_name=self.product1.name,
                prod_id_type=PROD_ID_TYPE,
            )
        )

        with self._patch_process_request(self.mirakl_sc_for_catalog):
            self.mirakl_sc_for_catalog.channel_id._scheduler_export()
            self._check_parameters_test(
                EXPECTED_OFFER_URL,
                {
                    "file": (expected_filename, expected_file_content),
                    "import_mode": "NORMAL",
                    "with_products": "true",
                },
                REQUEST_POST,
            )

    def test_get_struct_to_import(self):
        for struct_key in self.mirakl_sc_import.channel_id._get_struct_to_import():
            self.assertEqual(struct_key, SALE_ORDER)

    @contextmanager
    def _patch_call_request(self, sale_channel):
        def _sub_function(
            self_local,
            url,
            headers=None,
            params=None,
            data=None,
            files=None,
            ignore_result=False,
            request_type=None,
        ):

            return self.mirakl_sale_orders

        sale_channel._patch_method("_process_request", _sub_function)
        yield
        sale_channel._revert_method("_process_request")

    def test_sale_orders_import(self):
        with self._patch_call_request(self.mirakl_sc_import):
            self.mirakl_sc_import.channel_id._scheduler_import()

    @contextmanager
    def _patch_import_one_sale_order(self, sale_channel):
        def _only_one_sale_order(
            self_local,
            url,
            headers=None,
            params=None,
            data=None,
            files=None,
            ignore_result=False,
            request_type=None,
        ):
            return self.a_sale_order

        sale_channel._patch_method("_process_request", _only_one_sale_order)
        yield
        sale_channel._revert_method("_process_request")

    def test_import_one_sale_order(self):
        with self._patch_import_one_sale_order(self.mirakl_sc_import):
            orders = self.sale_channel_4._job_trigger_import(SALE_ORDER)

            self.assertEqual(1, len(orders))
            self.assertEqual(type(orders[0]), self.env[SALE_ORDER].__class__)
            self.assertTrue(orders[0].is_from_mirakl)
