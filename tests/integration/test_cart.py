import json
import os
import tempfile
import unittest
from src import create_app
from src.services .user_service import register_user
from db.database import init_db

class CartIntegrationTests(unittest.TestCase):
    def setUp(self):
        # Create a temporary SQLite database.
        self.db_fd, self.db_path = tempfile.mkstemp()
        init_db(self.db_path)
        
        # Create the Flask app configured for testing.
        self.app = create_app()
        self.app.config['TESTING'] = True
        # Override the database configuration to use the temporary DB.
        self.app.config['DATABASE'] = self.db_path
        self.client = self.app.test_client()
        
        # Register an admin user (for adding products).
        admin_response = self.client.post(
            '/users/register',
            json={
                "username": "adminUser",
                "password": "adminpass",
                "role": "admin"
            }
        )
        if admin_response.status_code == 201:
            register_data = json.loads(admin_response.data)
            self.assertIn("id", register_data)
        else:
            # If registration fails, we assume it is because the user is already registered.
            self.assertEqual(admin_response.status_code, 400)
        
        # Register a regular user (for buying products).
        regular_response = self.client.post(
            '/users/register',
            json={
                "username": "regularUser",
                "password": "userpass",
                "role": "regular"
            }
        )
        if regular_response.status_code == 201:
            register_data = json.loads(regular_response.data)
            self.assertIn("id", register_data)
        else:
            # If registration fails, we assume it is because the user is already registered.
            self.assertEqual(regular_response.status_code, 400)

        self.mock_admin_user = register_user(
            "adminUser", "adminpass", "admin", db_path=self.db_path
        )

        self.mock_regular_user = register_user(
            "regularUser", "adminpass", "regular", db_path=self.db_path
        )

        # Admin adds six products.
        self.product_ids = []
        i = 0
        for i in range(6):
            product_data = {
                "user_id": self.mock_admin_user.id,
                "name": f"Product {i}",
                "description": f"Description {i}",
                "price": (i+1) * 10.0
            }
            prod_resp = self.client.post('/products/add', json=product_data)
            self.assertEqual(prod_resp.status_code, 201)
            prod = json.loads(prod_resp.data)
            self.product_ids.append(prod['id'])
            i+1

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_shopping_journey(self):
        # 1. Regular user views list of products.
        resp_products = self.client.get('/products')
        self.assertEqual(resp_products.status_code, 200)
        products = json.loads(resp_products.data)
        self.assertIsNotNone(products)
        
        # 2. Regular user selects three products (e.g., the first three)
        # and adds them to the cart with a quantity of 2 for each.
        items_to_add = []
        for pid in self.product_ids[:3]:
            items_to_add.append({"product_id": pid, "product_quantity": 2})
        add_cart_resp = self.client.post('/cart/add', json={
            "user_id": self.mock_regular_user.id,
            "items": items_to_add
        })
        self.assertEqual(add_cart_resp.status_code, 201)
        cart = json.loads(add_cart_resp.data)
        self.assertIn("cart_id", cart)
        # Ensure three items were added.
        self.assertEqual(len(cart["items"]), 3)
        cart_id = cart["cart_id"]

        # 3. Regular user places an order using the cart.
        order_resp = self.client.post('/cart/order', json={
            "user_id": self.mock_regular_user.id,
            "cart_id": cart_id
        })
        self.assertEqual(order_resp.status_code, 201)
        order = json.loads(order_resp.data)
        self.assertIn("order_id", order)
        self.assertEqual(order["user_id"], self.mock_regular_user.id)
        
        # The order's "products" field is expected to be a JSON string representing
        # the list of ordered products. Let's verify it.
        order_products = json.loads(order["products"])
        # We expect three items, each with a quantity of 2.
        self.assertEqual(len(order_products), 3)
        for item in order_products:
            self.assertEqual(item["product_quantity"], 2)

if __name__ == '__main__':
    unittest.main()
