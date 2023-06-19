# Copyright 2023 Akretion (https://www.akretion.com).
# @author Raphaël Reverdy<raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductCatalog(models.Model):
    _inherit = "product.catalog"

    channel_ids = fields.One2many(
        comodel_name="sale.channel",
        inverse_name="product_catalog",
    )
