from odoo import fields, models


class SaleChannelRelation(models.AbstractModel):
    """
    all models representing the relationships between
    an odoo record and a sales channel must inherit it
    """

    _name = "sale.channel.relation"
    _description = "Relation between sale channel and other model"

    sale_channel_external_code = fields.Char(
        help="Unique code assigned to an object linked to the sales channel"
    )

    sale_channel_sync_date = fields.Datetime(
        help="Date of last import sync for the related record"
    )

    sale_channel_id = fields.Many2one(
        comodel_name="sale.channel", string="sale channel", required=True
    )
