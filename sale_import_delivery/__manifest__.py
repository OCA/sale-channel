# Copyright 2026 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Import Delivery",
    "summary": "Carrier, shipping amount and promised date on imported sale orders",
    "version": "16.0.1.0.0",
    "development_status": "Beta",
    "category": "Generic Modules/Sale",
    "author": "KMEE, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-channel",
    "license": "AGPL-3",
    "maintainers": ["mileo"],
    "depends": ["sale_import_base", "delivery"],
    "external_dependencies": {"python": ["extendable_pydantic"]},
    "data": ["views/delivery_carrier_views.xml", "views/sale_views.xml"],
    "installable": True,
}
