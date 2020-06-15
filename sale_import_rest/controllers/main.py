#  Copyright (c) Akretion 2020
#  License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)
from odoo.addons.base_rest.controllers.main import RestController


class SaleImportBaseController(RestController):
    _root_path = "/sale-import/"
    _collection_name = "sale.import.rest.services"
