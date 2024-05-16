from odoo import fields, models


class ResPartnerSaleChannelRel(models.Model):
    """
    Model representation of the relationship table between a res partner and a sales channel
    """

    _name = "res.partner.sale.channel.rel"
    _table = "res_partner_sale_channel_rel"
    _description = "Res partner sale channel Relation"
    _inherit = "sale.channel.relation"

    sale_channel_id = fields.Many2one("sale.channel", string="Sale Channel")

    res_partner_id = fields.Many2one("res.partner", string="Res Partner")
