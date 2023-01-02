#  Copyright (c) Akretion 2020
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from datetime import date
from typing import List, Optional

from pydantic import BaseModel

# TODO use extendable when ready


class Address(BaseModel):
    name: str
    street: str
    street2: Optional[str] = None
    zip: str
    city: str
    email: Optional[str]
    state_code: Optional[str]
    country_code: str
    phone: Optional[str]
    mobile: Optional[str]


class Customer(Address):
    external_id: str


class SaleOrderLine(BaseModel):
    product_code: str
    qty: float
    price_unit: float
    description: Optional[str]
    discount: Optional[float]


class Amount(BaseModel):
    amount_tax: Optional[float] = None
    amount_untaxed: Optional[float] = None
    amount_total: Optional[float] = None


class Invoice(BaseModel):
    date: date
    number: str


class Payment(BaseModel):
    mode: str
    amount: float
    reference: str
    currency_code: str
    provider_reference: Optional[str]


class SaleOrder(BaseModel):
    name: str
    address_customer: Customer
    address_shipping: Address
    address_invoicing: Address
    lines: List[SaleOrderLine]
    amount: Optional[Amount]
    invoice: Optional[Invoice]
    payment: Optional[Payment]
    pricelist_id: Optional[int]
    date_order: Optional[date]
