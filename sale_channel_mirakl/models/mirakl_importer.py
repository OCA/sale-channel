import hashlib
import logging

from pydantic import BaseModel

from odoo import fields, models, tools

from ..mirakl_mapper.mirakl_billing_address import MiraklBillingAddress
from ..mirakl_mapper.mirakl_customer import MiraklCustomer
from ..mirakl_mapper.mirakl_sale_order import MiraklSaleOrder
from ..mirakl_mapper.mirakl_sale_order_line import MiraklSaleOrderLine
from ..mirakl_mapper.mirakl_shipping_address import MiraklShippingAddress

_logger = logging.getLogger(__name__)


class MiraklImporter(models.AbstractModel):
    _name = "mirakl.importer"
    _description = "import record from mirakl"

    def _build_dependencies(self, sale_channel, mirakl_record):
        for attr in mirakl_record.model_fields_set:
            attributes = getattr(mirakl_record, attr)

            if isinstance(attributes, BaseModel):
                attributes = [attributes]

            if isinstance(attributes, list) and all(
                isinstance(item, BaseModel) for item in attributes
            ):
                for item in attributes:
                    if isinstance(item, MiraklSaleOrderLine):
                        return None
                    importer_name = self._get_importers().get(type(item))
                    if importer_name:
                        importer = self.env[importer_name]
                        try:
                            binding = importer._get_binding(sale_channel, item)
                        except NotImplementedError:
                            binding = None
                        if not binding:
                            importer.create_or_update_record(sale_channel, item)
        return None

    def _get_binding(self, sale_channel, mirakl_record):
        """
        returns the odoo object attached to the external object whose id is 'external_id'
        """
        raise NotImplementedError("Something is missing here")

    def _get_importers(self):
        importers = {
            MiraklCustomer: "mirakl.customer.importer",
            MiraklBillingAddress: "mirakl.res.partner.importer",
            MiraklShippingAddress: "mirakl.res.partner.importer",
            MiraklSaleOrder: "mirakl.sale.order.importer",
            MiraklSaleOrderLine: "mirakl.sale.order.line.importer",
        }
        return importers

    def _map_record(self, sale_channel, mirakl_record):
        return mirakl_record.odoo_model_dump(sale_channel)

    def _after_binding(
        self, record, sale_channel, external_id
    ):  # from odoo.addons.connector.components.binder.py (bind())
        """Create the link between an external ID and an Odoo ID

        :param external_id: external id to bind
        :param binding: Odoo record to bind
        :type binding: int
        """
        # Prevent False, None, or "", but not 0
        # avoid to trigger the export when we modify the `external_id`
        now_fmt = fields.Datetime.now()
        if hasattr(record, "_name") and record._name == "sale.channel.owner":
            record._fields.get("channel_ids").relation
            # Check there is a (Odoo) model related to this relation table
            model_name = (
                ""  # a revoir--------------------------------------------------------
            )
            TargetModel = self.env[model_name]
            relation_fields_record = [
                f for f in TargetModel._fields.values() if f.comodel_name == self._name
            ]
            relation_fields_channel = [
                f
                for f in TargetModel._fields.values()
                if f.comodel_name == sale_channel._name
            ]
            if len(relation_fields_record) == 1 and len(relation_fields_channel) == 1:
                relation_field = relation_fields_record[0]
                relation_field_channel = relation_fields_channel[0]
                domain = [
                    (relation_field, "=", record.id),
                    (relation_field_channel, "=", sale_channel.id),
                ]
                binding = TargetModel.search(domain, limit=1)
                binding.write(
                    {
                        "mirakl_code": tools.ustr(external_id),
                        "sync_date": now_fmt,
                    }
                )

    def _after_import(self, sale_channel, binding, mirakl_record):
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

    def _update_record(self, binding, odoo_data):
        binding.write(odoo_data)

    def _create_record(self, binding_model, odoo_data):
        return self.env[binding_model].create(odoo_data)

    def create_or_update_record(self, sale_channel, mirakl_record):
        """

        :param mirakl_id: identifier of the record on Mirakl
        :param mirakl_record: the record who comes from Mirakl
        """
        mirakl_id = mirakl_record.get_key()
        binding_model = mirakl_record._odoo_model
        if not mirakl_id:
            mirakl_id = self._generate_hash_key(mirakl_record)

        self._build_dependencies(sale_channel, mirakl_record)

        try:
            binding = self._get_binding(sale_channel, mirakl_record)
        except NotImplementedError:
            binding = None
        odoo_data = self._map_record(sale_channel, mirakl_record)

        if binding:
            self._update_record(binding, odoo_data)
        else:
            binding = self._create_record(binding_model, odoo_data)
        mirakl_record._define_internal_id(binding.id)
        # self._after_binding(binding, sale_channel, mirakl_id)
        self._after_import(sale_channel, binding, mirakl_record)
        return binding
