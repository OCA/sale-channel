from .mirakl_export_mapper import MiraklExportMapper


class MiraklOffer(MiraklExportMapper):

    sku: str
    product_id: str
    product_id_type: str
    state: str

    @classmethod
    def map_item(cls, mirakl_channel, product):
        relation_prod_channel = product.product_tmpl_id.prod_sale_channel_ids.filtered(
            lambda r: r.sale_channel_id == mirakl_channel.channel_id
        )
        return cls(
            sku=relation_prod_channel.sale_channel_external_code,
            product_id=product.barcode if product.barcode else product.default_code,
            product_id_type="EAN" if product.barcode else "SHOP_SKU",
            state="11",
        )

    @classmethod
    def get_file_header(cls):
        res = super().get_file_header()
        res.extend(["sku", "product-id", "product-id-type", "state"])
        return res

    @classmethod
    def get_additional_options(cls):
        res = super().get_additional_options()
        res.update({"import_mode": "NORMAL"})
        return res

    def to_json(self):
        return {
            "sku": self.sku,
            "product-id": self.product_id,
            "product-id-type": self.product_id_type,
            "state": self.state,
        }
