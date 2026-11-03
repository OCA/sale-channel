# Copyright 2026 Akretion (https://www.akretion.com).
# @author Raphaël Reverdy <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import fields, models


class SaleChannel(models.Model):
    _inherit = "sale.channel"

    should_publish_root = fields.Boolean(
        help="If unchecked, root categories (without parent) are not "
        "published in the search engine, only their children are.",
    )

    def write(self, vals):
        res = super().write(vals)
        if "should_publish_root" in vals:
            self.env["product.category"].search(
                [("parent_id", "=", False), ("channel_ids", "in", self.ids)]
            )._on_sale_channel_modified()
        return res
