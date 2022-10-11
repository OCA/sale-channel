#  Copyright (c) Akretion 2020
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)
from odoo.addons.base_rest.controllers.main import RestController


class SaleImportBaseController(RestController):
    _root_path = "/channel-api/"
    _collection_name = "sale.import.rest.services"
    _default_auth = "api_key"
