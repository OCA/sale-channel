from odoo import fields, models


class SaleOrderSaleChannelRel(models.Model):
    _name = "sale.order.sale.channel.rel"
    _table = "sale_order_sale_channel_rel"
    _inherit = "sale.channel.relation"
    _description = " sale order sale channel relation"

    sale_channel_id = fields.Many2one(
        comodel_name="sale.channel", string="sale channel"
    )

    sale_order_id = fields.Many2one(comodel_name="sale.order", string="sale order")
