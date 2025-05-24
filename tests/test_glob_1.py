#!/bin/env python3
import unittest
import re

from scan_dir_skel.list import globre3


def match3(pattern, base=""):
    from re import escape, compile as regex

    (rex, dir_only, neg, g) = globre3(pattern, base, escape)
    reg = regex(rex)

    def fn(p=""):
        if dir_only:
            if not p.endswith("/"):
                return False
            p = p[0:-1]
        return reg.match(p) is not None

    return fn


class TestGlobre2(unittest.TestCase):
    def setUp(self):
        # Compile helper function
        self.match = match3

    def test_basic_globs(self):
        match = self.match("*.txt")
        self.assertTrue(match("file.txt"))
        self.assertTrue(match("image.txt"))
        self.assertFalse(match("file.csv"))
        # self.assertFalse(match("dir/file.txt"))  # * shouldn't match across separators

        match = self.match("file?.txt")
        self.assertTrue(match("file1.txt"))
        self.assertTrue(match("fileA.txt"))
        self.assertFalse(match("file.txt"))
        self.assertFalse(match("file12.txt"))

    def test_star_star_recursive(self):
        match = self.match("**/*.py")
        self.assertTrue(match("script.py"))
        self.assertTrue(match("src/script.py"))
        self.assertTrue(match("src/utils/script.py"))
        self.assertFalse(match("script.pyc"))

    def test_character_classes(self):
        match = self.match("file[0-9].txt")
        self.assertTrue(match("file1.txt"))
        self.assertTrue(match("file5.txt"))
        self.assertFalse(match("fileA.txt"))
        self.assertFalse(match("file10.txt"))

        match = self.match("file[!0-9].txt")
        self.assertTrue(match("fileA.txt"))
        self.assertFalse(match("file1.txt"))

    def test_path_handling(self):
        # Test trailing separator (directory only)
        match = self.match("docs/")
        self.assertTrue(match("docs/"))
        self.assertFalse(match("docs"))
        self.assertFalse(match("docs/file.txt"))

        # Test root anchoring
        match = self.match("/var/log/*.log", "/A")
        self.assertTrue(match("/A/var/log/app.log"))
        self.assertFalse(match("/B/var/log/app.log"))  # Not root-anchored
        self.assertFalse(match("/tmp/var/log/app.log"))

    def test_edge_cases(self):
        # Empty pattern
        match = self.match("")
        self.assertTrue(match(""))
        self.assertFalse(match("file"))

        # Pattern with special regex chars
        match = self.match("file.(txt|csv)")
        self.assertTrue(match("file.(txt|csv)"))  # Should be escaped
        self.assertFalse(match("file.txt"))

        # Pattern with backslashes (Windows paths)
        match = self.match("C:\\Windows\\*.exe")
        self.assertTrue(match("C:\\Windows\\notepad.exe"))
        self.assertFalse(match("C:\\Program Files\\notepad.exe"))

    def test_directory_matching(self):
        match = self.match("src/**/")
        self.assertTrue(match("src/utils/"))
        self.assertTrue(match("src/a/b/c/"))
        self.assertFalse(match("src"))
        self.assertFalse(match("src/file.txt"))
        # self.assertTrue(match("src/"))

    def test_at_start(self):
        match = self.match("/apple/*.txt")
        self.assertFalse(match("src/file.txt"))
        self.assertTrue(match("apple/file.txt"))
        self.assertFalse(match("citrus/file.txt"))
        self.assertFalse(match("file.txt"))

    def test_at_end_no_glob(self):
        match = self.match("read.txt")
        self.assertFalse(match("src/read.txp"))
        self.assertTrue(match("apple/read.txt"))
        self.assertTrue(match("read.txt"))
        self.assertFalse(match("bread.txt"))
        self.assertFalse(match("read.txp"))
        self.assertTrue(match("./read.txt"))
        self.assertTrue(match("tora/uma/read.txt"))
        self.assertFalse(match("tora/uma/bread.txt"))

    def test_with_base_path(self):
        match = self.match("*.config", base="/etc")
        self.assertTrue(match("/etc/app.config"))
        self.assertTrue(match("/etc/system.config"))
        self.assertFalse(match("app.config"))  # Not in base
        self.assertFalse(match("/var/etc/app.config"))  # Wrong base


if __name__ == "__main__":
    unittest.main()
