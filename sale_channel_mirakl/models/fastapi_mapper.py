from typing import List, Optional

import dateutil.parser
from pydantic import BaseModel

from odoo.tools.safe_eval import pytz


class MiraklProduct(BaseModel):

    ean: str = ""
    sku: str = ""
    product_title: str = ""
    product_description: str = ""
    product_cat_code: str = ""

    @classmethod
    def build_mirakl_product(cls, product):
        cat = product.categ_id.display_name or ""
        cat = cat.replace("/", ">")

        pydantic_object = MiraklProduct(
            ean=product.barcode or "",
            sku=product.default_code or "",
            product_title=product.name,
            product_description=product.description or product.name,
            product_cat_code=cat,
        )

        return pydantic_object

    @classmethod
    def get_products_file_header(cls):
        return [
            "sku",
            "ean",
            "PRODUCT_TITLE",
            "PRODUCT_DESCRIPTION",
            "PRODUCT_CAT_CODE",
        ]

    def pydantic_product_model_dump(self):
        return {
            "sku": self.sku,
            "ean": self.ean,
            "PRODUCT_TITLE": self.product_title,
            "PRODUCT_DESCRIPTION": self.product_description,
            "PRODUCT_CAT_CODE": self.product_cat_code,
        }


class MiraklOffer(BaseModel):

    sku: str = ""
    product_id: str = ""
    product_id_type: str = ""
    state: str = ""

    @classmethod
    def build_mirakl_offer(cls, product):
        pydantic_object = MiraklOffer(
            sku=product.mirakl_id,
            product_id=product.barcode if product.barcode else product.default_code,
            product_id_type="EAN" if product.barcode else "SHOP_SKU",
            state="11",
        )

        return pydantic_object

    @classmethod
    def get_offers_file_header(cls):
        return ["sku", "product-id", "product-id-type", "state"]

    def pydantic_offer_model_dump(self):
        return {
            "sku": self.sku,
            "product-id": self.product_id,
            "product-id-type": self.product_id_type,
            "state": self.state,
        }


class MiraklBillingAddress(BaseModel):
    city: str
    civility: str
    company: str
    country: str
    country_iso_code: str | None
    firstname: str
    lastname: str
    phone: str
    phone_secondary: str
    state: str
    street_1: str
    street_2: str
    zip_code: str
    email: str = ""
    customer_notification_email: str = ""

    @classmethod
    def build_mirakl_billing_address(cls, data: dict):
        return cls(**data)


class MiraklShippingAddress(BaseModel):
    additional_info: str
    city: str
    civility: str
    company: str
    country: str
    country_iso_code: str | None
    firstname: str
    lastname: str
    phone: str
    phone_secondary: str
    state: str
    street_1: str
    street_2: str
    zip_code: str
    email: str = ""

    @classmethod
    def build_mirakl_shipping_address(cls, data: dict):
        return cls(**data)


class MiraklResPartner(BaseModel):
    billing_address: MiraklBillingAddress
    civility: str = ""
    customer_id: str  # required
    firstname: str | None  # required, Can be None
    lastname: str = ""
    locale: str = ""
    shipping_address: MiraklShippingAddress
    shipping_zone_code: Optional[str] = None  # not required, Can be None
    company: str = None
    country_iso_code: Optional[str] = None

    @classmethod
    def build_mirakl_customer(cls, data: dict):
        return cls(**data)

    def build_name(self):
        name = (
            " ".join([self.lastname, self.firstname])
            if self.firstname
            else self.lastname
        )
        name = "{}, {}".format(self.company, name) if self.company else name
        return name

    def build_country_id(self, sale_channel):  # TODO
        if self.country_iso_code:
            country = self.env["res.country"].search(
                [("code", "=", self.country_iso_code)]
            )
        elif self.shipping_zone_code:
            country = self.env["res.country"].search(
                [("code", "=", self.shipping_zone_code)]
            )
        else:
            country = sale_channel.channel_id.company_id
        return country.id if country else None

    def odoo_model_dump(self, mirakl_channel):
        return {
            "name": self._compute_name(),
            "country_id": self._compute_country_id(mirakl_channel),
            "sale_channel_id": mirakl_channel.channel_id.id,
            "is_from_mirakl": True,
        }


