#!/bin/env python3
import unittest
import os
import tempfile
import subprocess
import sys


class TestListCommandWithSizes(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory with test files
        self.temp_dir = tempfile.mkdtemp()
        self.file_sizes = {
            "empty.txt": 0,
            "small.txt": 100,
            "medium.txt": 1024,  # 1KB
            "large.txt": 1048576,  # 1MB
        }

        for name, size in self.file_sizes.items():
            path = os.path.join(self.temp_dir, name)
            with open(path, "wb") as f:
                if size > 0:
                    f.seek(size - 1)
                    f.write(b"\0")

    def tearDown(self):
        # Clean up the temporary directory
        for name in self.file_sizes:
            path = os.path.join(self.temp_dir, name)
            if os.path.exists(path):
                os.unlink(path)
        os.rmdir(self.temp_dir)

    def run_list_command(self, *args):
        """Run the list command and return output as list of lines"""
        cmd = [sys.executable, "-m", "scan_dir_skel.list", *args, self.temp_dir]
        print("RUN", cmd)
        result = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        self.assertEqual(
            result.returncode, 0, f"Command failed with stderr: {result.stderr}"
        )
        a = [line.strip() for line in result.stdout.splitlines() if line.strip()]

        for x in a:
            print(x)
        return a

    def test_single_size_filter(self):
        # Test exact size match
        output = self.run_list_command("--sizes", "0")
        self.assertEqual(len(output), 1)
        self.assertIn("empty.txt", output[0])

        # Test size with unit
        output = self.run_list_command("--sizes", "1k")
        self.assertEqual(len(output), 1)
        self.assertIn("medium.txt", output[0])

    def test_size_range(self):
        # Test range (100B to 1KB)
        output = self.run_list_command("--sizes", "100..1k")
        self.assertEqual(len(output), 2)
        output_files = [os.path.basename(line) for line in output]
        self.assertIn("small.txt", output_files)
        self.assertIn("medium.txt", output_files)

    def test_open_ended_range(self):
        # Test minimum size
        output = self.run_list_command("--sizes", "1k..")
        self.assertEqual(len(output), 2)
        output_files = [os.path.basename(line) for line in output]
        self.assertIn("medium.txt", output_files)
        self.assertIn("large.txt", output_files)

        # Test maximum size
        output = self.run_list_command("--sizes", "..100")
        self.assertEqual(len(output), 2)
        output_files = [os.path.basename(line) for line in output]
        self.assertIn("empty.txt", output_files)
        self.assertIn("small.txt", output_files)

    def test_multiple_size_filters(self):
        # Test multiple --sizes arguments
        output = self.run_list_command("--sizes", "100", "--sizes", "1m")
        self.assertEqual(len(output), 2)
        output_files = [os.path.basename(line) for line in output]
        self.assertIn("small.txt", output_files)
        self.assertIn("large.txt", output_files)

    def test_size_with_units(self):
        # Test different unit specifications
        output = self.run_list_command("--sizes", "0.5k..1.5k")
        self.assertEqual(len(output), 1)
        self.assertIn("medium.txt", output[0])

        output = self.run_list_command("--sizes", "1M")
        self.assertEqual(len(output), 1)
        self.assertIn("large.txt", output[0])

    def test_no_matches(self):
        # Test case where no files match
        output = self.run_list_command("--sizes", "2m..")
        self.assertEqual(len(output), 0)


if __name__ == "__main__":
    unittest.main()
