#  Copyright (c) Akretion 2020
#  License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)
from psycopg2 import IntegrityError

from odoo.tests import TransactionCase


class TestConstraints(TransactionCase):
    def setUp(self):
        super().setUp()
        self.binding = self.env.ref(
            "sale_channel_partner.sale_channel_partner_willie_ebay"
        )

    def test_constraint_channel_extid(self):
        new_partner = self.env.ref("base.res_partner_address_31")
        with self.assertRaises(IntegrityError):
            self.binding.copy({"partner_id": new_partner.id})

    def test_constraint_channel_partner(self):
        with self.assertRaises(IntegrityError):
            self.binding.copy({"external_id": "new external id"})
