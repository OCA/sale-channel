from odoo import fields, models


class MiraklBinding(models.AbstractModel):
    _name = "mirakl.binding"
    _description = "used to attache several items to mirakl sale channel"

    mirakl_id = fields.Char()
    is_from_mirakl = fields.Boolean()
