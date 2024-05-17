from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

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
        struct_keys = super()._get_struct_to_export()
        if self.channel_type == MIRAKL:
            struct_keys.extend([c.data_to_export for c in self.mirakl_channel_ids])
        return struct_keys

    def _get_items_to_export(self, struct_key):
        if self.channel_type == MIRAKL:
            yield from self._get_items_to_export_mirakl_product()

        return super()._get_items_to_export(struct_key)

    def _get_items_to_export_mirakl_product(self):
        domain = [("product_tmpl_id.channel_ids", "in", self.id)]
        if self.max_items_to_export <= 0:
            products = self.env["product.product"].search(domain)
            yield products
        else:
            products = self.env["product.product"].search(
                domain, limit=self.max_items_to_export
            )
            already_loaded = self.max_items_to_export
            while products:
                yield products
                products = self.env["product.product"].search(
                    domain, limit=self.max_items_to_export, offset=already_loaded
                )
                already_loaded += self.max_items_to_export

    def _map_items(self, struct_key, items):
        if self.channel_type == MIRAKL:
            for item in self.mirakl_channel_ids._map_items(struct_key, items):
                yield item
        else:
            return super()._map_items(struct_key, items)

    def _trigger_export(self, struct_key, pydantic_items):
        if self.channel_type == MIRAKL:
            mirakl_channel = self.mirakl_channel_ids.filtered(
                lambda r: r.data_to_export == struct_key
            )
            return mirakl_channel._export_data(pydantic_items)
        return super()._trigger_export(struct_key, pydantic_items)

    def _get_struct_to_import(self):
        struct_keys = super()._get_struct_to_import()
        if self.channel_type == MIRAKL:
            struct_keys.extend(
                record.data_to_import for record in self.mirakl_channel_ids
            )
        return struct_keys

    def _job_trigger_import(self, struct_key):
        if self.channel_type == MIRAKL:
            mirakl_channel = self.mirakl_channel_ids.filtered(
                lambda x: x.data_to_import == struct_key
            )
            return mirakl_channel._import_data(struct_key)
        return super()._job_trigger_import(struct_key)
