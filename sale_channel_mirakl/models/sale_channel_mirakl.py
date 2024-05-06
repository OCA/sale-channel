import base64
import csv
import hashlib
import io
import logging
from collections import OrderedDict
from datetime import date, datetime, timedelta

import requests

from odoo import fields, models

from ..mirakl_mapper.mirakl_catalog import MiraklCatalog
from ..mirakl_mapper.mirakl_offer import MiraklOffer
from ..mirakl_mapper.mirakl_product import MiraklProduct

_logger = logging.getLogger(__name__)
DELIMITER = ";"
MIRAKL_DELAY = 2


class SaleChannelMirakl(models.Model):
    _name = "sale.channel.mirakl"
    _inherits = {"sale.channel": "channel_id"}
    _description = "sale channel from Mirakl"

    channel_id = fields.Many2one(
        comodel_name="sale.channel", required=True, index=True, ondelete="restrict"
    )

    location = fields.Char(required=True, help="Url to Mirakl application")
    api_key = fields.Char(help="WebService API Key")
    url = fields.Char(store=True)

    offer_filename = fields.Char(string="Offers File Name", required=True)
    shop_id = fields.Char(string="Shop ID on Mirakl")

    data_to_export = fields.Selection(
        selection=[
            ("product", "Product"),
            ("offer", "Offer"),
            ("catalog", "Catalog"),
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
        selection=[("sale.order", "Sale Order")],
        default="sale.order",
        string="Type of data to Import",
    )

    def _get_url(self):
        return "{}/api/".format(self.location)

    def _get_file_options(self):
        """
        Get additional options for the CSV file based on data's type to export.
        :return: Additional options for the CSV file.
        """
        if self.data_to_export == "offer":
            return MiraklOffer.get_additional_option_for_file()
        elif self.data_to_export == "catalog":
            return MiraklCatalog.get_additional_option_for_file()
        else:
            return {}

    def _get_url_suffix(self):
        """
        The URL suffix (varies depending on the type of data to export)
        :return: url suffix
        """
        if self.data_to_export == "catalog":
            return "offers/imports"
        return "{}s/imports".format(self.data_to_export)

    def _get_filename_prefix(self):
        """
        The file name prefix for exporting data
        (varies depending on the type of data to be exported)
        :return: file name prefix
        """
        if self.data_to_export == "catalog":
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
        if self.data_to_export == "product":
            return self.generate_header_from_fields(self._get_product_file_header())
        elif self.data_to_export == "offer":
            return self.generate_header_from_fields(self._get_offer_file_header())
        elif self.data_to_export == "catalog":
            return self.generate_header_from_fields(self._get_catalog_file_header())

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
            csvfile, delimiter=DELIMITER, quoting=csv.QUOTE_ALL, quotechar='"'
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

        return self.env["ir.attachment"].create(attach_data)

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
            "product": MiraklProduct,
            "offer": MiraklOffer,
            "catalog": MiraklCatalog,
        }
        MiraklMapping = mapping.get(struct_key)
        if MiraklMapping:
            for product in products:
                mapped_products.append(MiraklMapping.map_item(self, product))
        return mapped_products

    def _generate_hash_key(self, customer):
        """
        This method is used to generate a key from customer not identified
        on Mirakl.
        The connector will generate one based on select data such as name,
        and city. Used principally when the is imported
        """
        hashtring = "".join([customer.firstname, customer.lastname, customer.city])
        if not hashtring:
            return False
        hash_object = hashlib.sha1(hashtring.encode("utf8"))
        return hash_object.hexdigest()

    def _get_binding(self, sale_channel, external_id, binding_model):
        return self.env["mirakl_importer"]._get_binding(
            sale_channel, external_id, binding_model
        )

    def _import_data(self, filters=None):
        filters = self._adapt_filter(filters)
        self.env["sale.channel.owner"]._import_batch(self, filters)
        self.write({"import_orders_from_date": False})

    def _adapt_filter(self, filters):
        filters = filters or {}

        from_date = (
            fields.Date.to_string(
                fields.Datetime.from_string(self.import_orders_from_date).isoformat()
            )
            if self.import_orders_from_date
            else fields.Date.to_string(date.today() - timedelta(days=MIRAKL_DELAY))
        )
        filters.setdefault("from_date", "{}T00:00:00".format(from_date))

        now = fields.Datetime.context_timestamp(self, datetime.now())
        to_date = fields.Date.to_string(now.date())
        time = now.time()
        to_date = "{}T{}:{}:59".format(
            to_date,
            str(time.hour).zfill(2),
            str(time.minute).zfill(2),
        )
        filters.setdefault("to_date", to_date)

        filters.setdefault("state", "SHIPPING")
        return filters

    def _map_to_odoo_record(self, mirakl_pydantic_object):
        return mirakl_pydantic_object.odoo_model_dump(self)
