#  Copyright (c) Akretion 2020
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from marshmallow_objects import ValidationError, validates

from odoo import _

from odoo.addons.datamodel import fields
from odoo.addons.datamodel.datamodels.base import BaseDatamodel


class SaleOrderLineDatamodel(BaseDatamodel):
    _name = "sale.order.line"

    @validates("product_code")
    def _validate_product_code(self, code):
        product = self._env["product.product"].search([("default_code", "=", code)])
        if len(product.ids) != 1:
            raise ValidationError(
                _("Could not find one product with supplied product code")
            )

    product_code = fields.Str(required=True)
    qty = fields.Decimal(required=True)
    price_unit = fields.Decimal(required=True)
    description = fields.Str()
    discount = fields.Decimal()
