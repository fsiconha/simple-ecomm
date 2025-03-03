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
        self.user = user_service.register_user(
            "user", "userpass", "regular", db_path=self.db_path
        )
        self.product = product_service.add_product(
            self.admin, "Laptop", "Gaming laptop", 1500.00, db_path=self.db_path
        )

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def mock_add_to_cart(self):
        cart = order_service.add_to_cart(
            self.user, self.product.id, product_quantity=3, db_path=self.db_path
        )
        return cart

    def test_add_to_cart(self):
        # Add product to user's cart
        cart = self.mock_add_to_cart()
        self.assertIsNotNone(cart.id)

    def test_view_cart(self):
        # Add product to the user's cart first.
        self.mock_add_to_cart()
        cart_items = order_service.view_cart(self.user, db_path=self.db_path)
        # Assert that the returned value is a list with one item.
        self.assertIsInstance(cart_items, list)
        self.assertEqual(len(cart_items), 1)
        # Assert that the first item contains the expected product_id and product_quantity.
        self.assertEqual(cart_items[0]['product_id'], self.product.id)
        self.assertEqual(cart_items[0]['product_quantity'], 3)

    def test_place_order(self):
        # Add product to user's cart and capture the cart item.
        self.mock_add_to_cart()
        # Place the order.
        order = order_service.place_order(self.user, db_path=self.db_path)
        # Assert that an order record was created.
        self.assertIsNotNone(order.id)
        # Assert the content of the order
        order_products = json.loads(order.products)
        self.assertIsNotNone(order.products)
        self.assertIsInstance(order_products, list)
        # self.assertEqual(len(order_products), 3) ### RETURN TO INVESTIGATE
        # Verify that the user's cart has been cleared.
        cart_items_after = order_service.view_cart(self.user, db_path=self.db_path)
        self.assertEqual(len(cart_items_after), 0)

    def test_place_order_empty_cart(self):
        with self.assertRaises(order_service.OrderServiceError):
            order_service.place_order(self.user, db_path=self.db_path)

if __name__ == '__main__':
    unittest.main()
