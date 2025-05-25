#!/bin/env python3
import unittest

from scan_dir_skel.scantree import sizerangep


def size_range_check(s=""):
    a, b = sizerangep(s)
    return lambda n: n >= a and n <= b


class TestSizerangep(unittest.TestCase):
    def test_empty_range(self):
        """Test empty range (matches all sizes)"""
        fn = size_range_check()
        self.assertTrue(fn(0))
        self.assertTrue(fn(100))
        self.assertTrue(fn(float("inf")))

    def test_single_value(self):
        """Test single value range (exact size match)"""
        fn = size_range_check("1k")
        self.assertFalse(fn(1023))  # Below 1k
        self.assertTrue(fn(1024))  # Exactly 1k
        self.assertFalse(fn(1025))  # Above 1k

    def test_range_with_both_ends(self):
        """Test range with both start and end"""
        fn = size_range_check("1k..2k")
        self.assertFalse(fn(1023))  # Below range
        self.assertTrue(fn(1024))  # Lower bound
        self.assertTrue(fn(1536))  # Within range
        self.assertTrue(fn(2048))  # Upper bound
        self.assertFalse(fn(2049))  # Above range

    def test_range_with_lower_bound_only(self):
        """Test range with only lower bound"""
        fn = size_range_check("1m..")
        self.assertFalse(fn(1024 * 1024 - 1))  # Just below 1m
        self.assertTrue(fn(1024 * 1024))  # Exactly 1m
        self.assertTrue(fn(10 * 1024 * 1024))  # Well above 1m
        self.assertTrue(fn(float("inf")))  # Infinite size

    def test_range_with_upper_bound_only(self):
        """Test range with only upper bound"""
        fn = size_range_check("..1g")
        self.assertTrue(fn(0))  # Minimum size
        self.assertTrue(fn(1024 * 1024 * 1024))  # Exactly 1g
        self.assertFalse(fn(1024 * 1024 * 1024 + 1))  # Just above 1g

    def test_different_units(self):
        """Test ranges with different units"""
        fn = size_range_check("1k..1m")
        self.assertTrue(fn(1024))  # 1k
        self.assertTrue(fn(512 * 1024))  # 0.5m
        self.assertTrue(fn(1024 * 1024))  # 1m
        self.assertFalse(fn(1024 * 1024 + 1))  # Just above 1m

    def test_edge_cases(self):
        """Test various edge cases"""
        # Zero size
        fn = size_range_check("0..1k")
        self.assertTrue(fn(0))
        self.assertTrue(fn(512))
        self.assertFalse(fn(1025))

        # Very large range
        fn = size_range_check("1k..1t")
        self.assertTrue(fn(1024))
        self.assertTrue(fn(1024**4))

        # Decimal values
        fn = size_range_check("1.5k..2.5k")
        self.assertFalse(fn(1.5 * 1024 - 1))
        self.assertTrue(fn(1.5 * 1024))
        self.assertTrue(fn(2.5 * 1024))
        self.assertFalse(fn(2.5 * 1024 + 1))

    def test_invalid_formats(self):
        """Test invalid range formats"""
        with self.assertRaises(ValueError):
            size_range_check("invalid")

        with self.assertRaises(ValueError):
            size_range_check("1k..invalid")

        with self.assertRaises(ValueError):
            size_range_check("invalid..1k")


if __name__ == "__main__":
    unittest.main()
