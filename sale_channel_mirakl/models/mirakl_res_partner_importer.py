import logging

from odoo import fields, models, tools

_logger = logging.getLogger(__name__)


class MiraklResPartnerImporter(models.Model):
    _name = "mirakl.res.partner.importer"
    _inherit = "mirakl.importer"

    def _get_binding(self, sale_channel, mirakl_record):
        external_id = mirakl_record.get_key()
        binding_model = mirakl_record._odoo_model

        if binding_model == "res.partner":
            binding = self.env[binding_model].search(
                [
                    (
                        "res_partner_sale_channel_ids.mirakl_code",
                        "=",
                        tools.ustr(external_id),
                    ),
                    ("channel_ids", "in", sale_channel.channel_id.id),
                ],
                limit=2,
            )

            if len(binding) > 1:
                _logger.warning(
                    "there are many records linked to the same mirakl record"
                )
                binding = fields.first(binding)
            return binding
        else:
            return super()._get_binding(sale_channel, mirakl_record)
