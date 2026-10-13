# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class SaleChannel(models.Model):
    _inherit = "sale.channel"

    root_categ_ids = fields.Many2many(
        comodel_name="product.category",
        string="Root Categ",
        domain=[("parent_id", "=", False)],
    )

    def write(self, vals):
        if "root_categ_ids" in vals:
            root_categs = self.root_categ_ids
        res = super().write(vals)
        if "root_categ_ids" in vals:
            # Notify manually root categ (the computed field will notify the child)
            (root_categs | self.root_categ_ids)._on_sale_channel_modified()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        # Notify manually root categ (the computed field will notify the child)
        records.root_categ_ids._on_sale_channel_modified()
        return records
