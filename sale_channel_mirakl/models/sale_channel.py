from odoo import fields, models

MIRAKL = "mirakl"


class SaleChannel(models.Model):
    _inherit = "sale.channel"

    binded_product_ids = fields.Many2many(
        comodel_name="product.template",
        relation="product_template_sale_channel_rel",
        column1="sale_channel_id",
        column2="product_template_id",
        string="Binded Products",
    )

    channel_type = fields.Selection(selection_add=[(MIRAKL, "Mirakl Sale Channel")])

    mirakl_channel_ids = fields.One2many(
        comodel_name="sale.channel.mirakl",
        inverse_name="channel_id",
        string="Mirakl Sale Channels",
    )

    def _scheduler_export(self):
        mirakl_records = self.filtered(lambda r: r.channel_type == MIRAKL)
        others_records = self - mirakl_records
        for record in mirakl_records:
            products = self.env["product.product"].search(
                [("product_tmpl_id.channel_ids", "in", record.id)]
            )
            record.mirakl_channel_ids._export_data(products)
        return super(SaleChannel, others_records)._scheduler_export()

    def _scheduler_import_sale_order(self, filters=None):
        mirakl_records = self.filtered(lambda r: r.channel_type == MIRAKL)
        others_records = self - mirakl_records
        for record in mirakl_records:
            record._import_sale_orders(filters)
        return super(SaleChannel, others_records)._scheduler_import_sale_order(filters)

    def action_view_binded_products(self):

        action = self.env.ref("mirakl_connector.action_view_binded_products").read()[0]
        action["domain"] = [("id", "in", self.binded_product_ids.ids)]
        return action
