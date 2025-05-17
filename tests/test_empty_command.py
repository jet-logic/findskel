#!/bin/env python3
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


class TestEmptyCommand(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory structure
        self.test_dir = Path(tempfile.mkdtemp())

        # Create test files and directories
        self.empty_file = self.test_dir / "empty_file.txt"
        self.empty_file.touch()

        self.non_empty_file = self.test_dir / "non_empty.txt"
        self.non_empty_file.write_text("content")

        self.empty_dir = self.test_dir / "empty_dir"
        self.empty_dir.mkdir()

        self.non_empty_dir = self.test_dir / "non_empty_dir"
        self.non_empty_dir.mkdir()
        (self.non_empty_dir / "file.txt").write_text("not empty")
        self.empty_file_2 = self.test_dir / "empty_file_2.txt"
        self.empty_file_2.touch()

    def tearDown(self):
        # Clean up the temporary directory
        for root, dirs, files in os.walk(self.test_dir, topdown=False):
            for name in files:
                os.unlink(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.test_dir)

    def run_empty_command(self, *args, **kwargs):
        """Helper to run the empty command"""
        cmd = ["python", "-m", "scan_dir_skel.empty", *args]
        print("RUN", cmd)
        result = subprocess.run(cmd, cwd=self.test_dir, **kwargs)
        return result

    # @unittest.skip
    def test_list_empty_files(self):
        """Test listing empty files"""
        result = self.run_empty_command("--files", ".", capture_output=True, text=True)

        # Verify command succeeded
        self.assertEqual(result.returncode, 0, f"Command failed: {result.stderr}")

        # Verify output contains empty file but not non-empty file
        self.assertIn(str(self.empty_file.name), result.stdout)
        self.assertNotIn(str(self.non_empty_file.name), result.stdout)

    # @unittest.skip
    def test_list_empty_dirs(self):
        """Test listing empty directories"""
        result = self.run_empty_command(
            "--dirs", self.test_dir, capture_output=True, text=True
        )
        # print(result.stdout)
        self.assertEqual(result.returncode, 0)
        self.assertIn(str(self.empty_dir.name), result.stdout)
        self.assertNotIn(str(self.non_empty_dir.name), result.stdout)

    # @unittest.skip
    def test_remove_empty_files(self):
        """Test removing empty files"""
        result = self.run_empty_command("--files", "--remove", ".")

        self.assertEqual(result.returncode, 0)
        self.assertFalse(self.empty_file.exists(), "Empty file was not removed")
        self.assertTrue(
            self.non_empty_file.exists(), "Non-empty file was incorrectly removed"
        )

    # @unittest.skip
    def test_remove_empty_dirs(self):
        """Test removing empty directories"""
        result = self.run_empty_command("--dirs", "--remove", ".")

        self.assertEqual(result.returncode, 0)
        self.assertFalse(self.empty_dir.exists(), "Empty directory was not removed")
        self.assertTrue(
            self.non_empty_dir.exists(), "Non-empty directory was incorrectly removed"
        )

    # @unittest.skip
    def test_files_dirs(self):
        """Test files dirs"""
        result = self.run_empty_command("--files", "--dirs")

        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(self.empty_file.exists())
        self.assertTrue(self.empty_dir.exists())

    # @unittest.skip
    def test_combined_operations(self):
        """Test combined file and directory operations"""
        result = self.run_empty_command("--remove", ".")

        self.assertEqual(result.returncode, 0)
        self.assertFalse(self.empty_file.exists())
        self.assertFalse(self.empty_dir.exists())
        self.assertTrue(self.non_empty_file.exists())
        self.assertTrue(self.non_empty_dir.exists())
        self.assertFalse(self.empty_file_2.exists())


if __name__ == "__main__":
    unittest.main()
