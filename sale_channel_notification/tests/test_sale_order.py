# Copyright 2024 Akretion (http://www.akretion.com).
# @author Mathieu DELVA <mathieu.delva@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .common import Common


class TestSaleOrder(Common):
    def test_action_confirm(self):
        self.order_id.action_confirm()
        mail_id = self.env["mail.mail"].search(
            [("model", "=", "sale.order"), ("res_id", "=", self.order_id.id)]
        )
        self.assertTrue(mail_id)
