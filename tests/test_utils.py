import os
import tempfile

def setUp(self):
    # Create a temporary database file
    self.db_fd, self.db_path = tempfile.mkstemp()
    init_db(self.db_path)

def tearDown(self):
    os.close(self.db_fd)
    os.unlink(self.db_path)
