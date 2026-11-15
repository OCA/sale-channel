# Copyright 2026 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
from typing import Optional

from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel  # pylint: disable=missing-manifest-dependency

from odoo.addons.sale_import_base.models.schemas import SaleOrder as BaseSaleOrder


class ShippingInfo(BaseModel, metaclass=ExtendableModelMeta):
    carrier_code: Optional[str] = None
    amount: float = 0.0
    promised_date: Optional[datetime] = None


class SaleOrder(BaseSaleOrder, extends=True):
    shipping: Optional[ShippingInfo] = None
