import logging

from odoo import fields, models, tools

_logger = logging.getLogger(__name__)


class MiraklCustomerImporter(models.Model):
    _name = "mirakl.customer.importer"
    _inherit = "mirakl.importer"
    _description = "Mirakl customer importer"

    def _build_dependencies(self, sale_channel, mirakl_record):
        """

        :param sale_channel:
        :param mirakl_record:
        :return:
        """
        customer = mirakl_record
        billing_partner_obj = customer.billing_address
        importer_billing_name = self._get_importers().get(type(billing_partner_obj))
        importer_billing = self.env[importer_billing_name]
        importer_billing._build_dependencies(
            sale_channel,
            billing_partner_obj,
        )
        shipping_partner_obj = customer.shipping_address
        importer_shipping_name = self._get_importers().get(type(shipping_partner_obj))
        importer_shipping = self.env[importer_shipping_name]
        importer_shipping._build_dependencies(
            sale_channel,
            shipping_partner_obj,
        )
        return super()._build_dependencies(sale_channel, mirakl_record)

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
