from odoo.addons.datamodel import fields
from odoo.addons.datamodel.datamodels.base import BaseDatamodel


class SaleOrderInvoiceDatamodel(BaseDatamodel):
    _name = "sale.order.invoice"

    date = fields.Date()
    number = fields.Str()
