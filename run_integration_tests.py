
import unittest

if __name__ == '__main__':
    tests = unittest.TestLoader().discover('tests/integration')
    unittest.TextTestRunner(verbosity=2).run(tests)
