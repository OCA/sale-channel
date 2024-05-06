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
        # OCA
        "sale_channel_product",
        "queue_job",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/sale_channel_mirakl_v2.xml",
        "views/menu_sale_channel_mirakl.xml",
    ],
}
