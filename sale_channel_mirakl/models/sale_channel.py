from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import split_every

MIRAKL = "mirakl"


class SaleChannel(models.Model):
    _inherit = "sale.channel"

    mirakl_channel_ids = fields.One2many(
        comodel_name="sale.channel.mirakl",
        inverse_name="channel_id",
        string="Mirakl Sale Channels",
    )

    max_items_to_export = fields.Integer(
        default=100,
        help="defines the maximum number of elements that can be exported. "
        "If <=0, we export all the items linked to the channel at once. "
        "Otherwise, we will do several exports in batches of 'max_items_to_export' each",
    )

    channel_type = fields.Selection(selection_add=[(MIRAKL, "Mirakl Sale Channel")])

    pricelist_ids = fields.Many2many(comodel_name="product.pricelist")

    @api.constrains("mirakl_channel_ids")
    def _check_uniqueness(self):
        for record in self:
            if len(record.mirakl_channel_ids) > 1:
                raise ValidationError(
                    _(
                        "Only one SaleChannelMirakl can be linked to each SaleChannel record"
                    )
                )

    def _get_struct_to_export(self):
        if self.channel_type == MIRAKL:
            for channel in self.mirakl_channel_ids:
                yield channel.data_to_export
        else:
            super()._get_struct_to_export()

    def split_products(self, products):
        """
        constructs a list of product lists whose length of e
        ach sublist depends on a given parameter.
        This is to avoid launching the export of too many products at once.
        :param products: list of products to split
        :return: A generator that returns each sublist of products one by one
        """
        return split_every(self.max_items_to_export, products)

    def _get_items_to_export(self, struct_key):
        if self.channel_type == MIRAKL:
            products = self.env["product.product"].search(
                [("product_tmpl_id.channel_ids", "in", self.id)]
            )
            products_list = self.split_products(products)  # List of lists of products
            return products_list

        return super()._get_items_to_export(struct_key)

    def _map_items(self, struct_key, items):
        if self.channel_type == MIRAKL:
            for item in self.mirakl_channel_ids._map_items(struct_key, items):
                yield item
        else:
            super()._map_items(struct_key, items)

    def _trigger_export(self, struct_key, pydantic_items):
        if self.channel_type == MIRAKL:
            mirakl_channel = self.mirakl_channel_ids.filtered(
                lambda r: r.data_to_export == struct_key
            )
            return mirakl_channel._export_data(pydantic_items)

        return super()._trigger_export(struct_key, pydantic_items)

    def _get_struct_to_import(self):
        if self.channel_type == MIRAKL:
            for record in self.mirakl_channel_ids:
                yield record.data_to_import
        else:
            super()._get_struct_to_import()

    def _job_trigger_import(self, struct_key):
        if self.channel_type == MIRAKL:
            mirakl_channel = self.mirakl_channel_ids.filtered(
                lambda x: x.data_to_import == struct_key
            )
            return mirakl_channel._import_data(struct_key)
        return super()._job_trigger_import(struct_key)
