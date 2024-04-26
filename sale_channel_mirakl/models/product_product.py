from odoo import models


class ProductProduct(models.Model):
    _name = "product.product"
    _inherit = ["mirakl.binding", _name]
