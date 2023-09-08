# Copyright 2023 Akretion (https://www.akretion.com).
# @author Raphaël Reverdy<raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleChannel(models.Model):
    _inherit = "sale.channel"

    product_catalog = fields.Many2one("product.catalog")

    def is_add_to_sol_authorized(self, product, **kwargs):
        # product_id should exist
        # return true or false if this product can add the product in so
        # inactive products are always exluded
        # not sellable products are always excluded
        # if you need to sell inactive product, make unarchive them before

        # this method is a basic check to limit data leak
        # if someone try to add an unauthorized product

        # is product in the catalog ?
        if self.product_catalog.id in product.product_catalog_ids.ids:
            return product.active and product.sale_ok
        else:
            return False
