import csv
from base64 import b64decode
from io import StringIO

from odoo import Command
from odoo.tests import common


class SetUpMiraklBase(common.TransactionCase):
    def _read_filename(self, filename):
        csv_file = self.env["ir.attachment"].search([("name", "=", filename)], limit=1)
        datas = b64decode(csv_file.datas)
        reader = csv.DictReader(StringIO(datas.decode()), delimiter=";")
        return reader

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.sale_channel = cls.env["sale.channel"].create(
            {
                "name": "Super sale channel",
                "channel_type": "mirakl",
            }
        )

        cls.sale_channel_mirakl = cls.env["sale.channel.mirakl"]

        cls.mirakl_sc_for_product = cls.sale_channel_mirakl.create(
            {
                "channel_id": cls.sale_channel.id,
                "location": "http://anyurl.com",
                "api_key": "azerty",
                "offer_filename": "offers.csv",
                "shop_id": "11",
                "data_to_export": "product",
            }
        )

        cls.mirakl_sc_for_offer = cls.sale_channel_mirakl.create(
            {
                "channel_id": cls.sale_channel.id,
                "location": "http://anyurl.com",
                "api_key": "azerty",
                "offer_filename": "offers.csv",
                "shop_id": "25",
                "data_to_export": "offer",
            }
        )

        cls.mirakl_sc_for_catalog = cls.sale_channel_mirakl.create(
            {
                "channel_id": cls.sale_channel.id,
                "location": "http://anyurl.com",
                "api_key": "azerty",
                "offer_filename": "offers.csv",
                "shop_id": "25",
                "data_to_export": "both",
            }
        )

        cls.product1 = cls.env.ref("product.product_product_9")
        cls.product2 = cls.env.ref("product.product_product_11")

        cls.product1.write(
            {
                "default_code": "29491209",
                "mirakl_id": "29491209",
                "channel_ids": [Command.link(cls.mirakl_sc_for_product.channel_id.id)],
            }
        )
        cls.product2.write(
            {
                "default_code": "29182572",
                "mirakl_id": "29182572",
                "barcode": "4004764782703",
                "description": "A smart description",
                "list_price": 40.59,
                "channel_ids": [Command.link(cls.mirakl_sc_for_product.channel_id.id)],
            }
        )

    def setUp(self):
        super().setUp()
        self.orders = [
            {
                "acceptance_decision_date": "2016-11-18T15:30:56Z",
                "can_cancel": "",
                "channel": "",
                "commercial_id": "1611DBLLZ-MP002191",
                "created_date": "2016-11-18T13:31:55Z",
                "currency_iso_code": "EUR",
                "customer_notification_email": "test@email.com",
                "customer": {
                    "billing_address": {
                        "city": "fontenay-aux-roses",
                        "civility": "Mme",
                        "company": "",
                        "country": "France",
                        "country_iso_code": None,
                        "firstname": "maria",
                        "lastname": "nicolo",
                        "phone": "0688430945",
                        "phone_secondary": "0688430945",
                        "state": "",
                        "street_1": "21 avenue paul langevin ",
                        "street_2": "",
                        "zip_code": "92260",
                    },
                    "civility": "",
                    "customer_id": "3786926",
                    "firstname": "maria",
                    "lastname": "nicolo",
                    "locale": "",
                    "shipping_address": {
                        "additional_info": "",
                        "city": "fontenay-aux-roses",
                        "civility": "Mme",
                        "company": "",
                        "country": "France",
                        "country_iso_code": None,
                        "firstname": "Albert",
                        "lastname": "Einstein",
                        "phone": "0688430945",
                        "phone_secondary": "0688430945",
                        "state": "",
                        "street_1": "21 avenue paul langevin ",
                        "street_2": "",
                        "zip_code": "92260",
                    },
                },
                "customer_debited_date": "2016-11-18T" "15:31:03.190Z",
                "has_customer_message": "",
                "has_incident": "",
                "has_invoice": "",
                "last_updated_date": "2017-02-21T23:00:01Z",
                "leadtime_to_ship": 0,
                "order_additional_fields": [],
                "order_id": "1611DBLLZ-MP002191-A",
                "order_lines": [
                    {
                        "can_refund": "",
                        "cancelations": [],
                        "category_code": "JJ01-003-002",
                        "category_label": "FIGURINES",
                        "commission_fee": 11.25,
                        "commission_rate_vat": 0,
                        "commission_taxes": [
                            {"amount": 0, "code": "TAXZERO", "rate": 0}
                        ],
                        "commission_vat": 0,
                        "created_date": "2016-11-18T13:31:55Z",
                        "debited_date": "2016-11-18T15:31:03Z",
                        "description": "Avec ses quatre étages "
                        "de parking,"
                        " ses pompes à "
                        "essence et un "
                        "marquage d'héliport, les "
                        "conducteurs impatients "
                        "vont et "
                        "viennent dans toutes les "
                        "directions.INFORMATIONS "
                        "TECHNIQUES :  - Age : 3A+",
                        "last_updated_date": "2017-02-21T23:00:01Z",
                        "offer_id": 41601,
                        "offer_sku": "29182572",
                        "offer_state_code": "11",
                        "order_line_additional_fields": [],
                        "order_line_id": "1611DBLLZ-MP002191-A-1",
                        "order_line_index": 1,
                        "order_line_state": "CLOSED",
                        "order_line_state_reason_code": "AUTO_CLOSED",
                        "order_line_state_reason_label": "Fermée automatiquement",
                        "price": 62.49,
                        "price_additional_info": "",
                        "price_unit": 62.49,
                        "product_medias": [],
                        "product_sku": "91191850",
                        "product_title": "Garage en bois jouet hape",
                        "promotions": [],
                        "quantity": 1,
                        "received_date": "2016-11-23T19:15:03Z",
                        "refunds": [],
                        "shipped_date": "2016-11-21T08:43:39Z",
                        "shipping_price": 32,
                        "shipping_price_additional_unit": "",
                        "shipping_price_unit": "",
                        "shipping_taxes": [],
                        "taxes": [],
                        "total_commission": 11.25,
                        "total_price": 62.49,
                    }
                ],
                "order_state": "CLOSED",
                "order_state_reason_code": "AUTO_CLOSED",
                "order_state_reason_label": "Fermée automatiquement",
                "paymentType": "CarteBancairePaybox",
                "payment_type": "CarteBancairePaybox",
                "payment_workflow": "PAY_ON_ACCEPTANCE",
                "price": 62.49,
                "promotions": {
                    "applied_promotions": [],
                    "total_deduced_amount": 0,
                },
                "quote_id": "",
                "shipping_carrier_code": "Group",
                "shipping_company": "GLS",
                "shipping_price": 32,
                "shipping_tracking": "009YYDNG",
                "shipping_tracking_url": "https://gls-group.eu"
                "/FR/fr/suivi-colis?"
                "match=009YYDNG",
                "shipping_type_code": "L08",
                "shipping_type_label": "Colis suivi",
                "shipping_zone_code": "FRA",
                "shipping_zone_label": "France métropolitaine + Corse",
                "total_commission": 11.25,
                "total_price": 94.49,
                "transaction_date": "2016-11-18T15:30:56.000Z",
            },
            {
                "acceptance_decision_date": "2016-11-18T15:30:57Z",
                "can_cancel": "",
                "channel": "",
                "commercial_id": "1611DBLMN-MP002191",
                "created_date": "2016-11-18T13:40:20Z",
                "currency_iso_code": "EUR",
                "customer": {
                    "billing_address": {
                        "city": "GRENOBLE",
                        "civility": "Mme",
                        "company": "Zebulon",
                        "country": "France",
                        "country_iso_code": "",
                        "firstname": "Anne-Sophie",
                        "lastname": "Martigne",
                        "phone": "0686685166",
                        "phone_secondary": "0686685166",
                        "state": "",
                        "street_1": "33 Rue marceau",
                        "street_2": "Résidence le Sully",
                        "zip_code": "38000",
                    },
                    "civility": "",
                    "customer_id": "3786940",
                    "firstname": "Anne-Sophie",
                    "lastname": "Martigne",
                    "locale": "",
                    "shipping_address": {
                        "additional_info": "",
                        "city": "GRENOBLE",
                        "civility": "Mme",
                        "company": "",
                        "country": "France",
                        "country_iso_code": "",
                        "firstname": "Johnny",
                        "lastname": "Depp",
                        "phone": "0686685166",
                        "phone_secondary": "0686685166",
                        "state": "",
                        "street_1": "33 Rue marceau",
                        "street_2": "Résidence le Sully",
                        "zip_code": "38000",
                    },
                },
                "customer_debited_date": "2016-11-18T15:31:03.486Z",
                "has_customer_message": "",
                "has_incident": "",
                "has_invoice": "",
                "last_updated_date": "2017-02-21T23:00:01Z",
                "leadtime_to_ship": 0,
                "order_additional_fields": [],
                "order_id": "1611DBLMN-MP002191-A",
                "order_lines": [
                    {
                        "can_refund": "",
                        "cancelations": [],
                        "category_code": "JJ01-007-004",
                        "category_label": "MUSIQUE",
                        "commission_fee": 11.7,
                        "commission_rate_vat": 0,
                        "commission_taxes": [
                            {"amount": 0, "code": "TAXZERO", "rate": 0}
                        ],
                        "commission_vat": 0,
                        "created_date": "2016-11-18T13:40:20Z",
                        "debited_date": "2016-11-18T15:31:03Z",
                        "description": "Laissez parler la musique. "
                        "Les dix-huit petites touches de "
                        "ce piano en bois robuste "
                        "permettent aux virtuoses en "
                        "herbe d'exprimer tout leur talent."
                        "INFORMATIONS TECHNIQUES :  - Age "
                        ": 3A+",
                        "last_updated_date": "2017-02-21T23:00:01Z",
                        "offer_id": 41636,
                        "offer_sku": "29491209",
                        "offer_state_code": "11",
                        "order_line_additional_fields": [],
                        "order_line_id": "1611DBLMN-MP002191-A-1",
                        "order_line_index": 1,
                        "order_line_state": "CLOSED",
                        "order_line_state_reason_code": "AUTO_CLOSED",
                        "order_line_state_reason_label": "Fermée automatiquement",
                        "price": 64.99,
                        "price_additional_info": "",
                        "price_unit": 64.99,
                        "product_medias": [],
                        "product_sku": "91191860",
                        "product_title": "Jouet piano rouge bois hape",
                        "promotions": [],
                        "quantity": 1,
                        "received_date": "2016-11-23T19:15:04Z",
                        "refunds": [],
                        "shipped_date": "2016-11-21T17:09:31Z",
                        "shipping_price": 0,
                        "shipping_price_additional_unit": "",
                        "shipping_price_unit": "",
                        "shipping_taxes": [],
                        "taxes": [],
                        "total_commission": 11.7,
                        "total_price": 64.99,
                    },
                    {
                        "can_refund": "",
                        "cancelations": [],
                        "category_code": "PU02-006-010",
                        "category_label": "AUTRES JEUX DE MANIPULATION",
                        "commission_fee": 3.96,
                        "commission_rate_vat": 0,
                        "commission_taxes": [
                            {"amount": 0, "code": "TAXZERO", "rate": 0}
                        ],
                        "commission_vat": 0,
                        "created_date": "2016-11-18T13:40:20Z",
                        "debited_date": "2016-11-18T15:31:03Z",
                        "description": "Les blocs remplis de perles "
                        "ajoutent une nouvelle dimension "
                        "à ce trieur de formes multitâches."
                        "INFORMATIONS TECHNIQUES :  - "
                        "Age : 12M+",
                        "last_updated_date": "2017-02-21T23:00:01Z",
                        "offer_id": 41575,
                        "offer_sku": "29627455",
                        "offer_state_code": "11",
                        "order_line_additional_fields": [],
                        "order_line_id": "1611DBLMN-MP002191-A-2",
                        "order_line_index": 2,
                        "order_line_state": "CLOSED",
                        "order_line_state_reason_code": "AUTO_CLOSED",
                        "order_line_state_reason_label": "Fermée automatiquement",
                        "price": 21.99,
                        "price_additional_info": "",
                        "price_unit": 21.99,
                        "product_medias": [],
                        "product_sku": "91191860",
                        "product_title": "Trieur de formes en bois hape",
                        "promotions": [],
                        "quantity": 1,
                        "received_date": "2016-11-23T19:15:04Z",
                        "refunds": [],
                        "shipped_date": "2016-11-21T17:09:31Z",
                        "shipping_price": 0,
                        "shipping_price_additional_unit": "",
                        "shipping_price_unit": "",
                        "shipping_taxes": [],
                        "taxes": [],
                        "total_commission": 3.96,
                        "total_price": 21.99,
                    },
                ],
                "order_state": "CLOSED",
                "order_state_reason_code": "AUTO_CLOSED",
                "order_state_reason_label": "Fermée automatiquement",
                "paymentType": "CarteBancairePaybox",
                "payment_type": "CarteBancairePaybox",
                "payment_workflow": "PAY_ON_ACCEPTANCE",
                "price": 86.98,
                "promotions": {
                    "applied_promotions": [],
                    "total_deduced_amount": 0,
                },
                "quote_id": "",
                "shipping_carrier_code": "Group",
                "shipping_company": "GLS",
                "shipping_price": 0,
                "shipping_tracking": "009YYI19",
                "shipping_tracking_url": "https://gls-group.eu"
                "/FR/fr/suivi-colis?"
                "match=009YYI19",
                "shipping_type_code": "L08",
                "shipping_type_label": "Colis suivi",
                "shipping_zone_code": "FRA",
                "shipping_zone_label": "France métropolitaine + Corse",
                "total_commission": 15.66,
                "total_price": 86.98,
                "transaction_date": "2016-11-18T15:30:57.000Z",
            },
            {
                "acceptance_decision_date": "2016-11-18T15:30:57Z",
                "can_cancel": "",
                "channel": "",
                "commercial_id": "1611DBLMO-MP002191",
                "created_date": "2016-11-18T13:40:20Z",
                "currency_iso_code": "EUR",
                "customer": {
                    "billing_address": {
                        "city": "LIEGE",
                        "civility": "Mme",
                        "company": "Jupiler",
                        "country": "Belgique",
                        "country_iso_code": "",
                        "firstname": "Nanesse",
                        "lastname": "Francois",
                        "phone": "0495123456",
                        "phone_secondary": "0495123456",
                        "state": "",
                        "street_1": "1 Place du marché",
                        "street_2": "",
                        "zip_code": "4000",
                    },
                    "civility": "",
                    "customer_id": "3786942",
                    "firstname": "Nanesse",
                    "lastname": "Francois",
                    "locale": "",
                    "shipping_address": {
                        "additional_info": "",
                        "city": "LIEGE",
                        "civility": "Mme",
                        "company": "",
                        "country": "Belgique",
                        "country_iso_code": "",
                        "firstname": "Nanesse",
                        "lastname": "Francois",
                        "phone": "0495123456",
                        "phone_secondary": "0495123456",
                        "state": "",
                        "street_1": "1 Place du marché",
                        "street_2": "",
                        "zip_code": "4000",
                    },
                },
                "customer_debited_date": "2016-11-18T15:31:03.486Z",
                "has_customer_message": "",
                "has_incident": "",
                "has_invoice": "",
                "last_updated_date": "2017-02-21T23:00:01Z",
                "leadtime_to_ship": 0,
                "order_additional_fields": [],
                "order_id": "1611DBLMO-MP002191-A",
                "order_lines": [
                    {
                        "can_refund": "",
                        "cancelations": [],
                        "category_code": "JJ01-007-004",
                        "category_label": "MUSIQUE",
                        "commission_fee": 11.7,
                        "commission_rate_vat": 0,
                        "commission_taxes": [
                            {"amount": 0, "code": "TAXZERO", "rate": 0}
                        ],
                        "commission_vat": 0,
                        "created_date": "2016-11-18T13:40:20Z",
                        "debited_date": "2016-11-18T15:31:03Z",
                        "description": "Laissez parler la musique. "
                        "Les dix-huit petites touches de "
                        "ce piano en bois robuste "
                        "permettent aux virtuoses en "
                        "herbe d'exprimer tout leur talent."
                        "INFORMATIONS TECHNIQUES :  - Age "
                        ": 3A+",
                        "last_updated_date": "2017-02-21T23:00:01Z",
                        "offer_id": 41636,
                        "offer_sku": "29491209",
                        "offer_state_code": "11",
                        "order_line_additional_fields": [],
                        "order_line_id": "1611DBLMO-MP002191-A-1",
                        "order_line_index": 1,
                        "order_line_state": "CLOSED",
                        "order_line_state_reason_code": "AUTO_CLOSED",
                        "order_line_state_reason_label": "Fermée automatiquement",
                        "price": 64.99,
                        "price_additional_info": "",
                        "price_unit": 64.99,
                        "product_medias": [],
                        "product_sku": "91191860",
                        "product_title": "Jouet piano rouge bois hape",
                        "promotions": [],
                        "quantity": 1,
                        "received_date": "2016-11-23T19:15:04Z",
                        "refunds": [],
                        "shipped_date": "2016-11-21T17:09:31Z",
                        "shipping_price": 0,
                        "shipping_price_additional_unit": "",
                        "shipping_price_unit": "",
                        "shipping_taxes": [],
                        "taxes": [],
                        "total_commission": 11.7,
                        "total_price": 64.99,
                    },
                    {
                        "can_refund": "",
                        "cancelations": [],
                        "category_code": "PU02-006-010",
                        "category_label": "AUTRES JEUX DE MANIPULATION",
                        "commission_fee": 3.96,
                        "commission_rate_vat": 0,
                        "commission_taxes": [
                            {"amount": 0, "code": "TAXZERO", "rate": 0}
                        ],
                        "commission_vat": 0,
                        "created_date": "2016-11-18T13:40:20Z",
                        "debited_date": "2016-11-18T15:31:03Z",
                        "description": "Les blocs remplis de perles "
                        "ajoutent une nouvelle dimension "
                        "à ce trieur de formes multitâches."
                        "INFORMATIONS TECHNIQUES :  - "
                        "Age : 12M+",
                        "last_updated_date": "2017-02-21T23:00:01Z",
                        "offer_id": 41575,
                        "offer_sku": "29627455",
                        "offer_state_code": "11",
                        "order_line_additional_fields": [],
                        "order_line_id": "1611DBLMO-MP002191-A-2",
                        "order_line_index": 2,
                        "order_line_state": "CLOSED",
                        "order_line_state_reason_code": "AUTO_CLOSED",
                        "order_line_state_reason_label": "Fermée automatiquement",
                        "price": 21.99,
                        "price_additional_info": "",
                        "price_unit": 21.99,
                        "product_medias": [],
                        "product_sku": "91191860",
                        "product_title": "Trieur de formes en bois hape",
                        "promotions": [],
                        "quantity": 1,
                        "received_date": "2016-11-23T19:15:04Z",
                        "refunds": [],
                        "shipped_date": "2016-11-21T17:09:31Z",
                        "shipping_price": 0,
                        "shipping_price_additional_unit": "",
                        "shipping_price_unit": "",
                        "shipping_taxes": [],
                        "taxes": [],
                        "total_commission": 3.96,
                        "total_price": 21.99,
                    },
                ],
                "order_state": "CLOSED",
                "order_state_reason_code": "AUTO_CLOSED",
                "order_state_reason_label": "Fermée automatiquement",
                "paymentType": "CarteBancairePaybox",
                "payment_type": "CarteBancairePaybox",
                "payment_workflow": "PAY_ON_ACCEPTANCE",
                "price": 86.98,
                "promotions": {
                    "applied_promotions": [],
                    "total_deduced_amount": 0,
                },
                "quote_id": "",
                "shipping_carrier_code": "Group",
                "shipping_company": "GLS",
                "shipping_price": 0,
                "shipping_tracking": "009YYI19",
                "shipping_tracking_url": "https://gls-group.eu"
                "/FR/fr/suivi-colis?"
                "match=009YYI19",
                "shipping_type_code": "L08",
                "shipping_type_label": "Colis suivi",
                "shipping_zone_code": "BEL",
                "shipping_zone_label": "Belgique",
                "total_commission": 15.66,
                "total_price": 86.98,
                "transaction_date": "2016-11-18T15:30:57.000Z",
            },
        ]
