from odoo import fields, models


class MiraklChannelRelation(models.AbstractModel):
    _name = "mirakl.channel.relation"
    _description = "Relation between sale channel and other model"

    mirakl_code = fields.Char()

    sync_date = fields.Datetime()
