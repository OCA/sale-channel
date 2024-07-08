# Copyright 2024 Akretion (http://www.akretion.com).
# @author Mathieu DELVA <mathieu.delva@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .common import Common


class TestSaleOrder(Common):
    def test_onchange_carrier_id(self):
        carrier_id = self.env.ref("delivery.free_delivery_carrier")
        self.order_id.action_confirm()
        picking_id = self.order_id.picking_ids
        picking_id.carrier_id = carrier_id
        picking_id.onchange_carrier_id()

        mail_id = self.env["mail.mail"].search(
            [("model", "=", "stock.picking"), ("res_id", "=", picking_id.id)]
        )

        self.assertTrue(mail_id)
