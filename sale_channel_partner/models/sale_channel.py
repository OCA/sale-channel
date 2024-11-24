#  Copyright (c) Akretion 2020
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)
from odoo import _, fields, models


class SaleChannel(models.Model):
    _inherit = "sale.channel"

    def _compute_count_sale_channel_partners(self):
        for rec in self:
            rec.count_sale_channel_partners = len(rec.sale_channel_partner_ids.ids)

    sale_channel_partner_ids = fields.One2many(
        "sale.channel.partner", "sale_channel_id", string="Sale Channel Partners"
    )
    count_sale_channel_partners = fields.Integer(
        string="Sale Channel Partner count",
        compute=_compute_count_sale_channel_partners,
    )

    def button_open_bindings(self):
        tree_view_id = self.env.ref(
            "sale_channel_partner.sale_channel_partner_view_tree"
        ).id
        act = {
            "name": _("Partner bindings"),
            "res_model": "sale.channel.partner",
            "type": "ir.actions.act_window",
            "views": [(tree_view_id, "tree")],
            "domain": [("sale_channel_id", "=", self.id)],
        }
        return act
