import json
import os
import tempfile
import unittest
from src import create_app
from src.services .user_service import register_user
from db.database import init_db

class ProductIntegrationTests(unittest.TestCase):
    def setUp(self):
        # Create a temporary SQLite database.
        self.db_fd, self.db_path = tempfile.mkstemp()
        init_db(self.db_path)

        # Create the Flask app and configure for testing.
        self.app = create_app()
        self.app.config['TESTING'] = True
        # Override your DB config to point to the temporary DB.
        self.app.config['DATABASE'] = self.db_path
        self.client = self.app.test_client()

        # Register an admin user.
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
        
        # Register a regular user.
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
            "admin", "adminpass", "admin", db_path=self.db_path
        )

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_admin_add_edit_delete_products_and_regular_user_view(self):
        # Step 1: Admin adds 4 products.
        products_to_add = [
            {"name": "Product 1", "description": "Desc 1", "price": 10.0},
            {"name": "Product 2", "description": "Desc 2", "price": 20.0},
            {"name": "Product 3", "description": "Desc 3", "price": 30.0},
            {"name": "Product 4", "description": "Desc 4", "price": 40.0}
        ]
        added_products = []
        # Retrieve existing products from the DB.
        get_resp = self.client.get('/products')
        self.assertEqual(get_resp.status_code, 200)
        existing_products = json.loads(get_resp.data)

        for prod in products_to_add:
            # Check if a product with the same name is already registered.
            existing = next((p for p in existing_products if p["name"] == prod["name"]), None)
            if existing:
                added_products.append(existing)
            else:
                data_add_product = {"user_id": self.mock_admin_user.id, **prod}
                resp = self.client.post('/products/add', json=data_add_product)
                self.assertEqual(resp.status_code, 201)
                product_added = json.loads(resp.data)
                added_products.append(product_added)
                # Append newly added product to our existing_products list.
                existing_products.append(product_added)
        self.assertEqual(len(added_products), 4)

        # Step 2: Admin edits two products (Product 1 and Product 2).
        edit_data1 = {
            "user_id": self.mock_admin_user.id,
            "name": "Updated Product 1",
            "description": "Desc 1 Updated",
            "price": 15.0
        }
        resp_edit1 = self.client.put(f'/products/edit/{added_products[0]["id"]}', json=edit_data1)
        self.assertEqual(resp_edit1.status_code, 200)
        updated_product1 = json.loads(resp_edit1.data)
        self.assertEqual(updated_product1["name"], "Updated Product 1")
        self.assertEqual(updated_product1["price"], 15.0)

        edit_data2 = {
            "user_id": self.mock_admin_user.id,
            "name": "Updated Product 2",
            "description": "Desc 2 Updated",
            "price": 25.0
        }
        resp_edit2 = self.client.put(f'/products/edit/{added_products[1]["id"]}', json=edit_data2)
        self.assertEqual(resp_edit2.status_code, 200)
        updated_product2 = json.loads(resp_edit2.data)
        self.assertEqual(updated_product2["name"], "Updated Product 2")
        self.assertEqual(updated_product2["price"], 25.0)

        # Step 3: Admin deletes one product (Product 3).
        delete_data = {"user_id": self.mock_admin_user.id}
        resp_delete = self.client.delete(f'/products/delete/{added_products[2]["id"]}', json=delete_data)
        self.assertEqual(resp_delete.status_code, 200)

        # Step 4: Regular user views all products.
        resp_view = self.client.get('/products')
        self.assertEqual(resp_view.status_code, 200)
        products_viewed = json.loads(resp_view.data)

        # Assert that Product 3 (deleted) is not in the list.
        product_ids = [prod["id"] for prod in products_viewed]
        self.assertNotIn(added_products[2]["id"], product_ids)

        # Assert that the updated products are present with their changes.
        for prod in products_viewed:
            if prod["id"] == updated_product1["id"]:
                self.assertEqual(prod["name"], "Updated Product 1")
                self.assertEqual(prod["price"], 15.0)
            if prod["id"] == updated_product2["id"]:
                self.assertEqual(prod["name"], "Updated Product 2")
                self.assertEqual(prod["price"], 25.0)

if __name__ == '__main__':
    unittest.main()
