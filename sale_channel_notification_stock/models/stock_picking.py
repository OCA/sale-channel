# Copyright 2026 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _send_confirmation_email(self):
        # Only send regular notifications if no channel is configured
        return super(
            StockPicking,
            self.filtered(
                lambda picking: (
                    not (
                        picking.picking_type_id.code == "outgoing"
                        and picking.move_ids.mapped(
                            "sale_line_id.order_id.sale_channel_id"
                        ).filtered(lambda x: x.custom_notifications)
                    )
                )
            ),
        )._send_confirmation_email()

    def _compute_state(self):
        picking_states = {
            pick.id: pick.state
            for pick in self.filtered(
                lambda pick: pick.picking_type_id.code == "outgoing"
            )
        }

        rv = super()._compute_state()

        for record in self:
            old_state = picking_states.get(record.id)
            print(record.state, old_state)
            if (
                record.state == "assigned" and old_state not in ["assigned", "done"]
            ) or (record.state == "done" and old_state != "done"):
                sale_channel = record.move_ids.mapped(
                    "sale_line_id.order_id.sale_channel_id"
                ).filtered(lambda channel: channel.custom_notifications)

                if sale_channel:
                    sale_channel[0]._send_notification(
                        {
                            "assigned": "outgoing_picking_ready",
                            "done": "outgoing_picking_shipped",
                        }[record.state],
                        record,
                    )
        return rv
