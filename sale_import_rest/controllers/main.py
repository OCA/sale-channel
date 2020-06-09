#  Copyright (c) Akretion 2020
#  License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)
from odoo import _, http
from odoo.exceptions import ValidationError


class SaleImportBaseController(http.Controller):
    @http.route("/sale_order/post", type="json", auth="api_key", methods=["POST"])
    def main(self, **kw):
        sale_order_data = kw.get("sale_orders")
        api_key_id = http.request.get("auth_api_key_id")
        api_key_db_id = self.env["auth.api.key"].search(
            [("auth_api_key_id", "=", api_key_id)]
        )
        sale_channel = self.env["sale.channel"].search(
            [("api_key", "=", api_key_db_id.id)]
        )
        if not sale_channel:
            raise ValidationError(_("API key does not map to any sale channel"))
        sale_order_data["sale_channel"] = sale_channel.name
        job_ids = self.env["sale.order"].batch_process_json_imports(
            sale_order_data, sale_channel=sale_channel
        )
        return job_ids
