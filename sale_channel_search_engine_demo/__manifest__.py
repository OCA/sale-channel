# Copyright 2022 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Channel Search Engine Test/Demo module",
    "summary": "Implement an export of category in search engine based on "
    "sale channel link",
    "version": "16.0.0.0.1",
    "development_status": "Alpha",
    "category": "Uncategorized",
    "website": "https://github.com/OCA/sale-channel",
    "author": " Akretion, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "sale_channel_search_engine_category",
        "sale_channel_search_engine_product",
        "connector_elasticsearch",
        "connector_search_engine_serializer_ir_export",
    ],
    "data": [],
    "demo": [
        "demo/se_backend_demo.xml",
        "demo/ir_exports_demo.xml",
        "demo/se_index_config_demo.xml",
        "demo/se_index_demo.xml",
        "demo/sale_channel_demo.xml",
    ],
}
