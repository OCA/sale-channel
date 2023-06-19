# Copyright 2023 Akretion (https://www.akretion.com).
# @author Raphaël Reverdy<raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = ["product.template"]

    channel_categ_ids = fields.Many2many(
        comodel_name="product.category",
        compute="_compute_channel_categ_ids",
        string="Channel categories",
        help="All direct categories of the channel",
        readonly=True,
    )

    def _get_categories(self):
        # use product-multi-category
        self.ensure_one()
        return self.categ_id + self.categ_ids

    @api.depends_context("channel_id")
    def _compute_channel_categ_ids(self):
        """filter direct category with
        children of the root categ of the channel
        """
        channel_id = self.env["sale.channel"].browse(
            self.env.context.get("channel_id", 0)
        )
        root_categ = channel_id.root_category_id
        if not channel_id:
            self.channel_categ_ids = self.channel_categ_ids.browse(0)
            return

        for rec in self:
            categs = self.env["product.category"].browse()
            for categ in rec._get_categories():
                if f"/{root_categ.id}/" in f"/{categ.parent_path}":
                    categs |= categ
            rec.channel_categ_ids = categs
