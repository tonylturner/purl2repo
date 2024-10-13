import unittest

# Import the test modules for each package manager
from .test_pypi_parser import TestPyPiParser
from .test_npm_parser import TestNpmParser
from .test_cargo_parser import TestCargoParser


# Create a test suite that aggregates all test cases
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPyPiParser))
    suite.addTest(unittest.makeSuite(TestNpmParser))
    suite.addTest(unittest.makeSuite(TestCargoParser))
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(suite())
