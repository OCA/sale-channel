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
            "product_code": "SKU_A",
            "qty": 5,
            "price_unit": 100,
            "description": "Initial Line 1 import description",
            "discount": 10.0,
            # total discounted = 450
        },
        {
            "product_code": "SKU_B",
            "qty": 2,
            "price_unit": 300,
            "description": "Initial Line 2 import description",
            "discount": 5.0,
            # total discounted = 570
        },
    ],
    "amount": {
        "amount_tax": 153,  # 1020 * 0.15 = 153
        "amount_untaxed": 1020,  # 450 + 570 = 1020
        "amount_total": 1173,  # 1020 + 153 = 1173
    },
    "invoice": {"date": "1900-12-30", "number": "IN-123"},
    "payment": {
        "mode": "credit_card",
        "amount": 1173.00,
        "reference": "PMT-EXAMPLE-001",
        "currency_code": "USD",
        "provider_reference": "T123",
    },
    "pricelist_id": 1,
    "date_order": "2020-01-02",
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
        "street": "1 rue de partner",
        "zip": "69100",
        "city": "Lyon",
        "country_code": "FR",
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
    "lines": [{"product_code": "FURN_7777", "qty": 5, "price_unit": 100}],
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
        "street": "1 rue de partner",
        "zip": "69100",
        "city": "Lyon",
        "country_code": "FR",
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
    "lines": [{"product_code": "FURN_7777", "qty": 5, "price_unit": 100}],
    # "lines": [{"product_code": "PROD_ORDER", "qty": 5, "price_unit": 100}],
    "amount": {
        "amount_tax": 45,  # 500 * 0.09 = 45
        "amount_untaxed": 500,
        "amount_total": 455,  # 500 - 45 = 455
    },
    "invoice": {"date": "1900-12-30", "number": "IN-123"},
    "payment": {
        "mode": "credit_card",
        "amount": 455.00,
        "reference": "PMT-EXAMPLE-001",
        "currency_code": "USD",
    },
}

invalid = {
    "name": "XX-0001",
}
