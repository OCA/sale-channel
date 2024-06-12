#  Copyright (c) Akretion 2020
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
{
    "name": "Sale Import Base",
    "summary": "Base for importing Sale Orders through a JSON file format",
    "version": "16.0.0.0.0",
    "category": "Generic Modules/Sale",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-channel",
    "depends": [
        "queue_job_chunk",
        "sale_channel_partner",
        "sale_exception",
        "extendable",
    ],
    "license": "AGPL-3",
    "data": [
        "security/ir.model.access.csv",
        "data/sale_exception.xml",
        "views/sale_channel_view.xml",
        "views/payment_provider_view.xml",
    ],
    "demo": ["demo/demo.xml"],
    "installable": True,
    "external_dependencies": {
        "python": ["extendable_pydantic"],
    },
}
