import hashlib
import logging

from pydantic import BaseModel

from odoo import fields, models, tools

from ..mirakl_mapper.mirakl_billing_address import MiraklBillingAddress
from ..mirakl_mapper.mirakl_customer import MiraklCustomer
from ..mirakl_mapper.mirakl_sale_order import MiraklSaleOrder
from ..mirakl_mapper.mirakl_sale_order_line import MiraklSaleOrderLine
from ..mirakl_mapper.mirakl_shipping_address import MiraklShippingAddress
from .sale_channel_owner import SaleChannelOwner

_logger = logging.getLogger(__name__)


class MiraklImporter(models.AbstractModel):
    _name = "mirakl.importer"
    _description = "import record from mirakl"

    def _build_dependencies(self, sale_channel, mirakl_record):
        """
        Allows you to construct the dependencies of an object.
         These dependencies are also objects
        :param sale_channel: channel on which the object is attached
        :param mirakl_record: the object whose dependencies we want to build
        """
        for attr in mirakl_record.model_fields_set:
            attributes = getattr(mirakl_record, attr)

            if isinstance(attributes, BaseModel):
                attributes = [attributes]

            if isinstance(attributes, list) and all(
                isinstance(item, BaseModel) for item in attributes
            ):
                for item in attributes:
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
            MiraklCustomer: "mirakl.res.partner.importer",
            MiraklBillingAddress: "mirakl.res.partner.importer",
            MiraklShippingAddress: "mirakl.res.partner.importer",
            MiraklSaleOrder: "mirakl.sale.order.importer",
            MiraklSaleOrderLine: "mirakl.sale.order.line.importer",
        }
        return importers

    def _map_record(self, sale_channel, mirakl_record):
        return mirakl_record.odoo_model_dump(sale_channel)

    def _after_binding(self, record, sale_channel, external_id):
        """
        Add sale_channel_external_code and sale_channel_sync_date
        on the relation between record and channel
        :param record: Odoo record to update
        :param sale_channel: channel linked to the record
        :param external_id: external id used to update record
        """
        now_fmt = fields.Datetime.now()
        if SaleChannelOwner._name in record._inherit:
            relation = record._fields.get("channel_ids").relation
            model_name = relation.replace("_", "%")
            models_candidate = self.env["ir.model"].search(
                [("model", "ilike", model_name)]
            )
            model = fields.first(
                models_candidate.filtered(
                    lambda m, r=relation: m.env[m.model]._table == r
                )
            )
            if model:
                TargetModel = self.env[model.model]
                relation_field_record = [
                    k
                    for k, f in TargetModel._fields.items()
                    if f.comodel_name == record._name
                ]
                relation_field_channel = [
                    k
                    for k, f in TargetModel._fields.items()
                    if f.comodel_name == sale_channel.channel_id._name
                ]
                if len(relation_field_record) == 1 and len(relation_field_channel) == 1:

                    domain = [
                        (relation_field_record[0], "=", record.id),
                        (relation_field_channel[0], "=", sale_channel.channel_id.id),
                    ]
                    binding = TargetModel.search(domain, limit=1)
                    binding.write(
                        {
                            "sale_channel_external_code": tools.ustr(external_id),
                            "sale_channel_sync_date": now_fmt,
                        }
                    )
                    record._compute_external_code()
                    record._compute_sync_date()

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

    def _update_record(self, binding, odoo_data):
        binding.write(odoo_data)

    def _create_record(self, binding_model, odoo_data):
        return self.env[binding_model].create(odoo_data)

    def create_or_update_record(self, sale_channel, mirakl_record):
        """
        Allows you to create or update an odoo record from
         the corresponding imported Mirakl object
        :param sale_channel: channel on which the record is attached
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
        self._after_binding(binding, sale_channel, mirakl_id)
        self._after_import(binding)
        return binding
