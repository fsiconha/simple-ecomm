import unittest
import tests.test_utils as test_utils
from source.database import init_db
from source.services import user_service

class TestUserService(unittest.TestCase):
    test_utils.baseSetUp()
    test_utils.tearDown()

    def test_register_user(self):
        # Register a new user
        user = user_service.register_user(
            "testuser", "password123", "regular", db_path=self.db_path
        )
        self.assertIsNotNone(user.id)

    def test_login_user(self):
        # Log in with correct credentials
        logged_in_user = user_service.login_user(
            "testuser", "password123", db_path=self.db_path
        )
        self.assertEqual(user.id, logged_in_user.id)
        self.assertEqual(user.username, logged_in_user.username)

    def test_register_duplicate_user(self):
        user_service.register_user(
            "testuser", "password123", "regular", db_path=self.db_path
        )
        with self.assertRaises(user_service.UserServiceError):
            user_service.register_user(
                "testuser", "newpassword", "regular", db_path=self.db_path
            )

    def test_invalid_login(self):
        user_service.register_user(
            "testuser", "password123", "regular", db_path=self.db_path
        )
        with self.assertRaises(user_service.UserServiceError):
            user_service.login_user(
                "testuser", "wrongpassword", db_path=self.db_path
            )

if __name__ == '__main__':
    unittest.main()
