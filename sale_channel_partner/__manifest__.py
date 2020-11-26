#  Copyright (c) Akretion 2020
#  License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)
{
    "name": "Sale Channel Partner",
    "summary": "Bind sale channels to contacts",
    "version": "12.0.1.0.0",
    "category": "Generic Modules/Sale",
    "author": "Akretion",
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
    "installable": False,
}
