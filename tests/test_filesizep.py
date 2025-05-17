#!/bin/env python3
import unittest

from scan_dir_skel.list import filesizep


class TestFilesizep(unittest.TestCase):
    def test_bytes(self):
        self.assertEqual(filesizep("1b"), 1)
        self.assertEqual(filesizep("1024b"), 1024)

    def test_kilobytes(self):
        self.assertEqual(filesizep("1k"), 1024)
        self.assertEqual(filesizep("2K"), 2048)
        self.assertEqual(filesizep("1.5k"), 1536)

    def test_megabytes(self):
        self.assertEqual(filesizep("1m"), 1048576)
        self.assertEqual(filesizep("2M"), 2097152)

    def test_gigabytes(self):
        self.assertEqual(filesizep("1g"), 1073741824)
        self.assertEqual(filesizep("3G"), 3221225472)

    def test_terabytes(self):
        self.assertEqual(filesizep("1t"), 1099511627776)

    def test_petabytes(self):
        self.assertEqual(filesizep("1p"), 1125899906842624)

    def test_exabytes(self):
        self.assertEqual(filesizep("1e"), 1152921504606846976)

    def test_zettabytes(self):
        self.assertEqual(filesizep("1z"), 1180591620717411303424)

    def test_yottabytes(self):
        self.assertEqual(filesizep("1y"), 1208925819614629174706176)

    def test_no_unit(self):
        self.assertEqual(filesizep("1024"), 1024.0)
        self.assertEqual(filesizep("3.14"), 3.14)

    def test_invalid_input(self):
        with self.assertRaises(ValueError):
            filesizep("abc")
        with self.assertRaises(ValueError):
            filesizep("k")
        with self.assertRaises(ValueError):
            filesizep("1x")  # invalid unit

    def test_case_insensitive(self):
        self.assertEqual(filesizep("1K"), 1024)
        self.assertEqual(filesizep("1kB"), 1024)
        self.assertEqual(filesizep("1Kb"), 1024)


if __name__ == "__main__":
    unittest.main()
