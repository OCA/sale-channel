# Copyright 2023 Akretion (https://www.akretion.com).
# @author Raphaël Reverdy<raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import fields, models


class SeBackend(models.Model):
    _inherit = "se.backend"

    sale_channel_id = fields.One2many(
        # is a one2one relation
        comodel_name="sale.channel",
        inverse_name="search_engine_id",
    )
