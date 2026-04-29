# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from uuid import uuid4

from odoo.fields import Command

from odoo.addons.connector_search_engine.tests.common import TestBindingIndexBase


class TestChannel(TestBindingIndexBase):
    def _create_sale_channel_with_search_engine(self, name):
        search_engine = self.env["se.backend"].create(
            {
                "name": "Fake SE",
                "tech_name": uuid4(),
                "backend_type": "fake",
                "index_ids": [
                    Command.create(
                        {
                            "name": "Categ Index",
                            "model_id": self.env["ir.model"]
                            .search([("model", "=", "product.category")], limit=1)
                            .id,
                            "lang_id": self.env.ref("base.lang_en").id,
                            "serializer_type": "fake",
                        }
                    )
                ],
            }
        )
        return self.env["sale.channel"].create(
            {
                "name": name,
                "search_engine_id": search_engine.id,
            }
        )

    def create_categ(self, name, parent=None, channels=None):
        vals = {"name": name}
        if parent:
            vals["parent_id"] = parent.id
        if channels:
            vals["channel_ids"] = channels.ids
        return self.env["product.category"].create(vals)

    def setUp(self):
        super().setUp()
        self.channel_1 = self._create_sale_channel_with_search_engine("Channel 1")
        self.channel_2 = self._create_sale_channel_with_search_engine("Channel 2")
        self.channels = self.channel_1 + self.channel_2

        self.categ_root = self.create_categ("Root", channels=self.channels)
        self.categ_level_1 = self.create_categ("Level 1", self.categ_root)
        self.categ_level_2 = self.create_categ("Level 2", self.categ_level_1)

    def test_create_categ(self):
        self.assertEqual(self.categ_level_1.channel_ids, self.channels)
        self.assertEqual(self.categ_level_2.channel_ids, self.channels)
        self.assertEqual(len(self.categ_level_1._get_bindings()), 2)
        self.assertEqual(len(self.categ_level_2._get_bindings()), 2)

    def test_add_parent(self):
        categ = self.create_categ("Root -1", channels=self.channel_1)
        self.categ_root.parent_id = categ
        self.assertEqual(self.categ_root.channel_ids, self.channel_1)
        self.assertEqual(self.categ_level_1.channel_ids, self.channel_1)
        self.assertEqual(self.categ_level_2.channel_ids, self.channel_1)
        for categ in [self.categ_root, self.categ_level_1, self.categ_level_2]:
            bindings = categ._get_bindings()
            self.assertEqual(len(bindings), 2)
            self.assertEqual(
                set(bindings.mapped("state")), {"to_recompute", "to_delete"}
            )

    def test_remove_parent(self):
        self.categ_level_1.parent_id = None
        self.assertEqual(self.categ_level_1.channel_ids, self.channels)
        self.assertEqual(self.categ_level_2.channel_ids, self.channels)

    def test_change_parent(self):
        categ = self.create_categ("Root 2", channels=self.channel_1)
        self.categ_level_1.parent_id = categ
        self.assertEqual(self.categ_level_1.channel_ids, self.channel_1)
        self.assertEqual(self.categ_level_2.channel_ids, self.channel_1)
        for categ in [self.categ_level_1, self.categ_level_2]:
            bindings = categ._get_bindings()
            self.assertEqual(len(bindings), 2)
            self.assertEqual(
                set(bindings.mapped("state")), {"to_recompute", "to_delete"}
            )

    def test_parent_remove_channel(self):
        self.categ_root.channel_ids = None
        self.assertFalse(self.categ_level_1.channel_ids)
        self.assertFalse(self.categ_level_2.channel_ids)
        for categ in [self.categ_level_1, self.categ_level_2]:
            bindings = categ._get_bindings()
            self.assertEqual(len(bindings), 2)
            self.assertEqual(set(bindings.mapped("state")), {"to_delete"})

    def test_parent_set_channel(self):
        # First remove
        self.categ_root.channel_ids = None
        # Set a channel
        self.categ_root.channel_ids = self.channel_1
        self.assertEqual(self.categ_level_1.channel_ids, self.channel_1)
        self.assertEqual(self.categ_level_2.channel_ids, self.channel_1)
        for categ in [self.categ_level_1, self.categ_level_2]:
            bindings = categ._get_bindings()
            self.assertEqual(len(bindings), 2)
            self.assertEqual(
                set(bindings.mapped("state")), {"to_recompute", "to_delete"}
            )

    def test_parent_change_channel(self):
        self.categ_root.channel_ids = self.channel_1
        self.assertEqual(self.categ_level_1.channel_ids, self.channel_1)
        self.assertEqual(self.categ_level_2.channel_ids, self.channel_1)
        for categ in [self.categ_level_1, self.categ_level_2]:
            bindings = categ._get_bindings()
            self.assertEqual(len(bindings), 2)
            self.assertEqual(
                set(bindings.mapped("state")), {"to_recompute", "to_delete"}
            )

    def test_add_from_channel(self):
        channel_3 = self._create_sale_channel_with_search_engine("Channel 3")
        channel_3.root_categ_ids = self.categ_root
        self.assertEqual(self.categ_root.channel_ids, self.channels | channel_3)
        self.assertEqual(self.categ_level_1.channel_ids, self.channels | channel_3)
        self.assertEqual(self.categ_level_2.channel_ids, self.channels | channel_3)
        for categ in [self.categ_root, self.categ_level_1, self.categ_level_2]:
            bindings = categ._get_bindings()
            self.assertEqual(len(bindings), 3)
            self.assertEqual(set(bindings.mapped("state")), {"to_recompute"})

    def test_remove_from_channel(self):
        self.channel_2.root_categ_ids = None
        self.assertEqual(self.categ_level_1.channel_ids, self.channel_1)
        self.assertEqual(self.categ_level_2.channel_ids, self.channel_1)
        for categ in [self.categ_root, self.categ_level_1, self.categ_level_2]:
            bindings = categ._get_bindings()
            self.assertEqual(len(bindings), 2)
            self.assertEqual(
                set(bindings.mapped("state")), {"to_recompute", "to_delete"}
            )
