import hashlib
import logging

from odoo import fields, models, tools

from ..mirakl_mapper.mirakl_billing_address import MiraklBillingAddress
from ..mirakl_mapper.mirakl_sale_order import MiraklSaleOrder
from ..mirakl_mapper.mirakl_shipping_address import MiraklShippingAddress

_logger = logging.getLogger(__name__)


class MiraklImporter(models.AbstractModel):
    _name = "mirakl.importer"
    _description = "import record from mirakl"

    def _build_dependencies(self, sale_channel, mirakl_record):

        importer_name = self._get_importers().get(type(mirakl_record))
        importer = self.env[importer_name]

        try:
            binding = importer._get_binding(sale_channel, mirakl_record)
        except NotImplementedError:
            binding = None

        if not binding:
            importer.create_or_update_record(
                sale_channel, mirakl_record, recursion=True
            )
        return None

    def _get_binding(self, sale_channel, mirakl_record):
        """
        returns the odoo object attached to the external object whose id is 'external_id'
        """
        raise NotImplementedError("Something is missing here")

    def _get_importers(self):
        importers = {
            MiraklBillingAddress: "mirakl.res.partner.importer",
            MiraklShippingAddress: "mirakl.res.partner.importer",
            MiraklSaleOrder: "mirakl.sale.order.importer",
        }
        return importers

    def _map_record(self, mirakl_pydantic_object):
        return self.env["sale.channel.mirakl"]._map_to_odoo_record(
            mirakl_pydantic_object
        )

    def attach_record(
        self, external_id, binding, binding_model
    ):  # from odoo.addons.connector.components.binder.py
        """Create the link between an external ID and an Odoo ID

        :param external_id: external id to bind
        :param binding: Odoo record to bind
        :type binding: int
        """
        # Prevent False, None, or "", but not 0
        assert (
            external_id or external_id == 0
        ) and binding, "external_id or binding missing, " "got: %s, %s" % (
            external_id,
            binding,
        )
        # avoid to trigger the export when we modify the `external_id`
        now_fmt = fields.Datetime.now()
        if isinstance(binding, models.BaseModel):
            binding.ensure_one()
        else:
            binding = self.env[binding_model].browse(binding)
        binding.with_context(connector_no_export=True).write(
            {
                "mirakl_code": tools.ustr(external_id),
                "sync_date": now_fmt,
            }
        )

    def _after_import(self, binding):
        return

    def _generate_hash_key(self, customer):
        """
        This method is used to generate a key from customer not identified
        on Mirakl.
        The connector will generate one based on select data such as name,
        and city. Used principally when the is imported
        """
        hashtring = "".join([customer.firstname, customer.lastname, customer.city])
        if not hashtring:
            return False
        hash_object = hashlib.sha1(hashtring.encode("utf8"))
        return hash_object.hexdigest()

    def create_or_update_record(self, sale_channel, mirakl_record, recursion=False):
        """

        :param mirakl_id: identifier of the record on Mirakl
        :param mirakl_data: data of the record on Mirakl
        """
        if not recursion:
            mirakl_id = mirakl_record.get_key()
            binding_model = mirakl_record._odoo_model
            if not mirakl_id:
                mirakl_id = self._generate_hash_key(mirakl_record)

            self._build_dependencies(sale_channel, mirakl_record)
        mapped_record = self._map_record(mirakl_record)

        try:
            binding = self._get_binding(sale_channel, mirakl_id, binding_model)
        except NotImplementedError:
            binding = None

        if binding:
            record = self._update_data(mapped_record)
            self._update_record(binding, record)
        else:

            binding = self._create_odoo_record(mapped_record, binding_model)

        self.attach_record(mirakl_id, binding, binding_model)
        self._after_import(binding)
