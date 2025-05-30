#!/bin/env python3
import unittest
import os
import tempfile
import subprocess
from pathlib import Path

from findskel.findskel import globre3
from re import escape


Windows = os.environ.get("RUNNER_OS") == "Windows"


class TestListCommand(unittest.TestCase):

    def run_list_command(self, *args):
        """Helper method to run the list command, print command and output"""
        cmd = [str(x) for x in ["python", "-m", "findskel.list", *args]]

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
            f1 = ensure(top.joinpath("A", "B", "C", "img1.png"))
            f2 = ensure(top.joinpath("A", "B", "img2.png"))
            f3 = ensure(top.joinpath("A", "img3.png"))
            ###
            lines = self.run_list_command(top, "--include", "*.png")
            self.assertSetEqual(set(lines), set([str(x) for x in (f1, f2, f3)]))
            ###
            p1 = ensure(top.joinpath("A", "paths"))
            p1.write_text(str(top.joinpath("A", "B", "C")) + "\n#" + str(top.joinpath("A")))
            lines = self.run_list_command("--include", "*.png", "--paths-from", p1)
            self.assertSetEqual(set(lines), set([str(x) for x in (f1,)]))
            ###
            p1 = ensure(top.joinpath("A", "paths"))
            p1.write_text(str(top.joinpath("A", "B", "img2.png")) + "\n#" + str(top.joinpath("A")))
            lines = self.run_list_command("--include", "*.png", "--paths-from", p1)
            self.assertSetEqual(set(lines), set([str(x) for x in (f2,)]))

    def test_basic_globs(self):
        ## test_basic_globs
        with tempfile.TemporaryDirectory() as tmp:
            top = Path(tmp)
            f1 = ensure(top / "file.txt")
            f2 = ensure(top / "image.txt")
            f3 = ensure(top / "file.csv")
            ls = self.run_list_command(top, "--include", "*.txt")
            self.assertSetEqual(set(ls), set(str(x) for x in (f1, f2)))
        ## test_basic_globs 2
        with tempfile.TemporaryDirectory() as tmp:
            top = Path(tmp)
            f1 = ensure(top / "file1.txt")
            f2 = ensure(top / "fileA.txt")
            f3 = ensure(top / "file.txt")
            f4 = ensure(top / "file12.txt")
            ls = self.run_list_command(top, "--include", "file?.txt")
            self.assertSetEqual(set(ls), set(str(x) for x in (f1, f2)))
        ## test_star_star_recursive
        with tempfile.TemporaryDirectory() as tmp:
            top = Path(tmp)
            f1 = ensure(top / "script.py")
            f2 = ensure(top / "src" / "script.py")
            f3 = ensure(top / "src" / "utils" / "script.py")
            ensure(top / "script.pyc")
            ls = self.run_list_command(top, "--include", "**/*.py")
            self.assertSetEqual(set(ls), set(str(x) for x in (f1, f2, f3)))
        # test_character_classes
        with tempfile.TemporaryDirectory() as tmp:
            top = Path(tmp)
            f1 = ensure(top / "file1.txt")
            f2 = ensure(top / "file5.txt")
            f3 = ensure(top / "fileA.txt")
            f4 = ensure(top / "file10.txt")
            f5 = ensure(top / "file9.txt")
            ls = self.run_list_command(top, "--include", "file[0-8].txt")
            self.assertSetEqual(set(ls), set(str(x) for x in (f1, f2)))
            ls = self.run_list_command(top, "--include", "file[!0-8].txt")
            self.assertSetEqual(set(ls), set(str(x) for x in (f5, f3)))
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
            Windows or ensure(top / "file.(txt|csv)")
            ensure(top / "file.txt")
            ensure(top / "file^.md")
            ensure(top / "file6.md")
            ensure(top / "file9.md")
            ensure(top / "file{7,9}.md")
            ensure(top / "file[.md")
            ensure(top / "file].md")
            if not Windows:
                ls1 = self.run_list_command(top, "--include", "file.(txt|csv)")
                ls2 = [*map(str, [top / "file.(txt|csv)"])]
                self.assertEqual(set(ls1), set(ls2))
            #
            ls1 = self.run_list_command(top, "--include", "file{7,9}.md")
            ls2 = [*map(str, [top / "file{7,9}.md"])]
            self.assertEqual(set(ls1), set(ls2))
            #
            ls1 = self.run_list_command(top, "--include", "file[^79].md")
            ls2 = [*map(str, [top / "file^.md", top / "file9.md"])]
            self.assertEqual(set(ls1), set(ls2))
            #
            ls1 = self.run_list_command(top, "--include", r"file[]^].md")
            ls2 = [*map(str, [top / "file^.md", top / "file].md"])]
            self.assertEqual(set(ls1), set(ls2))
            #
            ls1 = self.run_list_command(top, "--include", r"file[[9].md")
            ls2 = [*map(str, [top / "file9.md", top / "file[.md"])]
            self.assertEqual(set(ls1), set(ls2))
            # Pattern with backslashes (Windows paths)
            if Windows:
                pass
            else:
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
