{
    "name": "Mirakl Connector",
    "summary": "Module used to connect Odoo to Mirakl",
    "version": "16.0.1.0.0",
    "category": "Connector",
    "website": "https://github.com/OCA/sale-channel",
    "author": "ACSONE SA/NV, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": True,
    "external_dependencies": {"python": ["pydantic"]},
    "depends": [
        # ODOO
        "sale_stock",
        # OCA
        "sale_channel_product",
        "sale_channel_account",
        "account_payment_sale",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/sale_channel_mirakl.xml",
        "views/menu_sale_channel_mirakl.xml",
    ],
}
