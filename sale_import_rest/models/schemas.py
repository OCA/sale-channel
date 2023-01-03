# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from typing import List

from pydantic import BaseModel

from odoo.addons.sale_import_base.models.schemas import SaleOrder


class SaleImportInput(BaseModel):
    sale_orders: List[SaleOrder]


class SaleCancelInput(BaseModel):
    sale_name: str
