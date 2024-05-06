from odoo import models


class ProductTemplateSaleChannelRel(models.Model):
    _name = "product.template.sale.channel.rel"
    _inherit = ["sale.channel.relation", _name]
