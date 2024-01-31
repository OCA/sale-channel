#  Copyright (c) Akretion 2020
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)
{
    "name": "Sale Import REST",
    "summary": "REST API for importig Sale Orders",
    "version": "16.0.0.0.0",
    "category": "Generic Modules/Sale",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/akretion/sale-import",
    "depends": [
        "sale_import_base",
        # to avoid extra-glue module we have the dependency on auth_api_key
        # if needed (real use case) we can remove this dependency
        "auth_api_key",
        "fastapi",
    ],
    "license": "AGPL-3",
    "data": [
        "views/fastapi_endpoint_view.xml",
        "security/res_groups.xml",
        "data/res_users.xml",
    ],
    "demo": [
        "demo/demo.xml",
        "demo/fastapi_endpoint_demo.xml",
    ],
    "installable": True,
    "external_dependencies": {"python": ["fastapi", "extendable_pydantic"]},
}
