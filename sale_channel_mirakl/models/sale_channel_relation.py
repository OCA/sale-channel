from odoo import fields, models


class SaleChannelRelation(models.AbstractModel):
    _name = "sale.channel.relation"
    _description = "RElation between sale channel and other model"

    mirakl_code = fields.Char()
