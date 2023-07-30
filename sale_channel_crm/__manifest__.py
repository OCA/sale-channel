#  Copyright (c) Trescloud 2023
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)
{
    "name": "Sale Channel CRM",
    "summary": "Link crm team with sale channel",
    "version": "16.0.0.0.0",
    "category": "Generic Modules/Sale",
    "author": "Trescloud, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-channel-crm",
    "depends": ["sale_channel", "crm"],
    "license": "AGPL-3",
    "data": [
        'views/crm_team_view.xml'
    ],
    "installable": True,
}
