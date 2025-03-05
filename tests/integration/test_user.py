import json
import os
import tempfile
import unittest
from src import create_app
from db.database import init_db

class UserIntegrationTests(unittest.TestCase):
    def setUp(self):
        # Create a temporary database file.
        self.db_fd, self.db_path = tempfile.mkstemp()
        # Initialize the test database.
        init_db(self.db_path)
        # Create the Flask application configured for testing.
        self.app = create_app()
        self.app.config['TESTING'] = True
        # Override the database configuration to use the temporary DB.
        self.app.config['DATABASE'] = self.db_path
        self.client = self.app.test_client()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_user_already_registered_and_login(self):
        # Attempt to register a new user.
        register_response = self.client.post(
            '/users/register',
            json={
                "username": "integrationUser",
                "password": "testpass",
                "role": "regular"
            }
        )

        # Check if registration was successful or if the user already exists.
        if register_response.status_code == 201:
            register_data = json.loads(register_response.data)
            self.assertIn("id", register_data)
        else:
            # If registration fails, we assume it is because the user is already registered.
            self.assertEqual(register_response.status_code, 400)

        # Now attempt to log in with the same credentials.
        login_response = self.client.post(
            '/users/login',
            json={
                "username": "integrationUser",
                "password": "testpass"
            }
        )
        self.assertEqual(login_response.status_code, 200)
        login_data = json.loads(login_response.data)
        self.assertIn("id", login_data)

if __name__ == '__main__':
    unittest.main()
