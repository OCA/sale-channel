#  Copyright (c) Akretion 2020
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

# Full data on fields of sale.order
# Full data on sub-objects
full = {
    "name": "XX-0001",
    "address_customer": {
        "name": "Thomas Jean",
        "street": "1 rue de Jean",
        "street2": "bis",
        "zip": "69100",
        "city": "Arizonapolis",
        "email": "thomasjean@example.com",
        "state_code": "AZ",
        "country_code": "US",
        "external_id": "ThomasJeanEbay",
        "phone": "+1 2677215197",
        "mobile": "+1 1516288131",
    },
    "address_shipping": {
        "name": "shipping contact name",
        "street": "2 rue de shipping",
        "street2": "bis",
        "zip": "69100",
        "city": "New Jerseypolis",
        "state_code": "NJ",
        "country_code": "US",
        "phone": "+1 2677215197",
        "mobile": "+1 1516288131",
    },
    "address_invoicing": {
        "name": "invoicing contact name",
        "street": "3 rue de invoicing",
        "street2": "bis",
        "zip": "69100",
        "city": "New Jerseypolis",
        "state_code": "NJ",
        "country_code": "US",
        "phone": "+1 2677215197",
        "mobile": "+1 1516288131",
    },
    "lines": [
        {
            "product_code": "PROD_ORDER",
            "qty": 5,
            "price_unit": 100,
            "description": "Initial Line 1 import description",
            "discount": 10.0,
            # total discounted = 450
        },
        {
            "product_code": "PROD_DEL",
            "qty": 2,
            "price_unit": 300,
            "description": "Initial Line 2 import description",
            "discount": 5.0,
            # total = 570
        },
    ],
    "amount": {
        "amount_tax": 40.5,  # 450 * 0.09 = 40.5
        "amount_untaxed": 1020,  # 450 + 570 = 1020
        "amount_total": 1060.5,  # 1020 + 40.5 = 1090.5
    },
    "invoice": {"date": "1900-12-30", "number": "IN-123"},
    "payment": {
        "mode": "credit_card",
        "amount": 640.00,
        "reference": "PMT-EXAMPLE-001",
        "currency_code": "USD",
        "acquirer_reference": "T123",
    },
    "pricelist_id": 1,
}

# Minimum data on fields of sale.order
# Minimum data on required sub objects
# No optional sub objects
minimum = {
    "name": "XX-0001",
    "address_customer": {
        "name": "Thomas Jean",
        "email": "thomasjean@example.com",
        "external_id": "ThomasJeanEbay",
    },
    "address_shipping": {
        "name": "shipping contact name",
        "street": "2 rue de shipping",
        "zip": "69100",
        "city": "Lyon",
        "country_code": "FR",
    },
    "address_invoicing": {
        "name": "invoicing contact name",
        "street": "3 rue de invoicing",
        "zip": "69100",
        "city": "Lyon",
        "country_code": "FR",
    },
    "lines": [{"product_code": "PROD_ORDER", "qty": 5, "price_unit": 100}],
}

# Minimum data on sale.order
# Minimum data on required sub-objects
# Minimum data on optional sub-objects
mixed = {
    "name": "XX-0001",
    "address_customer": {
        "name": "Thomas Jean",
        "email": "thomasjean@example.com",
        "external_id": "ThomasJeanEbay",
    },
    "address_shipping": {
        "name": "shipping contact name",
        "street": "2 rue de shipping",
        "zip": "69100",
        "city": "Lyon",
        "country_code": "FR",
    },
    "address_invoicing": {
        "name": "invoicing contact name",
        "street": "3 rue de invoicing",
        "zip": "69100",
        "city": "Lyon",
        "country_code": "FR",
    },
    "lines": [{"product_code": "PROD_ORDER", "qty": 5, "price_unit": 100}],
    "amount": {
        "amount_tax": 45,  # 500 * 0.09 = 45
        "amount_untaxed": 500,
        "amount_total": 455,  # 500 - 45 = 455
    },
    "invoice": {"date": "1900-12-30", "number": "IN-123"},
    "payment": {
        "mode": "credit_card",
        "amount": 640.00,
        "reference": "PMT-EXAMPLE-001",
        "currency_code": "USD",
    },
}
