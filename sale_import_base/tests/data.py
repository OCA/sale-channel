#  Copyright (c) Akretion 2020
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
data = {
    "address_customer": {
        "name": "Thomas Jean",
        "street": "1 rue de Jean",
        "street2": "bis",
        "zip": "69100",
        "city": "Lyon",
        "email": "thomasjean@example.com",
        "country_code": "FR",
        "external_id": "ThomasJeanEbay",
    },
    "address_shipping": {
        "name": "shipping contact name",
        "street": "2 rue de shipping",
        "street2": "bis",
        "zip": "69100",
        "city": "Lyon",
        "country_code": "FR",
    },
    "address_invoicing": {
        "name": "invoicing contact name",
        "street": "3 rue de invoicing",
        "street2": "bis",
        "zip": "69100",
        "city": "Lyon",
        "country_code": "FR",
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
            # description: missing
            "discount": 0.0,
            # total = 600
        },
    ],
    "amount": {
        "amount_tax": 40.5,  # 450 * 0.09 = 40.5
        "amount_untaxed": 1050,  # 450 + 600 = 1050
        "amount_total": 1090.5,  # 1050 + 40.5 = 1090.5
    },
    "invoice": {"date": "1900-12-30", "number": "IN-123"},
    "payment": {
        "mode": "credit_card",
        "amount": 640.00,
        "reference": "PMT-EXAMPLE-001",
        "currency_code": "USD",
        "acquirer_reference": "T123",
    },
}
