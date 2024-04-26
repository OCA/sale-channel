# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = ["product.template", "sale.channel.owner"]
    _name = "product.template"

    channel_ids = fields.Many2many(
        comodel_name="sale.channel",
        relation="product_template_sale_channel_rel",
        column1="product_template_id",
        column2="sale_channel_id",
    )
