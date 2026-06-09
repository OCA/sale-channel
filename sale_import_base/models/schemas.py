#  Copyright (c) Akretion 2020
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from datetime import date

from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel  # pylint: disable=missing-manifest-dependency


class Address(BaseModel, metaclass=ExtendableModelMeta):
    name: str
    street: str
    street2: str | None = None
    zip: str
    city: str
    email: str | None = None
    state_code: str | None = None
    country_code: str
    phone: str | None = None
    mobile: str | None = None


class Customer(Address):
    external_id: str


class SaleOrderLine(BaseModel, metaclass=ExtendableModelMeta):
    product_code: str
    qty: float
    price_unit: float
    description: str | None = None
    discount: float | None = None


class Amount(BaseModel, metaclass=ExtendableModelMeta):
    amount_tax: float | None = None
    amount_untaxed: float | None = None
    amount_total: float | None = None


class Payment(BaseModel, metaclass=ExtendableModelMeta):
    mode: str
    amount: float
    reference: str
    currency_code: str
    provider_reference: str | None = None


class SaleOrder(BaseModel, metaclass=ExtendableModelMeta):
    name: str
    address_customer: Customer
    address_shipping: Address
    address_invoicing: Address
    lines: list[SaleOrderLine]
    amount: Amount | None = None
    payment: Payment | None = None
    pricelist_id: int | None = None
    date_order: date | None = None
