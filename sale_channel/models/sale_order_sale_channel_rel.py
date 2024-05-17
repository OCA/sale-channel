from odoo import fields, models


class SaleOrderSaleChannelRel(models.Model):
    _name = "sale.order.sale.channel.rel"
    _table = "sale_order_sale_channel_rel"
    _inherit = "sale.channel.relation"
    _description = " sale order sale channel relation"

    sale_order_id = fields.Many2one(
        comodel_name="sale.order", string="sale order", required=True
    )

    _sql_constraints = [
        (
            "unique_sale_order_sale_channel",
            "unique(sale_channel_id, sale_order_id)",
            "The combination of Sale Channel and Sale Order must be unique",
        )
    ]
