import os
import unittest
import tempfile
from db.database import init_db
from src.services import user_service

class TestUserService(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        init_db(self.db_path)

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def mock_register_user(self):
        user = user_service.register_user(
            "testuser", "password123", "regular", db_path=self.db_path
        )
        return user

    def test_register_user(self):
        # Register a new user
        user = self.mock_register_user()
        self.assertIsNotNone(user.id)

    def test_login_user(self):
        user = self.mock_register_user()
        # Log in with correct credentials
        logged_in_user = user_service.login_user(
            "testuser", "password123", db_path=self.db_path
        )
        self.assertEqual(user.username, logged_in_user.username)
        self.assertEqual(user.password, logged_in_user.password)

    def test_register_duplicate_user(self):
        user = self.mock_register_user()
        with self.assertRaises(user_service.UserServiceError):
            user_service.register_user(
                "testuser", "newpassword", "regular", db_path=self.db_path
            )

    def test_invalid_login(self):
        user = self.mock_register_user()
        with self.assertRaises(user_service.UserServiceError):
            user_service.login_user(
                "testuser", "wrongpassword", db_path=self.db_path
            )

if __name__ == '__main__':
    unittest.main()
