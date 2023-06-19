# Copyright 2023 Akretion (https://www.akretion.com).
# @author Raphaël Reverdy<raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestSaleChannel(TransactionCase):
    def setUp(self):
        super().setUp()
        self.sale_channel = self.env.ref("sale_channel.sale_channel_amazon")
        self.root = self.env.ref("sale_channel_product_category.product_category_root")
        self.sport = self.env.ref("sale_channel_product_category.product_category_1")
        self.sport_cycling_bike = self.env.ref(
            "sale_channel_product_category.product_category_1a1"
        )
        self.sport_cycling_bike_bmx = self.env.ref(
            "sale_channel_product_category.product_category_1a1a"
        )
        self.sport_cycling_bike_ebike = self.env.ref(
            "sale_channel_product_category.product_category_1a1b"
        )
        self.sport_cycling_bike_cargo = self.env.ref(
            "sale_channel_product_category.product_category_1a1c"
        )
        self.sport_cycling_spare_parts = self.env.ref(
            "sale_channel_product_category.product_category_1a2"
        )
        self.v2 = self.env.ref("sale_channel_product_category.product_douze_v2")

    def _channel_root_categ(self, root_categ):
        return self.env["sale.channel"].create(
            {
                "name": f"with category {root_categ.parent_path}",
                "root_category_id": root_categ.id,
            }
        )

    def test_categ_up_to_root_and_level(self):
        # nothing without ctx
        itself = 1
        self.assertEqual(self.sport_cycling_bike_bmx.level, 0)
        self.assertEqual(len(self.sport_cycling_bike_bmx.categs_up_to_root), 0)

        channel = self._channel_root_categ(self.root)
        bmx_with_ctx = self.sport_cycling_bike_bmx.with_context(channel_id=channel.id)
        # 1a1a is end of xmlid (one char per level)
        self.assertEqual(bmx_with_ctx.level, len("1a1a"[0:]))
        self.assertEqual(len(bmx_with_ctx.categs_up_to_root), itself + len("1a1a"[0:]))
        categs = set(
            (
                self.sport_cycling_bike_bmx
                | self.sport_cycling_bike
                | self.sport
                | self.root
            ).ids
        )
        self.assertTrue(categs.issubset(bmx_with_ctx.categs_up_to_root.ids))

        # with root/sport
        channel = self._channel_root_categ(self.sport)
        bmx_with_ctx = self.sport_cycling_bike_bmx.with_context(channel_id=channel.id)

        self.assertEqual(bmx_with_ctx.level, len("1a1a"[1:]))
        self.assertEqual(len(bmx_with_ctx.categs_up_to_root), itself + len("1a1a"[1:]))

        categs = set(
            (self.sport_cycling_bike_bmx | self.sport_cycling_bike | self.sport).ids
        )
        self.assertTrue(categs.issubset(bmx_with_ctx.categs_up_to_root.ids))
        self.assertFalse(
            set(self.root.ids).issubset(bmx_with_ctx.categs_up_to_root.ids)
        )

        # with root/sport/cycling/bike
        channel = self._channel_root_categ(self.sport_cycling_bike)
        bmx_with_ctx = self.sport_cycling_bike_bmx.with_context(channel_id=channel.id)
        self.assertEqual(bmx_with_ctx.level, len("1a1a"[3:]))
        self.assertEqual(
            len(bmx_with_ctx.categs_up_to_root), itself + len("1a1a"[3:])
        )  # 2

        categs = set((self.sport_cycling_bike_bmx | self.sport_cycling_bike).ids)
        self.assertTrue(categs.issubset(bmx_with_ctx.categs_up_to_root.ids))

        # with root/sport/cycling/bike/bmx
        channel = self._channel_root_categ(self.sport_cycling_bike_bmx)
        bmx_with_ctx = self.sport_cycling_bike_bmx.with_context(channel_id=channel.id)
        self.assertEqual(bmx_with_ctx.level, len("1a1a"[4:]))
        self.assertEqual(len(bmx_with_ctx.categs_up_to_root), itself + len("1a1a"[4:]))
        self.assertEqual(self.sport_cycling_bike_bmx, bmx_with_ctx.categs_up_to_root)

        # same level but not in the path
        channel = self._channel_root_categ(self.sport_cycling_bike_cargo)
        bmx_with_ctx = self.sport_cycling_bike_bmx.with_context(channel_id=channel.id)
        self.assertEqual(bmx_with_ctx.level, 0)
        self.assertEqual(len(bmx_with_ctx.categs_up_to_root), 0)

    def test_product(self):
        # no chanel
        self.assertTrue(len(self.v2.channel_categ_ids.ids) == 0)

        channel = self._channel_root_categ(self.root)
        # with root/sport/cycling/bike/cargo
        v2_with_ctx = self.v2.with_context(channel_id=channel.id)
        self.assertTrue(len(v2_with_ctx.channel_categ_ids.ids) == 1)
        self.assertEqual(v2_with_ctx.channel_categ_ids, self.sport_cycling_bike_cargo)

        channel = self._channel_root_categ(self.sport_cycling_bike)
        # with sport.cycling/bike/cargo
        v2_with_ctx = self.v2.with_context(channel_id=channel.id)
        self.assertTrue(len(v2_with_ctx.channel_categ_ids.ids) == 1)
        self.assertEqual(v2_with_ctx.channel_categ_ids, self.sport_cycling_bike_cargo)

        channel = self._channel_root_categ(self.sport_cycling_spare_parts)
        # with sport.cycling/spare_parts
        v2_with_ctx = self.v2.with_context(channel_id=channel.id)
        self.assertTrue(len(v2_with_ctx.channel_categ_ids.ids) == 0)

    def test_multi_categ(self):
        channel = self._channel_root_categ(self.root)

        # let's electrify our cargo
        self.v2.categ_ids = self.sport_cycling_bike_ebike

        self.assertEqual(
            self.v2._get_categories(),
            self.sport_cycling_bike_cargo | self.sport_cycling_bike_ebike,
        )

        # no chanel
        self.assertTrue(len(self.v2.channel_categ_ids.ids) == 0)

        # with ctx
        v2_with_ctx = self.v2.with_context(channel_id=channel.id)
        self.assertTrue(len(v2_with_ctx.channel_categ_ids.ids) == 2)
