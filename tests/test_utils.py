#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import unittest
import re

# Add project root to sys.path to allow importing utils
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import getRE, tr, method_exists

class TestUtils(unittest.TestCase):
    def test_getRE_compiles_pattern(self):
        # Test that getRE compiles a pattern and sets flags
        pattern = "some_pattern"
        regex_obj = getRE(pattern)
        self.assertIsInstance(regex_obj, type(re.compile('')))
        # Check for re.I and re.L flags by behavior
        self.assertTrue(regex_obj.match("SOME_PATTERN")) # re.I
        # Checking for re.L is a bit more complex and environment-dependent.
        # We'll assume it's set if getRE specifies it.
        # A more direct way to check flags in Python 3.7+ is regex_obj.flags
        if hasattr(regex_obj, 'flags'):
            self.assertTrue(regex_obj.flags & re.IGNORECASE)
            self.assertTrue(regex_obj.flags & re.LOCALE)

    def test_tr_translation(self):
        # Test basic translation
        self.assertEqual(tr("abc", "xyz", "a b c a"), "x y z x")
        # Test with characters not in fr
        self.assertEqual(tr("abc", "xyz", "a d c"), "x d z")
        # Test with empty word
        self.assertEqual(tr("abc", "xyz", ""), "")
        # Test with empty fr and to (should return word as is)
        self.assertEqual(tr("", "", "word"), "word")
        # Test with fr longer than to (should ignore extra fr chars)
        self.assertEqual(tr("abcde", "xyz", "a b c d e"), "x y z d e")
        # Test with to longer than fr (should ignore extra to chars)
        self.assertEqual(tr("abc", "xyzwv", "a b c"), "x y z")
        # Test with Greek characters (example)
        self.assertEqual(tr("αβγ", "abg", "α β γ"), "a b g")

    def test_method_exists(self):
        class MyClass:
            def my_method(self):
                pass
            
            my_prop = "not a method"

        instance = MyClass()

        # Assert true for an existing method
        self.assertTrue(method_exists(instance, "my_method"))
        # Assert false for a non-existent method
        self.assertFalse(method_exists(instance, "non_existent_method"))
        # Assert false for a property that is not a method
        self.assertFalse(method_exists(instance, "my_prop"))
        
        # Test with the class itself
        self.assertTrue(method_exists(MyClass, "my_method"))
        self.assertFalse(method_exists(MyClass, "non_existent_method"))
        self.assertFalse(method_exists(MyClass, "my_prop"))

if __name__ == '__main__':
    unittest.main()
