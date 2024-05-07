from .mirakl_export_mapper import MiraklExportMapper


class MiraklCatalog(MiraklExportMapper):

    ean: str
    sku: str
    product_title: str
    product_description: str
    product_cat_code: str
    product_id: str
    product_id_type: str
    state: str

    @classmethod
    def map_item(cls, mirakl_channel, product):
        """

        :param mirakl_channel:
        :param product: product to map
        :return: a pydantic object corresponding to the form expected by mirakl
        """
        cat = product.categ_id.display_name or ""
        cat = cat.replace(
            "/", ">"
        )  # odoo puts "/" by default but mirakl expects ">" instead

        return cls(
            ean=product.barcode or "",
            sku=product.default_code or product.mirakl_id or "",
            product_title=product.name,
            product_description=product.description or product.name,
            product_cat_code=cat,
            product_id=product.barcode if product.barcode else product.default_code,
            product_id_type="EAN" if product.barcode else "SHOP_SKU",
            state="11",
        )

    @classmethod
    def get_file_header(cls):
        res = super().get_file_header()
        res.extend(
            [
                "sku",
                "ean",
                "PRODUCT_TITLE",
                "PRODUCT_DESCRIPTION",
                "PRODUCT_CAT_CODE",
                "product-id",
                "product-id-type",
                "state",
            ]
        )
        return res

    @classmethod
    def get_additional_options(cls):
        res = super().get_additional_options()
        res.update({"import_mode": "NORMAL", "with_products": "true"})
        return res

    def to_json(self):
        return {
            "sku": self.sku,
            "ean": self.ean,
            "PRODUCT_TITLE": self.product_title,
            "PRODUCT_DESCRIPTION": self.product_description,
            "PRODUCT_CAT_CODE": self.product_cat_code,
            "product-id": self.product_id,
            "product-id-type": self.product_id_type,
            "state": self.state,
        }
