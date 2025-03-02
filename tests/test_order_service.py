import unittest
import tests.test_utils as test_utils
from src.database import init_db
from src.services import user_service, product_service, order_service

class TestOrderService(unittest.TestCase):
    test_utils.baseSetUp()
    test_utils.tearDown()

    def setUp(self):
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

    def test_add_to_cart(self):
        # Add product to user's cart
        cart_item = order_service.add_to_cart(
            self.user, self.product.id, quantity=2, db_path=self.db_path
        )
        self.assertIsNotNone(cart_item.id)
        # Verify that the cart has the item
        cart_items = order_service.view_cart(self.user, db_path=self.db_path)
        self.assertEqual(len(cart_items), 1)

    def test_place_order(self):
        # Place the order and ensure cart is cleared
        order = order_service.place_order(self.user, db_path=self.db_path)
        self.assertIsNotNone(order.id)
        cart_items_after = order_service.view_cart(
            self.user, db_path=self.db_path
        )
        self.assertEqual(len(cart_items_after), 0)

    def test_place_order_empty_cart(self):
        with self.assertRaises(order_service.OrderServiceError):
            order_service.place_order(self.user, db_path=self.db_path)

if __name__ == '__main__':
    unittest.main()
