#  Copyright (c) Akretion 2020
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)
{
    "name": "Sale Channel",
    "summary": "Adds the notion of sale channels",
    "version": "16.0.0.1.0",
    "category": "Generic Modules/Sale",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-channel",
    "depends": ["sale_management"],
    "license": "AGPL-3",
    "data": [
        "security/ir.model.access.csv",
        "views/sale_order_view.xml",
        "views/account_move_view.xml",
        "views/sale_channel_view.xml",
    ],
    "demo": ["demo/demo.xml"],
    "installable": True,
}
