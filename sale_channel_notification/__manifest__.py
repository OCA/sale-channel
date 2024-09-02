# Copyright 2024 Akretion (https://www.akretion.com).
# @author Mathieu Delva <mathieu.delva@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Channel Notification",
    "summary": "",
    "version": "16.0.1.0.1",
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
        "delivery",
        "sale_channel",
        "stock",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/sale_channel_notification_view.xml",
    ],
    "demo": [],
}
