from odoo import models

from .sale_channel import MIRAKL


class SaleChannelOwner(models.AbstractModel):

    _inherit = "sale.channel.owner"

    def _import_batch(self, sale_channel, filters):
        if sale_channel.channel_id.channel_type == MIRAKL:
            return self.env["mirakl.sale.order.importer"]._import_sale_orders_batch(
                sale_channel, filters
            )
        else:
            return super()._import_batch(sale_channel, filters)
