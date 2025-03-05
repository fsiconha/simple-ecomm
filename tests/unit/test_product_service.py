import os
import unittest
import tempfile
from db.database import init_db
from src.services import user_service, product_service

class TestProductService(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        init_db(self.db_path)
        # Create an admin and a regular user
        self.admin = user_service.register_user(
            "admin", "adminpass", "admin", db_path=self.db_path
        )
        self.regular = user_service.register_user(
            "user", "userpass", "regular", db_path=self.db_path
        )

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def mock_add_product(self):
        product = product_service.add_product(
            self.admin,
            "Notebook",
            "Gaming laptop",
            1500.00,
            db_path=self.db_path
        )
        return product

    def test_add_product_admin(self):
        product = self.mock_add_product()
        self.assertIsNotNone(product.id)
        self.assertEqual(product.name, "Notebook")

    def test_add_product_non_admin(self):
        with self.assertRaises(product_service.ProductServiceError):
            product_service.add_product(
                self.regular,
                "Phone",
                "Smartphone",
                800.00,
                db_path=self.db_path
            )

    def test_edit_product(self):
        product = self.mock_add_product()
        updated_product = product_service.edit_product(
            self.admin, product.id, price=1400.00, db_path=self.db_path
        )
        self.assertEqual(updated_product.price, 1400.00)

    def test_delete_product(self):
        product = self.mock_add_product()
        product_service.delete_product(
            self.admin, product.id, db_path=self.db_path
        )
        self.assertIsNone(
            product_service.get_product_by_id(product.id, db_path=self.db_path)
        )

if __name__ == '__main__':
    unittest.main()
