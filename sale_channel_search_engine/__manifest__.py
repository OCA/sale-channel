# Copyright 2022 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Channel Search Engine",
    "summary": "Abstract module for configuring a search engine on a sale channel",
    "version": "16.0.0.0.1",
    "development_status": "Alpha",
    "category": "Uncategorized",
    "website": "https://github.com/OCA/sale-channel",
    "author": " Akretion, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "connector_search_engine",
        "sale_channel",
    ],
    "data": [
        "views/sale_channel_view.xml",
    ],
    "demo": [],
}
