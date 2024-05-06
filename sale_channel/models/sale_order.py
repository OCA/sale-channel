#  Copyright (c) Akretion 2020
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

from odoo import Command, models


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = [_name, "sale.channel.owner"]

    # A sale order will only be linked to one and only one sale channel

    def _prepare_invoice(self):
        res = super()._prepare_invoice()
        res["channel_ids"] = [Command.set(self.channel_ids.ids)]

        return res
