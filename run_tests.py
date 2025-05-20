#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import sys
import os

def main():
    # Add project root to sys.path to allow test modules to import project files
    project_root = os.path.abspath(os.path.dirname(__file__))
    sys.path.insert(0, project_root)

    # Create a TestLoader instance
    loader = unittest.TestLoader()

    # Discover tests in the 'tests' directory
    # The pattern 'test*.py' is the default for discover
    suite = loader.discover('tests')

    # Create a TextTestRunner instance with verbosity set to 2 for detailed output
    runner = unittest.TextTestRunner(verbosity=2)

    # Run the tests
    result = runner.run(suite)

    # Exit with an appropriate status code
    if result.wasSuccessful():
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()
