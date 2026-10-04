#!/env/bin/python3.9
import httpx

data = {
    "sale_orders": [
        {
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
    ]
}


r = httpx.post(
    "http://localhost:8069/sale-channel-import/sale/create",
    json=data,
    headers={"API-KEY": "ASecureKeyApiRest"},
)
