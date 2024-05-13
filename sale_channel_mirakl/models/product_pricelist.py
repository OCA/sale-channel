from odoo import fields, models


class ProductPricelist(models.Model):
    _name = "product.pricelist"
    _inherit = [_name, "sale.channel.owner"]

    channel_ids = fields.Many2many(
        comodel_name="sale.channel", string="Binded Sale Channels"
    )