class MiraklCommissionTax(BaseModel):
    amount: float
    code: str
    rate: float

    @classmethod
    def build_mirakl_commion_tax(cls, data: dict):
        return cls(**data)


class MiraklSaleOrderLine(BaseModel):
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


class MiraklPromotion(BaseModel):
    applied_promotions: List[str]
    total_deduced_amount: int

    @classmethod
    def build_mirakl_promotion(cls, data: dict):
        return cls(**data)


class MiraklSaleOrder(BaseModel):

    acceptance_decision_date: str
    can_cancel: str
    channel: str
    commercial_id: str
    created_date: str
    currency_iso_code: str
    customer: MiraklResPartner
    customer_debited_date: str
    customer_notification_email: str = False
    has_customer_message: str
    has_incident: str
    has_invoice: str
    last_updated_date: str
    leadtime_to_ship: int
    order_additional_fields: List[str]
    order_id: str
    order_lines: List[MiraklSaleOrderLine]
    order_state: str
    order_state_reason_code: str
    order_state_reason_label: str
    paymentType: str
    payment_type: str
    payment_workflow: str
    price: float
    promotions: MiraklPromotion
    quote_id: str
    shipping_carrier_code: str
    shipping_company: str
    shipping_price: float
    shipping_tracking: str
    shipping_tracking_url: str
    shipping_type_code: str
    shipping_type_label: str
    shipping_zone_code: str = ""
    shipping_zone_label: str
    total_commission: float
    total_price: float
    transaction_date: str

    @classmethod
    def build_mirakl_sale_order(cls, data):
        return cls(**data)

    def _get_date_order(self):
        date_order = dateutil.parser.parse(self.created_date)
        date_order = date_order.astimezone(pytz.utc).replace(tzinfo=None)
        return date_order

    def _partner_id(
        self, mirakl_channel, billing_partner_data, partner_mirakl_id
    ):  # TODO
        binding_model = "res.partner"

        if not partner_mirakl_id:
            partner_mirakl_id = mirakl_channel._generate_hash_key(billing_partner_data)
        partner = mirakl_channel._get_binding(partner_mirakl_id, binding_model)

        assert partner is not None, (
            "partner %s should have been imported in "
            "MiraklSaleOrderImporter._import_dependencies" % billing_partner_data
        )
        return partner.id

    def _search_partner_id(self, mirakl_channel):
        partner_mirakl_id = False
        if self.customer.customer_id:
            partner_mirakl_id = self.customer.customer_id + "_billing"
        billing_partner_data = self.customer.billing_address
        billing_partner_data.customer_notification_email = (
            self.customer_notification_email
        )
        partner_id = self._partner_id(
            mirakl_channel, billing_partner_data, partner_mirakl_id
        )
        return partner_id

    def _get_partner_shipping_id(self, mirakl_channel):
        partner_mirakl_id = False
        if self.customer.customer_id:
            partner_mirakl_id = self.customer.customer_id + "_billing"
        partner_id = self._partner_id(
            mirakl_channel, self.customer.shipping_address, partner_mirakl_id
        )
        return partner_id

    def _get_fiscal_position_id(self, mirakl_channel):
        country = self.customer.shipping_address.country
        fiscal_position = mirakl_channel.channel_id.fiscal_position_ids.filtered(
            lambda x: x.country_id.name == country
        )
        return fiscal_position

    def _get_pricelist_id(self):  # TODO
        return self.currency_iso_code
        # currency = self.env["res.currency"].search([("name", "=", currency_code)])

    def odoo_model_dump(self, mirakl_channel):
        partner_id = self._search_partner_id(mirakl_channel)
        return {
            "date_order": self._get_date_order(),
            "partner_id": partner_id,
            "partner_invoice_id": partner_id,
            "partner_shipping_id": self._get_partner_shipping_id(mirakl_channel),
            "user_id": False,
            # "analytic_account_id": mirakl_channel.analytic_account_id.id,  # TODO
            # "fiscal_position_id": self._get_fiscal_position_id(mirakl_channel).id,
            # "warehouse_id": mirakl_channel.warehouse_id.id ,  # TODO
            # "payment_mode_id": mirakl_channel.payment_mode_id.id,  # TODO
            "name": self.order_id,
            # "pricelit_id": self._get_pricelist_id(),
            "sale_channel_id": mirakl_channel.channel_id.id,
        }
