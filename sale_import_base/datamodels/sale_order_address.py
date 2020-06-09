#  Copyright (c) Akretion 2020
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from marshmallow_objects import ValidationError, validates

from odoo import _

from odoo.addons.datamodel import fields
from odoo.addons.datamodel.core import Datamodel


class SaleOrderAddressDatamodel(Datamodel):
    _name = "sale.order.address"

    @validates("state_code")
    def _validate_state_code(self, code):
        if not code:
            return
        state = self._env["res.country.state"].search([("code", "=", code)])
        if len(state.ids) != 1:
            raise ValidationError(_("Could not determine one state from state code"))

    @validates("country_code")
    def _validate_country_code(self, code):
        country = self._env["res.country"].search([("code", "=", code)])
        if len(country.ids) != 1:
            raise ValidationError(
                _("Could not determine one country from country code")
            )

    name = fields.Str(required=True)
    street = fields.Str(required=True)
    street2 = fields.Str()
    zip = fields.Integer(required=True)
    city = fields.Str(required=True)
    email = fields.Email()  # validates in sale_order
    state_code = fields.Str()
    country_code = fields.Str(required=True)
    external_id = fields.Str()
