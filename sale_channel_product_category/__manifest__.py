# Copyright 2023 Akretion (https://www.akretion.com).
# @author Raphaël Reverdy<raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Channel Product Category",
    "summary": "Link Product Category with sale channel",
    "version": "16.0.1.0.0",
    "category": "Sale Channel",
    "website": "https://github.com/OCA/sale-channel",
    "author": "Akretion,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "sale_channel",
        "product_multi_category",
    ],
    "data": [
        "views/sale_channel.xml",
    ],
    "demo": ["demo/demo.xml"],
}
