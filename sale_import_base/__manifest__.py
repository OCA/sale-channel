#  Copyright (c) Akretion 2020
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
{
    "name": "Sale Import Base",
    "summary": "Base for importing Sale Orders through a JSON file format",
    "version": "14.0.1.0.0",
    "category": "Generic Modules/Sale",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/akretion/sale-import",
    "depends": [
        "queue_job_chunk",
        "product_code_unique",
        "datamodel",
        "sale_channel_partner",
        "sale_exception",
        "onchange_helper",
    ],
    "license": "AGPL-3",
    "data": [
        "data/sale_exception.xml",
        "views/sale_channel.xml",
        "views/payment_acquirer_view.xml",
    ],
    "demo": ["demo/demo.xml"],
    "installable": True,
    "external_dependencies": {"python": ["marshmallow_objects"]},
}
