from odoo import fields, models


class ProductTemplateSaleChannelRel(models.Model):
    _inherit = "product.template.sale.channel.rel"

    mirakl_code = fields.Char()
