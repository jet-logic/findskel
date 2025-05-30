#!/bin/env python3
import unittest
import os
import tempfile
import subprocess
import sys
from pathlib import Path


class TestListCommandWithDepth(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory with nested structure
        self.temp_dir = tempfile.mkdtemp()
        self.dir = Path(self.temp_dir)

        # Create directory structure:
        # temp_dir/
        # ├── file1.txt
        # ├── dir1/
        # │   ├── file2.txt
        # │   └── dir2/
        # │       ├── file3.txt
        # │       └── dir3/
        # │           └── file4.txt
        # └── dir4/
        #     └── file5.txt

        self.files = {
            "file1.txt": 0,
            "dir1/file2.txt": 0,
            "dir1/dir2/file3.txt": 0,
            "dir1/dir2/dir3/file4.txt": 0,
            "dir4/file5.txt": 0,
        }

        for rel_path, size in self.files.items():
            path = os.path.join(self.temp_dir, rel_path)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "wb") as f:
                if size > 0:
                    f.seek(size - 1)
                    f.write(b"\0")
        # self.dir.walk

    def tearDown(self):
        # Clean up the temporary directory
        for root, dirs, files in os.walk(self.temp_dir, topdown=False):
            for name in files:
                os.unlink(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.temp_dir)

    def exec(self, args):
        print("RUN", args)
        return subprocess.run(args)

    def run_list_command(self, *args):
        """Run the list command and return output as list of paths"""
        cmd = [sys.executable, "-m", "findskel.list", *args, self.temp_dir]
        print("RUN", cmd)
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )
        if result.returncode != 0:
            print(f"Command failed with stderr: {result.stderr}")
        self.assertEqual(result.returncode, 0)
        a = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        for x in a:
            print(x)
        for x in result.stderr.splitlines():
            print(x.rstrip())
        return a

    # @unittest.skip
    def test_no_depth_limit(self):
        # Should return all files
        ls = self.run_list_command()
        paths = []
        for root, dirs, files in os.walk(self.dir, topdown=False):
            for name in files:
                paths.append(str(self.dir / root / name))
            for name in dirs:
                paths.append(str(self.dir / root / name))
        self.assertSetEqual(set(ls), set(paths))
        ls = self.run_list_command("--depth", "")
        paths = []
        for root, dirs, files in os.walk(self.dir, topdown=False):
            for name in files:
                paths.append(str(self.dir / root / name))
            for name in dirs:
                paths.append(str(self.dir / root / name))
        self.assertSetEqual(set(ls), set(paths))

    # @unittest.skip
    def test_depth_zero(self):
        # Only root level files
        ls = self.run_list_command("--depth", "1")
        top = self.dir
        self.assertSetEqual(set(ls), set(str(x) for x in (top / "file1.txt", top / "dir1", top / "dir4")))

    # @unittest.skip
    def test_depth_one(self):
        # Root level and one level deep
        ls = self.run_list_command("--depth", "1..2")
        top = self.dir
        expected = {
            top / "file1.txt",
            top / "dir1",
            top / "dir4",
            top / "dir1" / "dir2",
            top / "dir1" / "file2.txt",
            top / "dir4" / "file5.txt",
        }
        self.assertSetEqual(set(ls), set(str(x) for x in expected))

    # @unittest.skip
    def test_depth_two(self):
        ls = self.run_list_command("--depth", "2")
        expected = {
            os.path.join(self.temp_dir, "dir1", "file2.txt"),
            os.path.join(self.temp_dir, "dir1", "dir2"),
            os.path.join(self.temp_dir, "dir4", "file5.txt"),
        }
        self.assertSetEqual(set(ls), expected)

    # @unittest.skip
    def test_depth_range(self):
        # Between depth 1 and 2
        ls = self.run_list_command("--depth", "2..3")
        expected = {
            os.path.join(self.temp_dir, "dir1", "file2.txt"),
            os.path.join(self.temp_dir, "dir1", "dir2"),
            os.path.join(self.temp_dir, "dir1", "dir2", "file3.txt"),
            os.path.join(self.temp_dir, "dir1", "dir2", "dir3"),
            os.path.join(self.temp_dir, "dir4", "file5.txt"),
        }
        self.assertEqual(set(ls), expected)

    # @unittest.skip
    def test_min_depth(self):
        # At least depth 1 (exclude root level)
        ls = self.run_list_command("--depth", "2..")
        expected = {
            os.path.join(self.temp_dir, "dir1", "file2.txt"),
            os.path.join(self.temp_dir, "dir1", "dir2", "file3.txt"),
            os.path.join(self.temp_dir, "dir1", "dir2"),
            os.path.join(self.temp_dir, "dir1", "dir2", "dir3"),
            os.path.join(self.temp_dir, "dir1", "dir2", "dir3", "file4.txt"),
            os.path.join(self.temp_dir, "dir4", "file5.txt"),
        }
        self.assertEqual(set(ls), expected)

    # @unittest.skip
    def test_max_depth(self):
        # At most depth 2
        ls = self.run_list_command("--depth", "..2")
        expected = {
            os.path.join(self.temp_dir, "file1.txt"),
            os.path.join(self.temp_dir, "dir1"),
            os.path.join(self.temp_dir, "dir1", "file2.txt"),
            os.path.join(self.temp_dir, "dir1", "dir2"),
            os.path.join(self.temp_dir, "dir4"),
            os.path.join(self.temp_dir, "dir4", "file5.txt"),
        }
        self.assertEqual(set(ls), expected)

    # @unittest.skip
    def test_combined_with_sizes(self):
        # Combine depth with size filtering
        # Make one file non-empty
        with open(os.path.join(self.temp_dir, "dir1", "file2.txt"), "wb") as f:
            f.write(b"content")

        ls = self.run_list_command("--depth", "2", "--sizes", "0")
        expected = {
            os.path.join(self.temp_dir, "dir4", "file5.txt"),
        }
        self.assertEqual(set(ls), expected)


if __name__ == "__main__":
    unittest.main()
