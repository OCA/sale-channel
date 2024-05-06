import logging

from odoo import fields, models, tools

_logger = logging.getLogger(__name__)


class MiraklResPartnerImporter(models.Model):
    _name = "mirakl.res.partner.importer"
    _inherit = "mirakl.importer"

    def _get_binding(self, sale_channel, external_id, binding_model):
        binding = self.env[binding_model].search(
            [
                ("mirakl_code", "=", tools.ustr(external_id)),
                ("channel_ids", "in", sale_channel.channel_id.id),
            ],
            limit=2,
        )

        if len(binding) > 1:
            _logger.warning("there are many records linked to the same mirakl record")
            binding = fields.first(binding)
        return binding
