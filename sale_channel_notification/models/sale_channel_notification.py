# Copyright 2026 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Mathieu Delva <mathieu.delva@akretion.com>
# @author Florian Mounier <florian.mounier@akretion.com>
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
    model_id = fields.Many2one(
        "ir.model",
        "Model",
        required=True,
        compute="_compute_model_id",
        ondelete="cascade",
    )
    template_id = fields.Many2one(
        "mail.template",
        "Mail Template",
        required=True,
    )

    _sql_constraints = [
        (
            "sale_channel_notification_unique",
            "UNIQUE(sale_channel_id, notification_type)",
            "A notification type can only be set once per sale channel",
        )
    ]

    def _selection_notification_type(self):
        notifications = self._get_all_notification()
        return [(key, notifications[key]["name"]) for key in notifications]

    def _get_all_notification(self):
        return {
            "sale_confirmation": {
                "name": _("Sale Confirmation"),
                "model": "sale.order",
            },
        }

    @api.depends("notification_type")
    def _compute_model_id(self):
        for record in self:
            notifications = self._get_all_notification()
            record.model_id = (
                self.env["ir.model"].search(
                    [
                        (
                            "model",
                            "=",
                            notifications[record.notification_type]["model"],
                        )
                    ]
                )
                if record.notification_type
                else False
            )

    def send(self, record):
        self.ensure_one()
        self._send(record, **self._get_template_context())

    def _send(self, record, **kwargs):
        return self.sudo().template_id.with_context(**kwargs).send_mail(record.id)

    def _get_template_context(self):
        return {
            "notification_type": self.notification_type,
            "sale_channel": self.sale_channel_id,
        }
