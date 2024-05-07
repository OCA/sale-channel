from typing import List

from .mirakl_commission_tax import MiraklCommissionTax
from .mirakl_import_mapper import MiraklImportMapper


class MiraklSaleOrderLine(MiraklImportMapper):
    can_refund: str
    cancelations: List[str]
    category_code: str
    category_label: str
    commission_fee: float
    commission_rate_vat: float
    commission_taxes: List[MiraklCommissionTax]
    commission_vat: float
    created_date: str
    debited_date: str
    description: str
    last_updated_date: str
    offer_id: int
    offer_sku: str
    offer_state_code: str
    order_line_additional_fields: List[str]
    order_line_id: str
    order_line_index: int
    order_line_state: str
    order_line_state_reason_code: str
    order_line_state_reason_label: str
    price: float
    price_additional_info: str
    price_unit: float
    product_medias: List[str]
    product_sku: str
    product_title: str
    promotions: List[str]
    quantity: int
    received_date: str
    refunds: List[str]
    shipped_date: str
    shipping_price: float
    shipping_price_additional_unit: str
    shipping_price_unit: str
    shipping_taxes: List[str]
    taxes: List[str]
    total_commission: float
    total_price: float

    @classmethod
    def build_mirakl_sale_order_line(cls, data: dict):
        return cls(**data)

    def to_json(self):
        return self.model_dump()
