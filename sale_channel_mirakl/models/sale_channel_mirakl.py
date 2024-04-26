import base64
import csv
import hashlib
import io
import logging
from collections import OrderedDict
from datetime import date, datetime, timedelta

import requests

from odoo import _, fields, models
from odoo.exceptions import UserError

from .fastapi_mapper import MiraklOffer, MiraklProduct, MiraklSaleOrder

_logger = logging.getLogger(__name__)

SALE_ORDER = "sale.order"
RES_PARTNER = "res.partner"


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

    binded_product_ids = fields.Many2many(
        comodel_name="product.template",
        relation="product_template_sale_channel_mirakl_rel",
        column2="product_template_id",
        column1="sale_channel_id",
        string="Binded Products",
    )

    data_to_export = fields.Selection(
        selection=[
            ("product", "Product"),
            ("offer", "Offer"),
            ("both", "Both"),
        ],
        string="Type of data to Export",
        required=True,
    )

    import_orders_from_date = fields.Datetime("Import Orders from Date")

    def _get_url(self):
        return "{}/api/".format(self.location)

    def _get_file_options(self):
        """
        Get additional options for the CSV file based on data's type to export.
        :return: Additional options for the CSV file.
        """
        if self.data_to_export == "offer":
            return {"import_mode": "NORMAL"}
        elif self.data_to_export == "both":
            return {"import_mode": "NORMAL", "with_products": "true"}
        else:
            return {}

    def _get_url_suffix(self):
        """
        The URL suffix (varies depending on the type of data to export)
        :return: url suffix
        """
        if self.data_to_export == "both":
            return "offers/imports"
        return "{}s/imports".format(self.data_to_export)

    def _get_filename_prefix(self):
        """
        The file name prefix for exporting data
        (varies depending on the type of data to be exported)
        :return: file name prefix
        """
        if self.data_to_export == "both":
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
        elif self.data_to_export == "both":
            return self.generate_header_from_fields(self._get_catalog_file_header())
        else:
            error = _("The only data type to export can be (product, offer, both)")
            raise UserError(error)

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

    def _map_item(self, item):
        """
        Mapping function based on data type
        :param item: item to map
        :return: dictionary containing mapped data of the item
        """
        if self.data_to_export == "product":
            mapped_product = MiraklProduct.build_mirakl_product(item)
            return mapped_product.pydantic_product_model_dump()

        elif self.data_to_export == "offer":
            mapped_offer = MiraklOffer.build_mirakl_offer(item)
            return mapped_offer.pydantic_offer_model_dump()

        elif self.data_to_export == "both":
            mapped_product = MiraklProduct.adapt_to_mirakl_record(item)
            mapped_offer = MiraklOffer.adapt_to_mirakl_record(item)

            json_product = mapped_product.pydantic_product_model_dump()
            json_offer = mapped_offer.pydantic_offer_model_dump()

            json_data = {
                **json_product,
                **{
                    key: json_offer[key]
                    for key in json_offer
                    if key not in json_product
                },
            }
            return json_data
        return None

    def _generate_mapped_items(self, items):
        """
        Generates mapped items one by one from the product list
        :param items: products list
        """
        for item in items:
            mapped_item_dict = self._map_item(item)
            yield mapped_item_dict

    def _create_and_fill_csv_file(self, items):
        """
        Method to initialize and populate the export file
        :param items: products list
        :return: the file's name and its contents
        """

        header = self._get_file_header()
        csvfile = io.StringIO()

        csv_writer = csv.writer(
            csvfile, delimiter=";", quoting=csv.QUOTE_ALL, quotechar='"'
        )
        csv_writer.writerow(header)

        for mapped_item_dict in self._generate_mapped_items(items):
            csv_writer.writerow([mapped_item_dict.get(attr, "") for attr in header])

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

    def _export_data(self, items):
        """
        Super class data export method adapted to Mirakl
        (Export products or offers)
        :param items: items to export.
        """
        attachment = self._create_and_fill_csv_file(items)
        self.post(attachment)

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

    def _adapt_filter_for_sale_orders_import(self, filters):
        # filters = filters or {}

        from_date = (
            fields.Date.to_string(
                fields.Datetime.from_string(self.import_orders_from_date).isoformat()
            )
            if self.import_orders_from_date
            else fields.Date.to_string(date.today() - timedelta(days=2))
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

    def _import_sale_orders(self, filters=None):
        if not filters:
            filters = {}
        filters = self._adapt_filter_for_sale_orders_import(filters)
        self.env["sale.channel.owner"]._import_sale_orders_batch(self, filters)
        # self.write({"import_orders_from_date": False})

    def _make_mirakl_sale_order(self, orders_data: list):
        """
        Build pydantic sales order objects in mirakl format with data imported from mirakl
        :param orders_data: sales order data imported from Mirakl
        :return: pydantic sales order list
        """
        mirakl_sale_orders = []
        for order_data in orders_data:
            mirakl_sale_orders.append(
                MiraklSaleOrder.make_mirakl_sale_order(order_data)
            )

        return mirakl_sale_orders

    def _map_to_odoo_record(self, mirakl_pydantic_object):
        return mirakl_pydantic_object.odoo_model_dump(self)

    def action_view_binded_products(self):
        return self.channel_id.action_view_binded_products()
