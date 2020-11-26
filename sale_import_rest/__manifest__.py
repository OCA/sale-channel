#  Copyright (c) Akretion 2020
#  License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)
{
    "name": "Sale Import REST",
    "summary": "REST API for importig Sale Orders",
    "version": "12.0.1.0.0",
    "category": "Generic Modules/Sale",
    "author": "Akretion",
    "website": "https://github.com/akretion/sale-import",
    "depends": ["sale_import_base", "auth_api_key", "base_rest"],
    "license": "AGPL-3",
    "data": ["views/sale_channel.xml"],
    "demo": ["demo/demo.xml"],
    "installable": False,
}
