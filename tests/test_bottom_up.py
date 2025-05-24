#!/bin/env python3
import unittest
import os
import tempfile
import shutil
from subprocess import run, PIPE


class TestListBottomUp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Create a temporary directory structure for testing."""
        cls.test_dir = tempfile.mkdtemp()

        # Create directory structure
        cls.root_file = os.path.join(cls.test_dir, "root_file.txt")
        with open(cls.root_file, "w") as f:
            f.write("root level file")

        cls.subdir = os.path.join(cls.test_dir, "subdir")
        os.mkdir(cls.subdir)
        cls.subdir_file = os.path.join(cls.subdir, "subdir_file.txt")
        with open(cls.subdir_file, "w") as f:
            f.write("subdirectory file")

        cls.subsubdir = os.path.join(cls.subdir, "subsubdir")
        os.mkdir(cls.subsubdir)
        cls.subsubdir_file = os.path.join(cls.subsubdir, "deep_file.txt")
        with open(cls.subsubdir_file, "w") as f:
            f.write("deeply nested file")

    @classmethod
    def tearDownClass(cls):
        """Clean up the temporary directory."""
        shutil.rmtree(cls.test_dir)

    def run_list_command(self, *args):
        """Helper to run the list command and return output."""
        cmd = ["python", "-m", "scan_dir_skel.list", *args, self.test_dir]
        print("RUN", cmd)
        result = run(cmd, stdout=PIPE, stderr=PIPE, text=True)
        a = [line for line in result.stdout.splitlines()]
        for x in a:
            print(x)
        return a

    @unittest.skip("Enable to test default top-down behavior")
    def test_default_top_down(self):
        """Test that default behavior is top-down traversal."""
        output = self.run_list_command()

        # Find positions of files in output
        root_pos = output.index(self.root_file) if self.root_file in output else -1
        subdir_pos = output.index(self.subdir_file) if self.subdir_file in output else -1
        subsubdir_pos = output.index(self.subsubdir_file) if self.subsubdir_file in output else -1

        # In top-down, parent directories appear before their contents
        self.assertLess(root_pos, subdir_pos)
        self.assertLess(subdir_pos, subsubdir_pos)

    @unittest.skip("Enable to test bottom-up behavior")
    def test_bottom_up(self):
        """Test that --bottom-up lists contents before parents."""
        output = self.run_list_command("--bottom-up")

        # Find positions of files in output
        root_pos = output.index(self.root_file) if self.root_file in output else -1
        subdir_pos = output.index(self.subdir_file) if self.subdir_file in output else -1
        subsubdir_pos = output.index(self.subsubdir_file) if self.subsubdir_file in output else -1

        # In bottom-up, children appear before parents
        self.assertGreater(root_pos, subdir_pos)
        self.assertGreater(subdir_pos, subsubdir_pos)

    @unittest.skip("Enable to test combined with other options")
    def test_bottom_up_with_other_options(self):
        """Test that --bottom-up works with other options like --depth."""
        output = self.run_list_command("--bottom-up", "--depth", "..2")

        # Should only show files up to depth 1 (subdir level)
        self.assertIn(self.root_file, output)
        self.assertIn(self.subdir_file, output)
        self.assertNotIn(self.subsubdir_file, output)

        # Verify bottom-up order is maintained
        root_pos = output.index(self.root_file) if self.root_file in output else -1
        subdir_pos = output.index(self.subdir_file) if self.subdir_file in output else -1
        print([self.root_file, self.subdir_file])
        self.assertGreater(root_pos, subdir_pos, output)


if __name__ == "__main__":
    unittest.main()
