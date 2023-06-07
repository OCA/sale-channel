# Copyright 2022 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.fields import Command

from odoo.addons.connector_search_engine.tests.test_all import TestBindingIndexBase
from odoo.addons.product.tests.common import ProductAttributesCommon


class IndexProduct(ProductAttributesCommon, TestBindingIndexBase):
    @classmethod
    def _create_product_template(cls, channels=None):
        vals = {
            "name": "Indexable Product",
            "categ_id": cls.product_category.id,
            "attribute_line_ids": [
                Command.create(
                    {
                        "attribute_id": cls.size_attribute.id,
                        "value_ids": [
                            Command.set(
                                [
                                    cls.size_attribute_s.id,
                                    cls.size_attribute_m.id,
                                    cls.size_attribute_l.id,
                                ]
                            )
                        ],
                    }
                ),
            ],
        }
        if channels:
            vals["channel_ids"] = [Command.set(channels.ids)]
        return cls.env["product.template"].create(vals)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.search_engine = cls.env["se.backend"].create(
            {
                "name": "Fake SE",
                "tech_name": "fake_se",
                "backend_type": "fake",
                "index_ids": [
                    Command.create(
                        {
                            "name": "Product Index",
                            "model_id": cls.env["ir.model"]
                            .search([("model", "=", "product.product")], limit=1)
                            .id,
                            "lang_id": cls.env.ref("base.lang_en").id,
                            "serializer_type": "fake",
                        }
                    )
                ],
            }
        )
        cls.channels = cls.env["sale.channel"].create(
            {
                "name": "My super shop",
                "search_engine_id": cls.search_engine.id,
            }
        )
        cls.product_index = cls.search_engine.index_ids[0]

    def test_create_with_channel(self):
        product_template = self._create_product_template(self.channels)
        bindings = product_template.product_variant_ids._get_bindings()
        self.assertEqual(len(bindings), 3)
        self.assertEqual(bindings.index_id, self.product_index)

    def test_add_channel(self):
        product_template = self._create_product_template()
        self.assertFalse(product_template.product_variant_ids._get_bindings())
        product_template.channel_ids = self.channels
        bindings = product_template.product_variant_ids._get_bindings()
        self.assertEqual(len(bindings), 3)
        self.assertEqual(bindings.index_id, self.product_index)

    def test_remove_channel(self):
        product_template = self._create_product_template(self.channels)
        product_template.channel_ids = None
        bindings = product_template.product_variant_ids._get_bindings()
        self.assertEqual({"to_delete"}, set(bindings.mapped("state")))

    def test_inactive_and_active(self):
        product_template = self._create_product_template(self.channels)
        bindings = product_template.product_variant_ids._get_bindings()
        product_template.active = False
        self.assertEqual({"to_delete"}, set(bindings.mapped("state")))

        product_template.active = True
        self.assertEqual({"to_recompute"}, set(bindings.mapped("state")))
