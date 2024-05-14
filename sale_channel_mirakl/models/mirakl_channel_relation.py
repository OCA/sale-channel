from odoo import fields, models


class MiraklChannelRelation(models.AbstractModel):
    _name = "mirakl.channel.relation"
    _description = "Relation between sale channel and other model"

    mirakl_code = fields.Char(
        compute="_compute_mirakl_codessssss",
        store=True,
    )

    sync_date = fields.Datetime(
        compute="_compute_sync_date",
        store=True,
    )
