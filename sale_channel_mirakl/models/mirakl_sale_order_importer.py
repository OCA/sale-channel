import logging
from datetime import date, timedelta

from odoo import fields, models

_logger = logging.getLogger(__name__)
BINDING_MODEL = "sale.order"


class MiraklSaleOrderImporter(models.AbstractModel):
    _name = "mirakl.sale.order.importer"
    _description = "used to define specific methods for sale orders import"
    _inherit = "mirakl.importer"

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

    def build_record(self, sale_channel, external_id, mirakl_sale_order, binding_model):
        mirakl_sale_order = self._preprocess_address_emails(mirakl_sale_order)
        mirakl_sale_order = self._order_line_preprocess(
            mirakl_sale_order
        )  # order_line_process retourne NONE

        return self.env["mirakl.importer"].create_or_update_record(
            sale_channel, external_id, mirakl_sale_order, binding_model
        )

    def _import_record(
        self, sale_channel, mirakl_sale_order, job_options=None, **kwargs
    ):
        mirakl_id = mirakl_sale_order.order_id

        description = "Import sale order {} from Mirakl channel '{}'".format(
            mirakl_id,
            sale_channel.channel_id.name,
        )

        job_options = job_options or {}
        job_options.update({"description": description})
        self.with_delay(**job_options or {}).build_record(
            sale_channel, mirakl_id, mirakl_sale_order, BINDING_MODEL, **kwargs
        )

    def _call(self, sale_channel, api):
        url = "{}/{}".format(sale_channel.location, api)
        headers = {"Authorization": sale_channel.api_key}
        params = {"max": 100}
        return sale_channel._process_request(
            url, headers=headers, params=params, request_type="get"
        )

    def get_orders_data_from_mirakl(
        self, sale_channel, api, from_date=None, to_date=None, state=None
    ):
        from_date = (
            fields.Date.to_string(date.today() - timedelta(days=1))
            if not from_date
            else from_date
        )
        to_date = fields.Date.to_string(date.today()) if not to_date else to_date
        api = (
            f"{api}?start_date={from_date}&end_date={to_date}&order_state_codes={state}"
        )
        return self._call(sale_channel, api)

    def _after_import(self, binding):
        res = super()._after_import(binding)
        main_partner = binding.partner_id
        shipping_partner = binding.partner_shipping_id

        if main_partner not in (shipping_partner, shipping_partner.parent_id):
            data = {"type": "delivery", "parent_id": main_partner.id}
            shipping_partner.write(data)
        return res

    def _import_sale_orders_batch(self, sale_channel, filters):

        api = "api/orders"
        filters = filters if filters else {}

        from_date = filters.pop("from_date", None)
        to_date = filters.pop("to_date", None)
        state = filters.pop("state", "SHIPPING")
        result = self.get_orders_data_from_mirakl(
            sale_channel, api, from_date=from_date, to_date=to_date, state=state
        )
        orders_data = result["orders"] or []

        mirakl_sale_orders = sale_channel._make_mirakl_sale_order(orders_data)

        for mirakl_sale_order in mirakl_sale_orders:
            if not self.env["sale.order"].search_count(
                [
                    ("sale_channel_id", "=", sale_channel.channel_id.id),
                    ("mirakl_id", "=", mirakl_sale_order.order_id),
                ]
            ):
                self._import_record(sale_channel, mirakl_sale_order)
