import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-sale-channel",
    description="Meta package for oca-sale-channel Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-sale_channel>=16.0dev,<16.1dev',
        'odoo-addon-sale_channel_category>=16.0dev,<16.1dev',
        'odoo-addon-sale_channel_product>=16.0dev,<16.1dev',
        'odoo-addon-sale_channel_search_engine>=16.0dev,<16.1dev',
        'odoo-addon-sale_channel_search_engine_category>=16.0dev,<16.1dev',
        'odoo-addon-sale_channel_search_engine_demo>=16.0dev,<16.1dev',
        'odoo-addon-sale_channel_search_engine_product>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
