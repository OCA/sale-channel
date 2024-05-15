import logging

from odoo import models

_logger = logging.getLogger(__name__)


class MiraklSaleOrderLineImporter(models.Model):
    _name = "mirakl.sale.order.line.importer"
    _description = "sale order line importer"
    _inherit = "mirakl.importer"

    def _create_record(self, binding_model, odoo_data):
        return self.env[binding_model].new(odoo_data)
