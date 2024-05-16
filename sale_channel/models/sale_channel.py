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
        for record in self:
            for struct_key in record._get_struct_to_export():
                for items in record._get_items_to_export(struct_key):
                    description = "Export {} from {} whose id is {}".format(
                        items,
                        record.name,
                        record.id,
                    )
                    record.with_delay(description=description)._job_trigger_export(
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
        """
        NotImplementedError("Something is missing")

    def _map_items(self, struct_key, items):
        """
        Allows to map items before export
        :param struct_key: helps identify type of items
        to call the appropriate mapping
        :param items: list of items to map
        :return:
        """
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
    def _scheduler_import(self):
        for record in self:
            for struct_key in record._get_struct_to_import():
                description = "Import {} from {} whose id is {}".format(
                    struct_key,
                    record.name,
                    record.id,
                )
                record.with_delay(description=description)._job_trigger_import(
                    struct_key
                )

    def _get_struct_to_import(self):
        """Retrieves the item types to import"""
        NotImplementedError("Something is missing")

    def _job_trigger_import(self, struct_key):
        """
        Initiates the import of channel items
        :param struct_key: type of item to import
        """
        raise NotImplementedError("Something is missing")

    def _import_data(self, struct_key):
        """
        launches the import of items on the sales channel.
        this method is called when the channel dedicated
        to the import of data of type 'struct_key' is found
        """
        raise NotImplementedError("Nothing found to import")
