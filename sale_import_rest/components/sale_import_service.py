#  Copyright (c) Akretion 2020
#  License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)
from odoo.addons.component.core import Component


class SaleImportService(Component):
    _inherit = "base.rest.service"
    _name = "sale.import.service"
    _usage = "import"
    _collection_name = "sale.import.rest.services"
    _default_auth = "public"

    def create(self, **params):
        api_key = params.get("api_key")
        if not api_key:
            return {"response": "No API key given"}
        api_key_id = self.env["auth.api.key"].search([("api_key", "=", api_key)])
        if not api_key_id:
            return {"response": "Couldn't find a matching API key"}
        sale_channel = self.env["sale.channel"].search(
            [("api_key", "=", api_key_id.id)]
        )
        if not sale_channel:
            return {"response": "API key does not map to any sale channel"}
        payload = params.get("payload")
        if not payload:
            return {"response": "No payload found"}
        try:
            vals = [
                {
                    "usage": "json_import",
                    "apply_on_model": "sale.order",
                    "data_str": data_str,
                    "model_name": "sale.channel",
                    "record_id": sale_channel.id,
                }
                for data_str in payload
            ]
            chunk_ids = self.env["queue.job.chunk"].create(vals)
        except Exception as e:
            return {"response": "Error while trying to create jobs: %s" % str(e)}
        return {"response": chunk_ids.ids}

    def get(self, _id, message):
        return {"response": "Get is not supported"}

    def search(self, message):
        return {"response": "Search is not supported"}

    def update(self, _id, message):
        return {"response": "PUT is not supported"}

    def delete(self, _id):
        return {"response": "DELETE is not supported"}
