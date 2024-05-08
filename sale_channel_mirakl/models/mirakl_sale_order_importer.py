import logging
from datetime import date, datetime, timedelta
from urllib.parse import urlencode

from odoo import fields, models, tools

from ..mirakl_mapper.mirakl_sale_order import MiraklSaleOrder

_logger = logging.getLogger(__name__)


class MiraklSaleOrderImporter(models.AbstractModel):
    _name = "mirakl.sale.order.importer"
    _description = "used to define specific methods for sale orders import"
    _inherit = "mirakl.importer"

    def _preprocess_address_emails(self, mirakl_record):
        """

        :param mirakl_record:
        :return:
        """
        billing_partner_obj = mirakl_record.customer.billing_address
        delivery_partner_obj = mirakl_record.customer.shipping_address

        if billing_partner_obj.email == delivery_partner_obj.email:
            delivery_partner_obj.email = ""

        return mirakl_record

    def _order_line_preprocess(self, mirakl_record):
        """

        :param mirakl_record:
        :return:
        """
        accepted_lines = []
        order_lines = mirakl_record.order_lines
        for line in order_lines:
            if line.order_line_state not in ("CANCELED", "REFUSED"):
                accepted_lines.append(line)

        mirakl_record.order_lines = accepted_lines
        return mirakl_record

    def _build_dependencies(self, sale_channel, mirakl_record):
        """

        :param sale_channel:
        :param mirakl_record:
        :return:
        """
        record = mirakl_record
        customer = record.customer
        importer_customer_name = self._get_importers().get(type(customer))
        importer_customer = self.env[importer_customer_name]
        importer_customer._build_dependencies(
            sale_channel,
            customer,
        )
        res = super()._build_dependencies(sale_channel, mirakl_record)
        customer.billing_address.customer_notification_email = (
            record.customer_notification_email
        )

        customer.shipping_address.shipping_zone_code = record.shipping_zone_code
        return res

    def create_or_update_record(self, sale_channel, mirakl_sale_order):
        """

        :param sale_channel:
        :param external_id:
        :param mirakl_sale_order:
        :param binding_model:
        :return:
        """

        mirakl_sale_order = self._preprocess_address_emails(mirakl_sale_order)
        mirakl_sale_order = self._order_line_preprocess(mirakl_sale_order)

        return super().create_or_update_record(sale_channel, mirakl_sale_order)

    def _call(self, sale_channel, api):
        """

        :param sale_channel:
        :param api:
        :return:
        """
        location = sale_channel.location
        channel_api_key = sale_channel.api_key

        url = "{}/{}".format(location, api)
        headers = {"Authorization": channel_api_key}
        params = {}
        if sale_channel.max_items_to_import > 0:
            params.update({"max": sale_channel.max_items_to_import})

        return sale_channel._process_request(
            url, headers=headers, params=params, request_type="get"
        )

    def import_orders(self, sale_channel, from_date=None, to_date=None, state=None):
        """

        :param sale_channel:
        :param from_date:
        :param to_date:
        :param state:
        :return:
        """
        from_date = (
            fields.Date.to_string(date.today() - timedelta(days=1))
            if not from_date
            else from_date
        )
        to_date = fields.Date.to_string(date.today()) if not to_date else to_date
        state = state or "SHIPPING"
        params = {"start_date": from_date, "end_date": to_date, "state": state}
        mirakl_orders_api = sale_channel.sale_orders_api

        api = f"{mirakl_orders_api}?{urlencode(params)}".replace("%3A", ":")
        return self._call(sale_channel, api)

    def _after_import(self, binding):
        """

        :param binding:
        :return:
        """
        res = super()._after_import(binding)
        main_partner = binding.partner_id
        shipping_partner = binding.partner_shipping_id

        if main_partner not in (shipping_partner, shipping_partner.parent_id):
            data = {"type": "delivery", "parent_id": main_partner.id}
            shipping_partner.write(data)
        return res

    def _map_orders(self, imported_orders: list):
        """
        Build pydantic sales order objects in mirakl format with data imported from mirakl
        :param orders_data: sales order data imported from Mirakl
        :return: pydantic sales order list
        """
        for order in imported_orders:
            yield MiraklSaleOrder.build_mirakl_sale_order(order)

    def _adapt_filter(self, sale_channel, filters):
        """

        :param sale_channel:
        :param filters:
        :return:
        """
        from_date = (
            fields.Date.to_string(
                fields.Datetime.from_string(
                    sale_channel.import_orders_from_date
                ).isoformat()
            )
            if sale_channel.import_orders_from_date
            else fields.Date.to_string(
                date.today() - timedelta(days=sale_channel.mirakl_delay)
            )
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

    def _get_binding(self, sale_channel, mirakl_record):
        external_id = mirakl_record.get_key()
        binding_model = mirakl_record._odoo_model

        if binding_model == "sale.order":
            binding = self.env[binding_model].search(
                [
                    ("mirakl_code", "=", tools.ustr(external_id)),
                    ("channel_ids", "in", sale_channel.channel_id.id),
                ],
                limit=2,
            )

            if len(binding) > 1:
                _logger.warning(
                    "there are many records linked to the same mirakl record"
                )
                binding = fields.first(binding)
            return binding
        else:
            return super()._get_binding(sale_channel, mirakl_record)

    def _import_sale_orders_batch(self, sale_channel, filters=None):
        """

        :param sale_channel:
        :param filters:
        :return:
        """
        filters = filters or {}
        filters = self._adapt_filter(sale_channel, filters)

        from_date = filters.pop("from_date")
        to_date = filters.pop("to_date")
        state = filters.pop("state", "SHIPPING")
        result = self.import_orders(
            sale_channel, from_date=from_date, to_date=to_date, state=state
        )
        imported_orders = result["orders"] or []

        for mirakl_sale_order in self._map_orders(imported_orders):
            if not self._get_binding(
                sale_channel,
                mirakl_sale_order,
            ):
                self.create_or_update_record(sale_channel, mirakl_sale_order)
