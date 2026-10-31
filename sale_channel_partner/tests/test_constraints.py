#  Copyright (c) Akretion 2020
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

from psycopg2 import IntegrityError

from odoo.tests import TransactionCase
from odoo.tools import mute_logger


class TestConstraints(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.channel = cls.env["sale.channel"].create({"name": "Test Channel"})
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.other_partner = cls.env["res.partner"].create({"name": "Other Partner"})
        cls.binding = cls.env["sale.channel.partner"].create(
            {
                "sale_channel_id": cls.channel.id,
                "partner_id": cls.partner.id,
                "external_id": "external_id_1",
            }
        )

    def test_constraint_channel_extid(self):
        # (external_id, sale_channel_id) pairs must be unique
        with self.assertRaises(IntegrityError), mute_logger("odoo.sql_db"):
            self.binding.copy({"partner_id": self.other_partner.id})

    def test_constraint_channel_partner(self):
        # (partner_id, sale_channel_id) pairs must be unique
        with self.assertRaises(IntegrityError), mute_logger("odoo.sql_db"):
            self.binding.copy({"external_id": "new external id"})
