#  Copyright (c) Akretion 2020
#  License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

import json

from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.base_rest.restapi import RestMethodParam


class IntegerList(RestMethodParam):
    def to_response(self, service, result):
        if not result:
            return []
        for el in result:
            if not isinstance(el, int):
                raise ValidationError(_("IntegerList must contain integers only"))
        return json.dumps(result)

    def to_openapi_responses(self, service):
        return {"200": {"content": {"application/json": {"schema": []}}}}
