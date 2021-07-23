#  Copyright (c) Akretion 2020
#  License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)
from odoo import _
from odoo.exceptions import MissingError, ValidationError
from odoo.http import request

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest.http import JSONEncoder as JSONEncoder
from odoo.addons.component.core import Component


class SaleImportService(Component):
    _inherit = "base.rest.service"
    _name = "sale.import.service"
    _usage = "sale"
    _collection = "sale.import.rest.services"
    _description = """
        Sale Import services

        Allows asynchronous import of Sale Orders and returns

        editable chunk IDs
    """

    def _get_channel(self):
        key = self._get_api_key()
        api_key = self.env["auth.api.key"]._retrieve_api_key(key)
        return self.env["sale.channel"].search([("api_key_id", "=", api_key.id)])

    @restapi.method(
        [(["/", "/create"], "POST")],
        input_param=restapi.Datamodel("sale.import.input"),
        output_param=restapi.Datamodel("sale.import.output"),
        auth="api_key",
    )
    # pylint: disable=W8106
    def create(self, sale_import_input):
        channel = self._get_channel()
        json_encoder = JSONEncoder()
        if not channel:
            raise ValidationError(_("API key does not map to any sale channel"))
        vals = [
            {
                "usage": "json_import",
                "apply_on_model": "sale.order",
                "data_str": json_encoder.encode(sale_order),
                "model_name": "sale.channel",
                "record_id": channel.id,
            }
            for sale_order in sale_import_input.dump()["sale_orders"]
        ]
        chunks = self.env["queue.job.chunk"].create(vals)
        output = self.env.datamodels["sale.import.output"].load(
            {"chunk_ids": chunks.ids}
        )
        return output

    def _get_openapi_default_parameters(self):
        defaults = super()._get_openapi_default_parameters()
        defaults.append(
            {
                "name": "API-KEY",
                "in": "header",
                "description": "Auth API key",
                "required": True,
                "schema": {"type": "string"},
                "style": "simple",
            }
        )
        return defaults

    def _get_api_key(self):
        headers = request.httprequest.environ
        return headers.get("HTTP_API_KEY")

    @restapi.method(
        [(["/cancel"], "POST")],
        input_param=restapi.Datamodel("sale.cancel.input"),
        output_param=restapi.Datamodel("sale.cancel.output"),
        auth="api_key",
    )
    def cancel(self, sale_cancel_input):
        channel = self._get_channel()
        name = sale_cancel_input.sale_name
        sale = self.env["sale.order"].search(
            [("client_order_ref", "=", name), ("sale_channel_id", "=", channel.id)]
        )
        if sale:
            sale.action_cancel()
            return self.env.datamodels["sale.cancel.output"].load({"success": True})
        else:
            raise MissingError(_("Sale order {} does not exist").format(name))
