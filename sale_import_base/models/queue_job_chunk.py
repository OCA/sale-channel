# Copyright 2022 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import fields, models


class QueueJobChunk(models.Model):
    _inherit = "queue.job.chunk"

    processor = fields.Selection(
        selection_add=[("sale_channel_importer", "Sale Channel Importer")]
    )

    def _get_processor(self):
        if self.processor == "sale_channel_importer":
            return self.env["sale.channel.importer"].new({"chunk_id": self.id})
        else:
            return super()._get_processor()
