from odoo import models


class ProductTemplateSaleChannelRel(models.Model):
    _name = "product.template.sale.channel.rel"
    _inherit = ["mirakl.channel.relation", _name]
