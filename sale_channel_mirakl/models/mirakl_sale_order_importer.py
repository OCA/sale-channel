import logging
from datetime import date, timedelta
from urllib.parse import urlencode

from odoo import fields, models

from odoo.addons.queue_job.exception import NothingToDoJob

from ..mirakl_mapper.mirakl_sale_order import MiraklSaleOrder

_logger = logging.getLogger(__name__)
BINDING_MODEL = "sale.order"


class MiraklSaleOrderImporter(models.AbstractModel):
    _name = "mirakl.sale.order.importer"
    _description = "used to define specific methods for sale orders import"
    _inherit = "mirakl.importer"

    _config = {}

    def _preprocess_address_emails(self, mirakl_record):
        billing_partner_obj = mirakl_record.customer.billing_address
        delivery_partner_obj = mirakl_record.customer.shipping_address

        if billing_partner_obj.email == delivery_partner_obj.email:
            delivery_partner_obj.email = ""

        return mirakl_record

    def _order_line_preprocess(self, mirakl_record):

        accepted_lines = []
        order_lines = mirakl_record.order_lines
        for line in order_lines:
            if line.order_line_state not in ("CANCELED", "REFUSED"):
                accepted_lines.append(line)

        mirakl_record.order_lines = accepted_lines
        return mirakl_record

    def _build_dependencies(self, sale_channel, mirakl_record):
        record = mirakl_record
        billing_partner_obj = record.customer.billing_address
        billing_partner_obj.customer_notification_email = (
            record.customer_notification_email
        )
        partner_mirakl_id = record.customer.customer_id
        self._build_dependency(
            sale_channel,
            partner_mirakl_id + "_billing",
            billing_partner_obj,
            "res.partner",
        )
        shipping_partner_obj = record.customer.shipping_address
        shipping_partner_obj.shipping_zone_code = record.shipping_zone_code
        self._build_dependency(
            sale_channel,
            partner_mirakl_id + "_shipping",
            shipping_partner_obj,
            "res.partner",
        )

    def create_or_update_record(
        self, sale_channel, external_id, mirakl_sale_order, binding_model
    ):
        mirakl_sale_order = self._preprocess_address_emails(mirakl_sale_order)
        mirakl_sale_order = self._order_line_preprocess(mirakl_sale_order)

        return super().create_or_update_record(
            sale_channel, external_id, mirakl_sale_order, binding_model
        )

    def _build_record(
        self, sale_channel, mirakl_sale_order, job_options=None, **kwargs
    ):
        external_id = mirakl_sale_order.order_id

        description = "Import sale order {} from Mirakl channel '{}'".format(
            external_id,
            sale_channel.channel_id.name,
        )

        job_options = job_options or {}
        job_options.update({"description": description})
        binding_model = self._config.get("binding_model")
        try:
            self.with_delay(**job_options or {}).create_or_update_record(
                sale_channel, external_id, mirakl_sale_order, binding_model, **kwargs
            )
        except NothingToDoJob:
            _logger.info("Dependency import has been ignored.")

    def _call(self, sale_channel, api):
        location = self._config.get("channel_location")
        channel_api_key = self._config.get("channel_api_key")
        request_type = self._config.get("request_type")

        url = "{}/{}".format(location, api)
        headers = {"Authorization": channel_api_key}
        params = {"max": 100}
        return sale_channel._process_request(
            url, headers=headers, params=params, request_type=request_type
        )

    def import_orders(self, sale_channel, from_date=None, to_date=None, state=None):
        from_date = (
            fields.Date.to_string(date.today() - timedelta(days=1))
            if not from_date
            else from_date
        )
        to_date = fields.Date.to_string(date.today()) if not to_date else to_date
        state = state or "SHIPPING"
        params = {"start_date": from_date, "end_date": to_date, "state": state}
        mirakl_orders_api = self._config.get("mirakl_orders_api")
        api = f"{mirakl_orders_api}?{urlencode(params)}"
        return self._call(sale_channel, api)

    def _after_import(self, binding):
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
            yield MiraklSaleOrder.make_mirakl_sale_order(order)

    def update_config(self, new_config):
        self._config.update(new_config)

    def _import_sale_orders_batch(self, sale_channel, filters):
        self.update_config({"mirakl_orders_api": "api/orders"})
        self.update_config({"channel_api_key": sale_channel.api_key})
        self.update_config({"channel_location", sale_channel.location})
        self.update_config({"request_type": "get"})
        self.update_config({"binding_model": "sale.order"})

        filters = filters or {}
        from_date = filters.pop("from_date", None)
        to_date = filters.pop("to_date", None)
        state = filters.pop("state", "SHIPPING")
        result = self.import_orders(
            sale_channel, from_date=from_date, to_date=to_date, state=state
        )
        imported_orders = result["orders"] or []

        for mirakl_sale_order in self._map_orders(imported_orders):
            if not self.env["sale.order"].search_count(
                [
                    ("channel_ids", "in", sale_channel.channel_id.id),
                    ("mirakl_code", "=", mirakl_sale_order.order_id),
                ]
            ):
                self._build_record(sale_channel, mirakl_sale_order)
