#  Copyright (c) Akretion 2020
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)
from abc import abstractmethod

from odoo import fields, models


class SaleChannel(models.Model):
    _name = "sale.channel"
    _description = "Sale Channel"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)
    channel_type = fields.Selection(
        [], help="Allows to use specific fields and actions for specific channel's type"
    )

    @abstractmethod
    def _scheduler_export(self):
        pass

    @abstractmethod
    def _export_data(self, items):
        """
        Method to export items on sale channels
        :param items: list of items to export (May vary to each channel)
        :return:
        """

    @abstractmethod
    def _scheduler_import_sale_order(self, filters=None):
        pass

    @abstractmethod
    def _import_sale_orders(self, filters=None):
        """
        Method to import sales orders on sale channels
        """
