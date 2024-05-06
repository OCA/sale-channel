from .mirakl_json import MiraklJson


class MiraklCatalog(MiraklJson):

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
    def get_additional_option_for_file(cls):
        return {"import_mode": "NORMAL", "with_products": "true"}

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
