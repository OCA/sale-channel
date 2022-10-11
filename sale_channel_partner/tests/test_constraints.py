#  Copyright (c) Akretion 2020
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

# pylint: disable=missing-manifest-dependency

from psycopg2 import IntegrityError

from odoo.tests import TransactionCase
from odoo.tools import mute_logger


class TestConstraints(TransactionCase):
    def setUp(self):
        super().setUp()
        self.binding = self.env.ref(
            "sale_channel_partner.sale_channel_partner_willie_ebay"
        )

    def test_constraint_channel_extid(self):
        new_partner = self.env.ref("base.res_partner_address_31")
        with self.assertRaises(IntegrityError), mute_logger("odoo.sql_db"):
            self.binding.copy({"partner_id": new_partner.id})

    def test_constraint_channel_partner(self):
        with self.assertRaises(IntegrityError), mute_logger("odoo.sql_db"):
            self.binding.copy({"external_id": "new external id"})
