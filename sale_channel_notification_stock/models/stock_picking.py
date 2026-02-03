# Copyright 2026 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _action_done(self):
        result = super()._action_done()
        for record in self:
            sale_channel = record.move_ids.mapped(
                "sale_line_id.order_id.sale_channel_id"
            ).filtered(lambda x: x.custom_notifications)

            if (
                record.picking_type_id.code == "outgoing"
                and record.date_done
                and sale_channel
            ):
                sale_channel[0]._send_notification("outgoing_picking_shipped", record)
        return result

    def _send_confirmation_email(self):
        # Only send regular notifications if no channel is configured
        return super(
            StockPicking,
            self.filtered(
                lambda picking: not (
                    picking.picking_type_id.code == "outgoing"
                    and picking.move_ids.mapped(
                        "sale_line_id.order_id.sale_channel_id"
                    ).filtered(lambda x: x.custom_notifications)
                )
            ),
        )._send_confirmation_email()
