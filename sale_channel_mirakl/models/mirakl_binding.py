from odoo import fields, models


class MiraklBinding(models.AbstractModel):
    _name = "mirakl.binding"
    _description = "used to attache several items to mirakl sale channel"

    is_from_mirakl = fields.Boolean()
