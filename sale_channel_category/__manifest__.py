# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Channel Category",
    "summary": "Link Category with sale channel",
    "version": "16.0.1.0.2",
    "category": "Sale Channel",
    "website": "https://github.com/OCA/sale-channel",
    "author": "Akretion,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "sale_channel",
    ],
    "data": [
        "views/product_category_view.xml",
        "views/sale_channel_view.xml",
    ],
    "demo": [],
}
