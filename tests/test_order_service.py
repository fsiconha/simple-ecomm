import json
import os
import unittest
import tempfile
from db.database import init_db
from src.services import user_service, product_service, order_service

class TestOrderService(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        init_db(self.db_path)
        # Create users and add a product (via admin)
        self.admin = user_service.register_user(
            "admin", "adminpass", "admin", db_path=self.db_path
        )
        self.user_1 = user_service.register_user(
            "user_1", "userpass", "regular", db_path=self.db_path
        )
        self.user_2 = user_service.register_user(
            "user_2", "userpass", "regular", db_path=self.db_path
        )
        self.product_1 = product_service.add_product(
            self.admin, "Laptop", "Gaming laptop", 1500.00, db_path=self.db_path
        )
        self.product_2 = product_service.add_product(
            self.admin, "Watch", "Sports smartwatch", 600.00, db_path=self.db_path
        )
        self.cart_1 = order_service.add_to_cart(
            self.user_1,
            [
                (self.product_1.id, 3),
            ],
            db_path=self.db_path
        )
        self.cart_2 = order_service.add_to_cart(
            self.user_2,
            [
                (self.product_1.id, 1),
                (self.product_2.id, 3),
            ],
            db_path=self.db_path
        )

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_add_to_cart(self):
        # Add product to user's cart
        cart = self.cart_1
        self.assertIsNotNone(cart.id)

    def test_view_cart(self):
        # Add product to the user's cart first.
        cart_with_one_item = self.cart_1
        cart_items = order_service.view_cart(
            cart=cart_with_one_item, user=self.user_1, db_path=self.db_path
        )
        # Assert that the returned value is a list with one item.
        self.assertIsInstance(cart_items, list)
        self.assertEqual(len(cart_items), 1)
        # Assert that the first item contains the expected product_id and product_quantity.
        self.assertEqual(cart_items[0]['product_id'], self.product_1.id)
        self.assertEqual(cart_items[0]['product_quantity'], 3)

        cart_with_two_items = self.cart_2
        cart_items = order_service.view_cart(
            cart=cart_with_two_items, user=self.user_2, db_path=self.db_path
        )
        # Assert that the returned value is a list with one item.
        self.assertIsInstance(cart_items, list)
        self.assertEqual(len(cart_items), 2)
        self.assertEqual(cart_items[1]['product_id'], self.product_2.id)

    def test_clean_cart(self):
        cart_with_product = self.cart_1
        order_service.clean_cart(
            cart=cart_with_product, user=self.user_1, db_path=self.db_path
        )
        # Verify that the user's cart has been cleared.
        cart_items_after_clean = order_service.view_cart(
            cart=cart_with_product, user=self.user_1, db_path=self.db_path
        )
        self.assertEqual(len(cart_items_after_clean), 0)

    def test_place_order(self):
        # Add product to user's cart and capture the cart item.
        cart_with_one_item = self.cart_1
        # Place the order.
        order = order_service.place_order(
            cart=cart_with_one_item, user=self.user_1, db_path=self.db_path
        )
        # Assert that an order record was created.
        self.assertIsNotNone(order.id)
        # Assert the content of the order
        order_products = json.loads(order.products)
        self.assertIsNotNone(order.products)
        self.assertIsInstance(order_products, list)
        self.assertEqual(order_products[0]["product_quantity"], 3)

    def test_place_order_empty_cart(self):
        # Clear the cart to ensure it's empty.
        order_service.clean_cart(
            cart=self.cart_1, user=self.user_1, db_path=self.db_path
        )
        with self.assertRaises(order_service.OrderServiceError):
            order_service.place_order(
                cart=self.cart_1, user=self.user_1, db_path=self.db_path
            )

if __name__ == '__main__':
    unittest.main()
