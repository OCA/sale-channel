# Copyright 2026 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Mathieu Delva <mathieu.delva@akretion.com>
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Channel Notification",
    "summary": "Custom notifications for sale channels",
    "version": "18.0.1.0.0",
    "category": "Sale Channel",
    "website": "https://github.com/OCA/sale-channel",
    "author": "Akretion,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "sale_channel",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/sale_channel_views.xml",
    ],
}
