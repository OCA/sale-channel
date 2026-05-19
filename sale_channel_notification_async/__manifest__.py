# Copyright 2026 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Channel Notification Async",
    "version": "18.0.1.0.0",
    "author": "Akretion, Odoo Community Association (OCA)",
    "summary": "Asynchronous notifications for sale channels",
    "depends": ["sale_channel_notification", "queue_job"],
    "website": "https://github.com/OCA/sale-channel",
    "data": [
        "views/sale_channel_views.xml",
    ],
    "maintainers": ["paradoxxxzero"],
    "installable": True,
    "license": "AGPL-3",
}
