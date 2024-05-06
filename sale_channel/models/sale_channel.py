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
        [],
        help="Allows to use specific fields and actions" " for specific channel's type",
    )

    @abstractmethod
    def _scheduler_export(self):
        for struct_key in self._get_struct_to_export():
            for items in self._get_items_to_export(struct_key):
                description = "Export {} from {} whose id is {}".format(
                    items,
                    self.name,
                    self.id,
                )
                self.with_delay(description=description)._job_trigger_export(
                    struct_key, items
                )

    def _job_trigger_export(self, struct_key, items):
        """
        Performs the mapping of the data to be exported and launches the export
        :param struct_key: type of item to export
        :param items: items to export
        """
        mapped_items = self._map_items(struct_key, items)
        self._trigger_export(struct_key, mapped_items)

    def _get_struct_to_export(self):
        """
        Retrieves the item types to export
        :return: list of data types to export
        """
        return []

    def _map_items(self, struct_key, items):
        return []

    @abstractmethod
    def _get_items_to_export(self, struct_key):
        """

        :param struct_key: type of data to export
        :return: A list of several lists of Odoo objects to export split
        according to a predefined size
        """
        raise NotImplementedError("Nothing found to export with %s" % struct_key)

    def _trigger_export(self, struct_key, mapped_items):
        """

        :param struct_key: type of data to export (allows you to know the appropriate channel
        to export this type of data that will need to be called)
        :param mapped_items: list of mapped items to export
        :return:
        """
        raise NotImplementedError("Something is missing")

    @abstractmethod
    def _scheduler_import(self, filters=None):
        for struct_key in self._get_struct_to_import():
            description = "Import {} from {} whose id is {}".format(
                struct_key,
                self.name,
                self.id,
            )
            self.with_delay(description=description)._job_trigger_import(
                struct_key, filters
            )

    def _get_struct_to_import(self):
        return []

    def _job_trigger_import(self, struct_key, filters):
        raise NotImplementedError("Something is missing")
