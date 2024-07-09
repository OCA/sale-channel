# Copyright 2024 Akretion (https://www.akretion.com).
# @author Mathieu Delva <mathieu.delva@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        if "send_email" in self._context and self._context.get("send_email"):
            self.env.context = dict(self.env.context)
            self.env.context.pop("send_email")
        res = super().action_confirm()
        for record in self:
            if record.state != "draft" and record.sale_channel_id:
                record.sale_channel_id._send_notification("sale_confirmation", record)
        return res

    def _get_confirmation_template(self):
        return False
