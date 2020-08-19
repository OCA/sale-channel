#  Copyright (c) Akretion 2020
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.datamodel import fields
from odoo.addons.datamodel.core import Datamodel


class SaleOrderCustomerDatamodel(Datamodel):
    _name = "sale.order.customer"

    name = fields.Str(required=True)
    street = fields.Str()
    street2 = fields.Str()
    zip = fields.Integer()
    city = fields.Str()
    email = fields.Email(required=True)
    state_code = fields.Str()
    country_code = fields.Str()
    external_id = fields.Str(required=True)
    phone = fields.Str()
    mobile = fields.Str()
