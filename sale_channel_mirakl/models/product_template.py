from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    prod_sale_channel_ids = fields.One2many(
        comodel_name="product.template.sale.channel.rel",
        inverse_name="product_template_id",
    )
