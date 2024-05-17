from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    channel_ids = fields.Many2many(
        comodel_name="sale.channel",
        relation="sale_order_sale_channel_rel",
        column1="sale_order_id",
        column2="sale_channel_id",
    )

    sale_order_sale_channel_ids = fields.One2many(
        comodel_name="sale.order.sale.channel.rel",
        inverse_name="sale_order_id",
    )
