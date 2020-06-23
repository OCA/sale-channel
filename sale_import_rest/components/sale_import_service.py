#  Copyright (c) Akretion 2020
#  License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)
from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component


class SaleImportService(Component):
    _inherit = "base.rest.service"
    _name = "sale.import.service"
    _usage = "import"
    _collection_name = "sale.import.endpoints"
    _default_auth = "public"

    def create(
        self, api_key, sale_order_data, **params
    ):  # pylint: disable=method-required-super
        api_key_id = self.env["auth.api.key"]._retrieve_api_key(api_key)
        sale_channel = self.env["sale.channel"].search(
            [("api_key", "=", api_key_id.id)]
        )
        if not sale_channel:
            raise ValidationError(_("API key does not map to any sale channel"))
        vals = [
            {
                "usage": "json_import",
                "apply_on_model": "sale.order",
                "data_str": data_str,
                "model_name": "sale.channel",
                "record_id": sale_channel.id,
            }
            for data_str in sale_order_data
        ]
        chunk_ids = self.env["queue.job.chunk"].create(vals)
        return {"response": chunk_ids.ids}
