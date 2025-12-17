#  Copyright (c) Akretion 2020
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)
import datetime
import json

from odoo import _, models
from odoo.exceptions import MissingError, ValidationError


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):  # pylint: disable=E0202,arguments-differ
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, datetime.date):
            return obj.isoformat()
        return super(JSONEncoder, self).default(obj)


class SaleImportService(models.AbstractModel):
    _name = "sale.import.service.sale"
    _description = "Sale Import Service Sale"

    def _get_channel(self):
        return self.env["sale.channel"].browse(self._context["channel_id"])

    def create_payload(self, sale_orders):
        channel = self._get_channel()
        if not channel:
            raise ValidationError(_("API key does not map to any sale channel"))
        vals_list = [
            {
                "data_str": json.dumps(
                    sale_order, cls=JSONEncoder, sort_keys=True, indent=4
                ),
                "sale_channel_id": channel.id,
            }
            for sale_order in sale_orders
        ]
        return self.env["sale.import.payload"].sudo().create(vals_list)

    def cancel(self, name):
        self = self.sudo()
        channel = self._get_channel()
        sale = self.env["sale.order"].search(
            [("client_order_ref", "=", name), ("sale_channel_id", "=", channel.id)]
        )
        if sale:
            return sale.action_cancel()
        else:
            raise MissingError(_("Sale order {} does not exist").format(name))
