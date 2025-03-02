import unittest
import tests.test_utils as test_utils
from src.database import init_db
from src.services import user_service, product_service

class TestProductService(unittest.TestCase):
    test_utils.baseSetUp()
    test_utils.tearDown()

    def setUp(self):
        # Create an admin and a regular user
        self.admin = user_service.register_user(
            "admin", "adminpass", "admin", db_path=self.db_path
        )
        self.regular = user_service.register_user(
            "user", "userpass", "regular", db_path=self.db_path
        )

    def test_add_product_admin(self):
        product = product_service.add_product(
            self.admin, "Laptop", "Gaming laptop", 1500.00, db_path=self.db_path
        )
        self.assertIsNotNone(product.id)
        self.assertEqual(product.name, "Laptop")

    def test_add_product_non_admin(self):
        with self.assertRaises(product_service.ProductServiceError):
            product_service.add_product(
                self.regular, "Phone", "Smartphone", 800.00, db_path=self.db_path
            )

    def test_edit_product(self):
        product = product_service.add_product(
            self.admin, "Laptop", "Gaming laptop", 1500.00, db_path=self.db_path
        )
        updated_product = product_service.edit_product(
            self.admin, product.id, price=1400.00, db_path=self.db_path
        )
        self.assertEqual(updated_product.price, 1400.00)

    def test_delete_product(self):
        product = product_service.add_product(
            self.admin, "Laptop", "Gaming laptop", 1500.00, db_path=self.db_path
        )
        product_service.delete_product(
            self.admin, product.id, db_path=self.db_path
        )
        self.assertIsNone(
            product_service.get_product_by_id(product.id, db_path=self.db_path)
        )

if __name__ == '__main__':
    unittest.main()
