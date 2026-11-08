# Copyright 2026 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Mathieu Delva <mathieu.delva@akretion.com>
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        res = super().action_confirm()
        for record in self:
            if record.state == "sale" and record.sale_channel_id.custom_notifications:
                record.sale_channel_id._send_notification("sale_confirmation", record)
        return res

    def _send_order_confirmation_mail(self):
        # Only send regular notifications if no channel is configured
        return super(
            SaleOrder,
            self.filtered(lambda so: not so.sale_channel_id.custom_notifications),
        )._send_order_confirmation_mail()
