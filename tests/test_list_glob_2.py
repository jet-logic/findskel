#!/bin/env python3
import unittest
import os
import tempfile
import subprocess
from pathlib import Path


class TestListCommand(unittest.TestCase):

    def run_list_command(self, *args):
        """Helper method to run the list command, print command and output"""
        cmd = [str(x) for x in ["python", "-m", "scan_dir_skel.list", *args]]

        # Print the command being executed
        print("\n\033[1mExecuting command:\033[0m")
        print(" ".join(cmd))

        # Run the command and capture output
        result = subprocess.run(cmd, capture_output=True, text=True)

        # Print the output
        print("\n\033[1mCommand output:\033[0m")
        print(result.stdout)
        if result.stderr:
            print("\n\033[1mCommand error output:\033[0m")
            print(result.stderr)

        return result.stdout.splitlines()

    # @unittest.skip("Enable to test basic listing")
    def test_basic_listing(self):

        with tempfile.TemporaryDirectory() as tmp:
            top = Path(tmp)
            ensure(top.joinpath("A", "B", "C", "img1.png"))
            ensure(top.joinpath("A", "B", "img2.png"))
            ensure(top.joinpath("A", "img3.png"))
            ###
            lines = self.run_list_command(top, "--include", "*.png")
            for x in lines:
                self.assertRegex(x, r".+(?:/A/img3.png|/A/B/C/img1.png|/A/B/img2.png)$")
            ###
            p1 = ensure(top.joinpath("A", "paths"))
            p1.write_text(str(top.joinpath("A", "B", "C")) + "\n#" + str(top.joinpath("A")))
            lines = self.run_list_command("--include", "*.png", "--paths-from", p1)
            self.assertEqual(len(lines), 1)
            for x in lines:
                self.assertRegex(x, r".+(?:/A/B/C/img1.png)$")
            ###
            p1 = ensure(top.joinpath("A", "paths"))
            p1.write_text(str(top.joinpath("A", "B", "img2.png")) + "\n#" + str(top.joinpath("A")))
            lines = self.run_list_command("--include", "*.png", "--paths-from", p1)
            self.assertEqual(len(lines), 1)
            for x in lines:
                self.assertRegex(x, r".+(?:/A/B/img2.png)$")

    def test_basic_globs(self):
        ## test_basic_globs
        with tempfile.TemporaryDirectory() as tmp:
            top = Path(tmp)
            ensure(top / "file.txt")
            ensure(top / "image.txt")
            ensure(top / "file.csv")
            for x in self.run_list_command(top, "--include", "*.txt"):
                self.assertRegex(x, r".+(?:/file.txt|/image.txt)$")
        ## test_basic_globs 2
        with tempfile.TemporaryDirectory() as tmp:
            top = Path(tmp)
            ensure(top / "file1.txt")
            ensure(top / "fileA.txt")
            ensure(top / "file.txt")
            ensure(top / "file12.txt")
            for x in self.run_list_command(top, "--include", "file?.txt"):
                self.assertRegex(x, r".+(?:/file1.txt|/fileA.txt)$")
        ## test_star_star_recursive
        with tempfile.TemporaryDirectory() as tmp:
            top = Path(tmp)
            ensure(top / "script.py")
            ensure(top / "src" / "script.py")
            ensure(top / "src" / "utils" / "script.py")
            ensure(top / "script.pyc")
            for x in self.run_list_command(top, "--include", "file?.txt"):
                self.assertRegex(x, r".+(?:/script\.py|/src/script\.py|/src/utils/script\.py)$")
        # test_character_classes
        with tempfile.TemporaryDirectory() as tmp:
            top = Path(tmp)
            ensure(top / "file1.txt")
            ensure(top / "file5.txt")
            ensure(top / "fileA.txt")
            ensure(top / "file10.txt")
            for x in self.run_list_command(top, "--include", "file[0-9].txt"):
                self.assertRegex(x, r".+(?:/file1\.txt|/file5\.txt)$")
            for x in self.run_list_command(top, "--include", "file[!0-9].txt"):
                self.assertRegex(x, r".+(?:/fileA\.txt|/file1\.txt)$")

        with tempfile.TemporaryDirectory() as tmp:
            top = Path(tmp)
            # Test trailing separator (directory only)
            ensure(top / "docs" / "file.txt")
            ensure(top / "public" / "docs")
            ensure(top / "tests" / "docs" / "docs")

            ls1 = self.run_list_command(top, "--include", "docs/")
            ls2 = [*map(str, [top / "docs", top / "tests" / "docs"])]
            # print(ls1, ls2)
            self.assertEqual(set(ls1), set(ls2))
            ensure(top / "A" / "log" / "app.log")
            ensure(top / "B" / "log" / "app.log")
            ensure(top / "C" / "log" / "app.log")
            # Test root anchoring
            ls1 = self.run_list_command(top, "--include", "/A/log/*.log")
            ls2 = [*map(str, [top / "A" / "log" / "app.log"])]
            self.assertEqual(set(ls1), set(ls2))
            ls1 = self.run_list_command(top, "--include", "/C/log/*.log")
            ls2 = [*map(str, [top / "C" / "log" / "app.log"])]
            self.assertEqual(set(ls1), set(ls2))

            # Pattern with special regex chars
            ensure(top / "file.(txt|csv)")
            ensure(top / "file.txt")
            ensure(top / "file^.md")
            ensure(top / "file6.md")
            ensure(top / "file9.md")
            ls1 = self.run_list_command(top, "--include", "file.(txt|csv)")
            ls2 = [*map(str, [top / "file.(txt|csv)"])]
            self.assertEqual(set(ls1), set(ls2))
            ls1 = self.run_list_command(top, "--include", "file[^79].md")
            ls2 = [*map(str, [top / "file^.md", top / "file9.md"])]
            self.assertEqual(set(ls1), set(ls2))
            # Pattern with backslashes (Windows paths)
            ensure(top / "C:\\Windows\\notepad.exe")
            ensure(top / "C:\\Program Files\\notepad.exe")
            ls1 = self.run_list_command(top, "--include", "C:\\Windows\\*.exe")
            ls2 = [*map(str, [top / "C:\\Windows\\notepad.exe"])]
            self.assertEqual(set(ls1), set(ls2))


def ensure(x: Path):
    x.parent.mkdir(parents=True, exist_ok=True)
    x.touch()
    return x


if __name__ == "__main__":
    unittest.main()
