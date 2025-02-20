#  Copyright (c) Akretion 2020
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from datetime import date
from typing import List, Optional

from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel  # pylint: disable=missing-manifest-dependency


class Address(BaseModel, metaclass=ExtendableModelMeta):
    name: str
    street: str
    street2: Optional[str] = None
    zip: str
    city: str
    email: Optional[str] = None
    state_code: Optional[str] = None
    country_code: str
    phone: Optional[str] = None
    mobile: Optional[str] = None


class Customer(Address):
    external_id: str


class SaleOrderLine(BaseModel, metaclass=ExtendableModelMeta):
    product_code: str
    qty: float
    price_unit: float
    description: Optional[str] = None
    discount: Optional[float] = None


class Amount(BaseModel, metaclass=ExtendableModelMeta):
    amount_tax: Optional[float] = None
    amount_untaxed: Optional[float] = None
    amount_total: Optional[float] = None


class Payment(BaseModel, metaclass=ExtendableModelMeta):
    mode: str
    amount: float
    reference: str
    currency_code: str
    provider_reference: Optional[str] = None


class SaleOrder(BaseModel, metaclass=ExtendableModelMeta):
    name: str
    address_customer: Customer
    address_shipping: Address
    address_invoicing: Address
    lines: List[SaleOrderLine]
    amount: Optional[Amount] = None
    payment: Optional[Payment] = None
    pricelist_id: Optional[int] = None
    date_order: Optional[date] = None
