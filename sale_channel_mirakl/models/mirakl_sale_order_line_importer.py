import logging

from odoo import models

_logger = logging.getLogger(__name__)


class MiraklSaleOrderLineImporter(models.AbstractModel):
    _name = "mirakl.sale.order.line.importer"
    _description = "sale order line importer"
    _inherit = "mirakl.importer"

    def _create_record(self, binding_model, odoo_data):
        """
        this method has been overridden because contrary to the super class,
        we create the odoo record with a 'create' method which ensures that all the
        necessary fields are provided.

        Except for the creation of a sale order, it is imperative to have
        lines and for lines, you must have an id for the sale order except with a
        'new' method, we leave it to the ORM to create the order and its lines.
        each instance as it should be by attaching them to each other
        """
        return self.env[binding_model].new(odoo_data)
