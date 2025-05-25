#!/bin/env python3
import unittest
import os
import tempfile
import shutil
from subprocess import run, PIPE


class TestListCommandWithSymlinks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Create a temporary directory structure with directory symlinks for testing."""
        cls.test_dir = tempfile.mkdtemp()

        # Create regular directory structure
        cls.dir_a = os.path.join(cls.test_dir, "dir_a")
        os.mkdir(cls.dir_a)
        with open(os.path.join(cls.dir_a, "file_in_a.txt"), "w") as f:
            f.write("file in dir_a")

        cls.dir_b = os.path.join(cls.test_dir, "dir_b")
        os.mkdir(cls.dir_b)
        with open(os.path.join(cls.dir_b, "file_in_b.txt"), "w") as f:
            f.write("file in dir_b")

        # Create symlink to directory
        cls.symlink_to_dir = os.path.join(cls.test_dir, "symlink_to_dir")
        os.symlink(cls.dir_b, cls.symlink_to_dir)

        # Create a broken symlink to test robustness
        cls.broken_symlink = os.path.join(cls.test_dir, "broken_symlink")
        os.symlink(os.path.join(cls.test_dir, "non_existent_dir"), cls.broken_symlink)

    @classmethod
    def tearDownClass(cls):
        """Clean up the temporary directory."""
        shutil.rmtree(cls.test_dir)

    def run_list_command(self, *args, path=None):
        """Helper to run the list command and return output."""
        cmd = ["python", "-m", "scan_dir_skel.list", *args, path or self.test_dir]
        print("RUN", cmd)
        result = run(cmd, stdout=PIPE, stderr=PIPE, text=True)
        a = [line.strip() for line in result.stdout.splitlines()]
        for x in a:
            print(x)
        return a

    # @unittest.skip("Enable to test default behavior (no symlink following)")
    def test_default_behavior(self):
        """Test that directory symlinks are not followed by default."""
        output = self.run_list_command()

        # The symlink itself should appear
        self.assertIn(os.path.join(self.test_dir, "symlink_to_dir"), output)

        # The contents of the symlinked directory should NOT appear
        self.assertNotIn(os.path.join(self.test_dir, "symlink_to_dir", "file_in_b.txt"), output)

        # Regular directory contents should appear
        self.assertIn(os.path.join(self.test_dir, "dir_a", "file_in_a.txt"), output)

    # @unittest.skip("Enable to test follow symlinks behavior")
    def test_follow_symlinks(self):
        """Test that directory symlinks are followed when --follow-symlinks is used."""
        output = self.run_list_command("--follow-symlinks")

        # The symlink itself should appear
        self.assertIn(os.path.join(self.test_dir, "symlink_to_dir"), output)

        # The contents of the symlinked directory SHOULD appear
        self.assertIn(os.path.join(self.test_dir, "symlink_to_dir", "file_in_b.txt"), output)

        # Regular directory contents should still appear
        self.assertIn(os.path.join(self.test_dir, "dir_a", "file_in_a.txt"), output)

    # @unittest.skip("Enable to test broken symlink handling")
    def test_broken_symlink(self):
        """Test behavior with broken symlinks."""
        output = self.run_list_command("--follow-symlinks")

        # The broken symlink should still appear in the listing
        self.assertIn(os.path.join(self.test_dir, "broken_symlink"), output)

    def test_symlink_arg_1(self):
        path = os.path.join(self.test_dir, "symlink_to_dir")
        ls = self.run_list_command(path=path)
        self.assertListEqual(ls, [os.path.join(self.test_dir, "symlink_to_dir", "file_in_b.txt")])

    def test_symlink_arg_2(self):
        path = os.path.join(self.test_dir, "symlink_to_dir", "file_in_b.txt")
        ls = self.run_list_command(path=path)
        self.assertListEqual(ls, [path])


if __name__ == "__main__":
    unittest.main()

# /tempdir
#   /dir_a
#     file_in_a.txt
#   /dir_b
#     file_in_b.txt
#   symlink_to_dir -> dir_b
#   broken_symlink -> non_existent_dir
