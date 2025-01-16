from odoo.tests import TransactionCase


class TestSaleChannel(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create base test data
        cls.channel_1 = cls.env["sale.channel"].create({"name": "Test Channel 1"})
        cls.channel_2 = cls.env["sale.channel"].create({"name": "Test Channel 2"})
        # Create root categories
        cls.root_categ_1 = cls.env["product.category"].create(
            {"name": "Root Category 1"}
        )
        cls.root_categ_2 = cls.env["product.category"].create(
            {"name": "Root Category 2"}
        )

    def test_01_root_categ_assignment(self):
        """Test assigning root categories to sale channel"""
        # Assign root categories to channel
        self.channel_1.write(
            {"root_categ_ids": [(6, 0, [self.root_categ_1.id, self.root_categ_2.id])]}
        )

        # Check if categories are properly assigned
        self.assertEqual(len(self.channel_1.root_categ_ids), 2)
        self.assertIn(self.root_categ_1, self.channel_1.root_categ_ids)
        self.assertIn(self.root_categ_2, self.channel_1.root_categ_ids)

    def test_02_channel_propagation_to_child_categories(self):
        """Test channel propagation to child categories"""
        # Create child categories
        child_categ = self.env["product.category"].create(
            {"name": "Child Category", "parent_id": self.root_categ_1.id}
        )

        grandchild_categ = self.env["product.category"].create(
            {"name": "Grandchild Category", "parent_id": child_categ.id}
        )

        # Assign channel to root category
        self.channel_1.write({"root_categ_ids": [(6, 0, [self.root_categ_1.id])]})

        # Check if channel is propagated to child categories
        self.assertEqual(child_categ.channel_ids, self.channel_1)
        self.assertEqual(grandchild_categ.channel_ids, self.channel_1)

    def test_03_multiple_channel_assignment(self):
        """Test assigning multiple channels to categories"""
        # Assign both channels to root category
        self.channel_1.write({"root_categ_ids": [(6, 0, [self.root_categ_1.id])]})
        self.channel_2.write({"root_categ_ids": [(6, 0, [self.root_categ_1.id])]})

        # Create child category
        child_categ = self.env["product.category"].create(
            {"name": "Child Category", "parent_id": self.root_categ_1.id}
        )

        # Check if both channels are properly assigned
        self.assertEqual(len(child_categ.channel_ids), 2)
        self.assertIn(self.channel_1, child_categ.channel_ids)
        self.assertIn(self.channel_2, child_categ.channel_ids)

    def test_04_channel_removal(self):
        """Test removing channels from categories"""
        # First assign channel
        self.channel_1.write({"root_categ_ids": [(6, 0, [self.root_categ_1.id])]})

        # Create child category
        child_categ = self.env["product.category"].create(
            {"name": "Child Category", "parent_id": self.root_categ_1.id}
        )

        # Remove channel
        self.channel_1.write({"root_categ_ids": [(5, 0, 0)]})

        # Check if channel is removed from both categories
        self.assertFalse(self.root_categ_1.channel_ids)
        self.assertFalse(child_categ.channel_ids)

    def test_05_create_channel_with_categories(self):
        """Test creating channel with categories"""
        new_channel = self.env["sale.channel"].create(
            {"name": "New Channel", "root_categ_ids": [(6, 0, [self.root_categ_1.id])]}
        )

        # Check if categories are properly assigned
        self.assertEqual(len(new_channel.root_categ_ids), 1)
        self.assertIn(self.root_categ_1, new_channel.root_categ_ids)

        # Check if channel is assigned to category
        self.assertIn(new_channel, self.root_categ_1.channel_ids)

    def test_06_recursive_category_creation(self):
        """Test channel inheritance when creating categories recursively"""
        # Assign channel to root category
        self.channel_1.write({"root_categ_ids": [(6, 0, [self.root_categ_1.id])]})

        # Create multiple levels of categories at once
        categories = self.env["product.category"].create(
            [
                {
                    "name": "Child Category",
                    "parent_id": self.root_categ_1.id,
                },
                {
                    "name": "Grandchild Category",
                    "parent_id": self.root_categ_1.id,
                },
            ]
        )

        # Check if all categories inherited the channel
        for category in categories:
            self.assertEqual(category.channel_ids, self.channel_1)
