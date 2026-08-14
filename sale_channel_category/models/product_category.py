# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductCategory(models.Model):
    _inherit = ["product.category", "sale.channel.owner"]
    _name = "product.category"

    channel_ids = fields.Many2many(
        "sale.channel",
        string="Sale Channel",
        store=True,
        compute="_compute_channel_ids",
        readonly=False,
        recursive=True,
    )

    @api.depends("parent_id.channel_ids")
    def _compute_channel_ids(self):
        for record in self:
            if record.parent_id:
                record.channel_ids = record.parent_id.channel_ids
                if not isinstance(record.id, models.NewId):
                    # skip onchange
                    record._on_sale_channel_modified()
