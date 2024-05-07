import base64
import csv
import io
import logging
from collections import OrderedDict
from datetime import timedelta

import requests

from odoo import fields, models

from ..mirakl_mapper.mirakl_catalog import MiraklCatalog
from ..mirakl_mapper.mirakl_export_mapper import MiraklExportMapper
from ..mirakl_mapper.mirakl_offer import MiraklOffer
from ..mirakl_mapper.mirakl_product import MiraklProduct

_logger = logging.getLogger(__name__)
PRODUCT = "product"
OFFER = "offer"
CATALOG = "catalog"
SALE_ORDER = "sale.order"


class SaleChannelMirakl(models.Model):
    _name = "sale.channel.mirakl"
    _inherits = {"sale.channel": "channel_id"}
    _description = "sale channel from Mirakl"

    channel_id = fields.Many2one(
        comodel_name="sale.channel", required=True, index=True, ondelete="restrict"
    )

    location = fields.Char(required=True, help="Url to Mirakl application")
    api_key = fields.Char(help="WebService API Key")

    offer_filename = fields.Char(string="Offers File Name", required=True)
    shop_id = fields.Char(string="Shop ID on Mirakl")

    data_to_export = fields.Selection(
        selection=[
            (PRODUCT, "Product"),
            (OFFER, "Offer"),
            (CATALOG, "Catalog"),
        ],
        string="Type of data to Export",
        required=True,
    )

    default_country_id = fields.Many2one(
        "res.country",
        string="Default Country",
        help="This country will be mentionned by default on adresses if no one"
        " is provided by the marketplace",
    )

    import_orders_from_date = fields.Datetime("Import Orders from Date")

    data_to_import = fields.Selection(
        selection=[(SALE_ORDER, "Sale Order")],
        default=SALE_ORDER,
        string="Type of data to Import",
    )

    max_items_to_import = fields.Integer(
        default=100,
        help="allows you to define the maximum number of objects "
        "to import per call. If <=0, import the maximum number possible "
        "depending on the corresponding data to import",
    )

    sale_orders_api = fields.Char(
        default="api/orders", help="Mirakl api key for sale order import"
    )

    file_delimiter = fields.Char(default=";")

    attachment_delation_day = fields.Integer(
        default=7,
        help="Delay in days before attachments created by the channel are deleted",
    )

    mirakl_delay = fields.Integer(default=2)

    _sql_constraints = [
        (
            "check_value",
            "CHECK(mirakl_delay > 0)",
            "The mirakl delay responsible for sale orders import "
            "must be strictly positive",
        ),
    ]

    def _get_url(self):
        return "{}/api/".format(self.location)

    def _get_file_options(self):
        """
        Get additional options for the CSV file based on data's type to export.
        :return: Additional options for the CSV file.
        """
        return self.pydantic_class.get_additional_options()

    @property
    def pydantic_class(self):
        if self.data_to_export == PRODUCT:
            return MiraklProduct
        elif self.data_to_export == OFFER:
            return MiraklOffer
        elif self.data_to_export == CATALOG:
            return MiraklCatalog
        else:
            return MiraklExportMapper

    def _get_url_suffix(self):
        """
        The URL suffix (varies depending on the type of data to export)
        :return: url suffix
        """
        if self.data_to_export == CATALOG:
            return "offers/imports"
        return "{}s/imports".format(self.data_to_export)

    def _get_filename_prefix(self):
        """
        The file name prefix for exporting data
        (varies depending on the type of data to be exported)
        :return: file name prefix
        """
        if self.data_to_export == CATALOG:
            return ""
        return "{}_".format(self.data_to_export.capitalize())

    def _get_product_file_header(self):
        return MiraklProduct.get_products_file_header()

    def _get_offer_file_header(self):
        return MiraklOffer.get_offers_file_header()

    def _get_catalog_file_header(self):
        header = self._get_product_file_header().copy()
        header.extend(
            [
                attr
                for attr in self._get_offer_file_header()
                if attr not in self._get_product_file_header()
            ]
        )
        return header

    def _get_header(self, data_map):
        ordered_dict = OrderedDict(sorted(data_map.items(), key=lambda r: r[1]))
        return ordered_dict.keys()

    def _create_ordered_dict(self, data_list):
        return {key: position for position, key in enumerate(data_list)}

    def generate_header_from_fields(self, fields_list):
        header_dict = self._create_ordered_dict(fields_list)
        return list(self._get_header(header_dict))

    def _get_file_header(self):
        return self.pydantic_class.get_file_header()

    def _get_http_request(self, request_type):
        if request_type == "post":
            return requests.post
        elif request_type == "get":
            return requests.get
        elif request_type == "put":
            return requests.put

    def _process_request(
        self,
        url,
        headers=None,
        params=None,
        data=None,
        files=None,
        ignore_result=False,
        request_type=None,
    ):
        """
        Process a POST request to the specified URL.
        :param url: URL for the request.
        :param headers: Headers for the request.
        :param params: Parameters for the request.
        :param data: Data for the request.
        :param files: Files to be sent with the request.
        :param request_type: type of http request to do
        """
        headers = headers or {}
        params = params or {}
        data = data or {}
        files = files or {}
        http_request = self._get_http_request(request_type)

        response = http_request(
            url, headers=headers, params=params, data=data, files=files
        )

        if response.status_code not in [200, 201, 204]:
            error = response.json()
            message = "{} - {}".format(error["status"], error["message"])
            raise Exception(message)

        if not ignore_result:
            return response.json()

    def post(self, attachment):
        """
        Allows you to launch the export method
        :param attachment: file who content the data to export
        """
        url = "{}{}".format(self._get_url(), self._get_url_suffix())
        shop_id_param = "?shop_id=" + self.shop_id if self.shop_id else ""
        url_with_shop_id = url + shop_id_param

        headers = {
            "Authorization": self.api_key,
            "Accept": "application/json",
        }

        filename = attachment.name
        file_content = base64.b64decode(attachment.datas).decode()
        files = {"file": (filename, file_content)}

        file_options = self._get_file_options()
        files.update(file_options)

        request_type = "post"
        try:
            self._process_request(
                url_with_shop_id,
                headers=headers,
                files=files,
                ignore_result=True,
                request_type=request_type,
            )
        except Exception as e:
            _logger.error("An error occurred while posting data to Mirakl: %s", e)

    def _create_and_fill_csv_file(self, pydantic_items):
        """
        Method to initialize and populate the export file
        :param items: products list
        :return: the file's name and its contents
        """

        header = self._get_file_header()
        csvfile = io.StringIO()

        csv_writer = csv.writer(
            csvfile, delimiter=self.file_delimiter, quoting=csv.QUOTE_ALL, quotechar='"'
        )
        csv_writer.writerow(header)

        for pydantic_item in pydantic_items:
            pydantic_json = pydantic_item.to_json()
            csv_writer.writerow([pydantic_json.get(attr, "") for attr in header])

        filename_prefix = self._get_filename_prefix()
        filename = "{}{}".format(filename_prefix, self.offer_filename)
        file_content = csvfile.getvalue()
        attach_data = {
            "name": filename,
            "datas": base64.encodebytes(str.encode(file_content)),
            "res_model": self._name,
            "res_id": self.id,
        }
        attachment = self.env["ir.attachment"].create(attach_data)

        # deletion_day = fields.Datetime.now() + timedelta(
        #     days=self.attachment_delation_day
        # )
        #
        # attachment.with_delay(eta=deletion_day).unlink() Currently, I have to
        # comment because having skipped the execution of the jobs for my tests,
        # the attachment is deleted before being returned

        return attachment

    def _export_data(self, pydantic_items):
        """
        Super class data export method adapted to Mirakl
        (Export products or offers)
        :param items: items to export.
        """
        self.ensure_one()
        attachment = self._create_and_fill_csv_file(pydantic_items)
        self.post(attachment)

    def _map_items(self, struct_key, products):
        """

        :param struct_key: Key word who allows you to define the appropriate
         mapping function to call
        :param products: products to map
        :return: the list of mapped products
        """
        self.ensure_one()
        mapped_products = []
        mapping = {
            PRODUCT: MiraklProduct,
            OFFER: MiraklOffer,
            CATALOG: MiraklCatalog,
        }
        MiraklMapping = mapping.get(struct_key)
        if MiraklMapping:
            for product in products:
                # yield MiraklMapping.map_item(
                #     self, product
                # )
                mapped_products.append(MiraklMapping.map_item(self, product))
        return mapped_products

    def _get_binding(self, sale_channel, external_id, binding_model):
        return self.env["mirakl_importer"]._get_binding(
            sale_channel, external_id, binding_model
        )

    def _import_data(self, struct_key):
        if struct_key == SALE_ORDER:
            self.env["mirakl.sale.order.importer"]._import_sale_orders_batch(self)
            self.write({"import_orders_from_date": False})
            return None
        else:
            return self.channel_id._import_data(self, struct_key)

    def _map_to_odoo_record(self, mirakl_pydantic_object):
        return mirakl_pydantic_object.odoo_model_dump(self)
