# Copyright 2026 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timezone

from odoo import models


class SaleChannelImporter(models.TransientModel):
    _inherit = "sale.channel.importer"

    def _prepare_sale_vals(self, data):
        vals = super()._prepare_sale_vals(data)
        shipping = data.get("shipping")
        if not shipping:
            return vals
        vals.update(
            {
                "channel_carrier_code": shipping.get("carrier_code"),
                "channel_shipping_amount": shipping.get("amount") or 0.0,
            }
        )
        promised = shipping.get("promised_date")
        if promised:
            if promised.tzinfo:
                promised = promised.astimezone(timezone.utc).replace(tzinfo=None)
            vals["commitment_date"] = promised
        return vals

    def _platform_carrier_codes(self):
        """Codes of a shipping done by the channel itself: they never fall
        back to the default carrier of the channel."""
        return ()

    def _find_carrier(self, code):
        channel = self.payload_id.sale_channel_id
        carrier = self.env["delivery.carrier"]
        if code:
            carrier = carrier.search(
                [
                    ("sale_import_code", "=", code),
                    ("company_id", "in", [channel.company_id.id, False]),
                ],
                limit=1,
            )
        if carrier or (code or "").lower() in self._platform_carrier_codes():
            return carrier
        return channel.sale_import_carrier_id

    def _finalize(self, new_sale_order, raw_import_data):
        shipping = raw_import_data.get("shipping")
        if shipping:
            carrier = self._find_carrier(shipping.get("carrier_code"))
            if carrier:
                amount = 0.0
                if carrier.sale_import_charge_freight:
                    amount = shipping.get("amount") or 0.0
                self._set_shipping(new_sale_order, carrier, amount)
        return super()._finalize(new_sale_order, raw_import_data)

    def _set_shipping(self, sale_order, carrier, amount):
        if amount:
            sale_order.set_delivery_line(carrier, amount)
        else:
            sale_order.carrier_id = carrier
