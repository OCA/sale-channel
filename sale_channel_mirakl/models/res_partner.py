from odoo import fields, models


class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = [_name, "mirakl.binding", "sale.channel.owner"]

    channel_ids = fields.Many2many(
        comodel_name="sale.channel",
        relation="res_partner_sale_channel_rel",
        column1="res_partner_id",
        column2="sale_channel_id",
    )

    res_partner_sale_channel_ids = fields.One2many(
        comodel_name="res.partner.sale.channel.rel",
        inverse_name="res_partner_id",
    )
