#!/bin/env python3
import unittest
import os
import tempfile
import subprocess
from pathlib import Path


class TestListCommand(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a temporary directory structure for testing
        cls.test_dir = tempfile.mkdtemp()
        cls.file1 = Path(cls.test_dir) / "included_file.txt"
        cls.file2 = Path(cls.test_dir) / "excluded_file.log"
        cls.subdir = Path(cls.test_dir) / "included_dir"
        cls.subdir_file = cls.subdir / "nested_file.txt"

        # Create files and directories
        cls.file1.touch()
        cls.file2.touch()
        cls.subdir.mkdir()
        cls.subdir_file.touch()
        subprocess.run(["find", cls.test_dir])

    @classmethod
    def tearDownClass(cls):
        # Clean up the temporary directory
        import shutil

        shutil.rmtree(cls.test_dir)

    def run_list_command(self, *args):
        """Helper method to run the list command, print command and output"""
        cmd = ["python", "-m", "scan_dir_skel.list", *args, self.test_dir]

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
        """Test listing all files without filters"""
        output = self.run_list_command()
        expected_paths = {str(self.file1), str(self.file2), str(self.subdir), str(self.subdir_file)}
        self.assertEqual(len(output), len(expected_paths))
        for path in output:
            self.assertIn(path, expected_paths)

    # @unittest.skip("Enable to test include filter")
    def test_include_filter(self):
        """Test listing only files matching include pattern"""
        output = self.run_list_command("--include", "*.txt")
        expected_paths = {str(self.file1), str(self.subdir_file)}
        self.assertEqual(len(output), len(expected_paths))
        for path in output:
            self.assertIn(path, expected_paths)

    # @unittest.skip("Enable to test exclude filter")
    def test_exclude_filter(self):
        """Test listing files not matching exclude pattern"""
        output = self.run_list_command("--exclude", "*.log")
        expected_paths = {str(self.file1), str(self.subdir), str(self.subdir_file)}
        self.assertEqual(len(output), len(expected_paths))
        for path in output:
            self.assertIn(path, expected_paths)

    # @unittest.skip("Enable to test combined include/exclude")
    def test_combined_filters(self):
        """Test listing with both include and exclude filters"""
        output = self.run_list_command("--include", "*file*", "--exclude", "*.log")
        expected_paths = {str(self.file1), str(self.subdir_file)}
        self.assertEqual(len(output), len(expected_paths))
        for path in output:
            self.assertIn(path, expected_paths)

    # @unittest.skip("Enable to test directory inclusion")
    def test_directory_inclusion(self):
        """Test that directories are included when they match patterns"""
        output = self.run_list_command("--include", "*dir**")
        expected_paths = {str(self.subdir), str(self.subdir_file)}
        # self.assertEqual(len(output), 1)
        # self.assertEqual(output[0], str(self.subdir))
        for path in output:
            self.assertIn(path, expected_paths)
        self.assertEqual(len(output), len(expected_paths))


if __name__ == "__main__":
    unittest.main()
