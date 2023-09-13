# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from uuid import uuid4

from odoo.fields import Command

from odoo.addons.connector_search_engine.tests.test_all import TestBindingIndexBase


class TestChannel(TestBindingIndexBase):
    @classmethod
    def _create_sale_channel_with_search_engine(cls, name):
        search_engine = cls.env["se.backend"].create(
            {
                "name": "Fake SE",
                "tech_name": uuid4(),
                "backend_type": "fake",
                "index_ids": [
                    Command.create(
                        {
                            "name": "Categ Index",
                            "model_id": cls.env["ir.model"]
                            .search([("model", "=", "product.category")], limit=1)
                            .id,
                            "lang_id": cls.env.ref("base.lang_en").id,
                            "serializer_type": "fake",
                        }
                    )
                ],
            }
        )
        return cls.env["sale.channel"].create(
            {
                "name": name,
                "search_engine_id": search_engine.id,
            }
        )

    @classmethod
    def create_categ(cls, name, parent=None, channels=None):
        vals = {"name": name}
        if parent:
            vals["parent_id"] = parent.id
        if channels:
            vals["channel_ids"] = channels.ids
        return cls.env["product.category"].create(vals)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.channel_1 = cls._create_sale_channel_with_search_engine("Channel 1")
        cls.channel_2 = cls._create_sale_channel_with_search_engine("Channel 2")
        cls.channels = cls.channel_1 + cls.channel_2

        cls.categ_root = cls.create_categ("Root", channels=cls.channels)
        cls.categ_level_1 = cls.create_categ("Level 1", cls.categ_root)
        cls.categ_level_2 = cls.create_categ("Level 2", cls.categ_level_1)

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
