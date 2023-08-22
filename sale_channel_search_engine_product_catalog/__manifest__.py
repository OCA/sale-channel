# Copyright 2023 Akretion (https://www.akretion.com).
# @author Raphaël Reverdy<raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Channel Search Engine Product Catalog",
    "summary": "export product through catalog to se",
    "version": "16.0.1.0.0",
    "category": "Sale Channel",
    "development_status": "Alpha",
    "website": "https://github.com/OCA/sale-channel",
    "author": "Akretion,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "data": ["views/product_catalog.xml"],
    "depends": [
        "sale_channel_product_catalog",
        "sale_channel_search_engine",
    ],
}
