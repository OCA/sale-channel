# Copyright 2023 Akretion (https://www.akretion.com).
# @author Raphaël Reverdy<raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductCategory(models.Model):
    _inherit = ["product.category", "sale.channel.owner"]
    _name = "product.category"

    sequence = fields.Integer(help="Determine the display order", index=True)

    channel_ids = fields.One2many(
        comodel_name="sale.channel",
        inverse_name="root_category_id",
        help="Only if category is root of channel",
    )

    level = fields.Integer(
        compute="_compute_level",
        help="Number of categories up to the channel's root category",
        readonly=True,
    )

    categs_up_to_root = fields.Many2many(
        "product.category",
        compute="_compute_path_to_root_channel",
        help="All the categories in the path including self",
        store=False,
        readonly=True,
    )

    channel_parent_categ_id = fields.Many2one(
        "product.category",
        compute="_compute_path_to_root_channel",
        store=False,
        readonly=True,
    )

    channel_child_categ_ids = fields.One2many(
        "product.category",
        compute="_compute_path_to_root_channel",
        store=False,
        readonly=True,
    )

    @api.depends_context("channel_id")
    def _compute_path_to_root_channel(self):
        channel_id = self.env["sale.channel"].browse(
            self.env.context.get("channel_id", 0)
        )

        if not channel_id:
            self.categs_up_to_root = self.browse(0)
            self.channel_parent_categ_id = self.browse(0)
            self.channel_child_categ_ids = self.browse(0)
            return

        root = channel_id.root_category_id
        needle = f"/{root.id}/"

        for rec in self:
            start = f"/{rec.parent_path}".find(needle)
            if start == -1:  # not found
                rec.categs_up_to_root = self.browse(0)
                rec.channel_parent_categ_id = self.browse(0)
                rec.channel_child_categ_ids = self.browse(0)
            else:
                # +1: to remove the first / of the path
                # :-1 to remove the last / of the path
                results = f"/{rec.parent_path}"[start + 1 : -1].split("/")
                rec.categs_up_to_root = self.browse([int(r) for r in results])

                # if parent_id may be outside the root if we are the root
                if rec == root:
                    rec.channel_parent_categ_id = self.browse(0)
                else:
                    rec.channel_parent_categ_id = rec.parent_id

                # if we are on the channel, so is our children
                rec.channel_child_categ_ids = rec.child_id

    @api.depends_context("channel_id")
    def _compute_level(self):
        """Count the number of categories up to the sale channel's root category.

        Quicker than len(categs_up_to_root) because no recursive browse()
        """
        channel_id = self.env["sale.channel"].browse(
            self.env.context.get("channel_id", 0)
        )
        if not channel_id:
            self.level = 0
            return
        root = channel_id.root_category_id
        needle = f"/{root.id}/"
        for rec in self:
            # add starting "/" to normalize search
            start = f"/{rec.parent_path}".find(needle) + len(needle)
            if start == -1 + len(needle):  # not found
                rec.level = 0
            else:
                rec.level = f"/{rec.parent_path}"[start:].count("/")
