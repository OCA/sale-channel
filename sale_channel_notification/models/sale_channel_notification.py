# Copyright 2024 Akretion (https://www.akretion.com).
# @author Mathieu Delva <mathieu.delva@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools.translate import _


class SaleChannelNotification(models.Model):
    _name = "sale.channel.notification"

    sale_channel_id = fields.Many2one("sale.channel")
    notification_type = fields.Selection(
        selection="_selection_notification_type",
        required=True,
    )
    model_id = fields.Many2one("ir.model", "Model", required=True, ondelete="cascade")
    template_id = fields.Many2one("mail.template", "Mail Template", required=True)

    def _selection_notification_type(self):
        notifications = self._get_all_notification()
        return [(key, notifications[key]["name"]) for key in notifications]

    def _get_all_notification(self):
        return {
            "sale_confirmation": {
                "name": _("Sale Confirmation"),
                "model": "sale.order",
            },
            "picking_shipped": {
                "name": _("Picking Shipped"),
                "model": "stock.picking",
            },
        }

    @api.onchange("notification_type")
    def on_notification_type_change(self):
        self.ensure_one()
        notifications = self._get_all_notification()
        if self.notification_type:
            model = notifications[self.notification_type].get("model")
            if model:
                self.model_id = self.env["ir.model"].search([("model", "=", model)])
                return {"domain": {"model_id": [("id", "=", self.model_id.id)]}}
            else:
                return {"domain": {"model_id": []}}

    def send(self, record_id):
        self.ensure_one()
        return (
            self.sudo()
            .template_id.with_context(**self._get_template_context())
            .send_mail(record_id)
        )

    def _get_template_context(self):
        return {
            "notification_type": self.notification_type,
            "sale_channel": self.sale_channel_id,
        }
