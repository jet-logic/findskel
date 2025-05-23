#!/bin/env python3
import unittest
import re

from scan_dir_skel.list import globre3


def globre2(g="", base="", seps=""):
    from re import escape

    if seps:
        SEP = seps[0]
    else:
        from os.path import altsep, sep

        seps = set(x for x in (sep, altsep) if x)
        SEP = sep
    # print(seps)

    NOT_SEP = f"[^{"".join(escape(x) for x in seps)}]"
    IS_SEP = f"[{"".join(escape(x) for x in seps)}]"
    if g.endswith(SEP):
        g = g[0:-1]
        dir_only = True
    else:
        dir_only = False

    i = g.find(SEP)
    if i < 0:
        anchor_root = False
    elif i == 0:
        anchor_root = True
        g = g[1:]
    else:
        anchor_root = None
    i, n = 0, len(g)
    res = ""
    while i < n:
        c = g[i]
        i = i + 1
        if c == "*":
            if i < n and "*" == g[i]:
                i = i + 1
                res = res + ".*"

                while i < n and g[i] in seps:
                    # print("**", g[i])
                    i = i + 1
            else:
                res = res + NOT_SEP + "+"
        elif c == "?":
            res = res + NOT_SEP
        elif c == "[":
            j = i
            if j < n and g[j] == "!":
                j = j + 1
            if j < n and g[j] == "]":
                j = j + 1
            while j < n and g[j] != "]":
                j = j + 1
            if j >= n:
                res = res + "\\["
            else:
                stuff = g[i:j].replace("\\", "\\\\")
                i = j + 1
                if stuff[0] == "!":
                    stuff = "^" + stuff[1:]
                elif stuff[0] == "^":
                    stuff = "\\" + stuff
                res = "%s[%s]" % (res, stuff)
        else:
            res = res + escape(c)
    if dir_only:
        END = escape(SEP) + r"\Z"
    else:
        END = r"\Z"
    if anchor_root:
        if base:
            res = escape(base) + SEP + res + END
        else:
            res = res + END
    else:
        OR_SEP = f"(?:|.+{IS_SEP})"
        if base:
            # res = r"(?ms)\A" + escape(base) + OR_SEP + res + END
            res = r"(?ms)\A" + escape(base) + ".*" + res + END
        else:
            res = res + END
    return res


def match3(pattern, base=""):
    from re import escape, compile as regex

    (neg, rex, dir_only, g) = globre3(pattern, base, escape)
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
        def compile_match(pattern, base=""):
            p = globre2(pattern, base)
            print(pattern, p)
            return re.compile(p).fullmatch

        self.match = compile_match
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

    def test_with_base_path(self):
        match = self.match("*.config", base="/etc")
        self.assertTrue(match("/etc/app.config"))
        self.assertTrue(match("/etc/system.config"))
        self.assertFalse(match("app.config"))  # Not in base
        self.assertFalse(match("/var/etc/app.config"))  # Wrong base

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
        self.assertFalse(match("read.txp"))
        self.assertTrue(match("./read.txt"))
        self.assertTrue(match("tora/uma/read.txt"))


if __name__ == "__main__":
    unittest.main()
