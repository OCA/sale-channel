#  Copyright (c) Akretion 2020
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)
{
    "name": "Sale Channel Partner",
    "summary": "Bind sale channels to contacts",
    "version": "14.0.1.0.0",
    "category": "Generic Modules/Sale",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/akretion/sale-import",
    "depends": ["sale_channel"],
    "license": "AGPL-3",
    "data": [
        "security/ir.model.access.csv",
        "views/sale_channel.xml",
        "views/res_partner.xml",
        "views/sale_channel_partner.xml",
    ],
    "demo": ["demo/demo.xml"],
    "installable": True,
}
