# Copyright 2023 Akretion (https://www.akretion.com).
# @author Raphaël Reverdy<raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SeBinding(models.Model):
    _inherit = "se.binding"

    channel_id = fields.Many2one("sale.channel", compute="_compute_sale_channel")

    def _compute_sale_channel(self):
        for rec in self:
            rec.channel_id = rec.backend_id.sale_channel_id

    def _contextualize(self, record):
        res = super()._contextualize(record)
        return res.with_context(channel_id=res.channel_id.id)
