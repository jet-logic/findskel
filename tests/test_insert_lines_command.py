#!/bin/env python3
import subprocess
import tempfile
import unittest
from pathlib import Path


class TestInsertLinesCommand(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory
        self.test_dir = Path(tempfile.mkdtemp())

        # Create test files
        self.source_file = self.test_dir / "test_file.txt"
        self.inlcude_file = self.test_dir / "header"

        # Source file with insertion markers
        self.source_file.write_text("First line\n" + "# <<< header\n" + "# >>>\n" + "Last line\n")
        print(self.source_file.read_text())

        # Template content to insert
        self.inlcude_file.write_text("INSERTED CONTENT\n")

    def tearDown(self):
        # Clean up the temporary directory
        for f in self.test_dir.glob("*"):
            f.unlink()
        self.test_dir.rmdir()

    def run_insert_lines(self, *args, capture_output=False):
        """Helper to run the insert_lines command"""
        cmd = ["python", "-m", "findskel.insert_lines", *args]
        print("RUN:", cmd)
        result = subprocess.run(cmd, cwd=self.test_dir, capture_output=capture_output, text=capture_output)
        return result

    # @unittest.skip
    def test_basic_insertion(self):
        """Test basic content insertion"""
        # Run the command
        result = self.run_insert_lines(str(self.source_file), "--search", str(self.test_dir), "--act")

        # Verify command succeeded
        self.assertEqual(result.returncode, 0, f"Command failed: {result.stderr}")

        # Verify file was modified correctly
        content = self.source_file.read_text()
        self.assertEqual(
            "First line\n" + "# <<< header\n" + "INSERTED CONTENT\n" + "# >>>\n" + "Last line\n",
            content,
        )
        # self.assertNotIn("<<< header", content)
        # self.assertEqual(
        #     content.splitlines(), ["First line", "INSERTED CONTENT", "Last line"]
        # )

    # @unittest.skip
    def test_dry_run(self):
        """Test dry run doesn't modify files"""
        original_content = self.source_file.read_text()

        # Run with dry-run
        result = self.run_insert_lines(str(self.source_file), "--search", str(self.test_dir), capture_output=True)

        # Verify file wasn't changed
        self.assertEqual(self.source_file.read_text(), original_content)

        # Verify output shows what would happen
        self.assertIn("INSERTED CONTENT", result.stdout)

    # @unittest.skip
    def test_missing_template(self):
        """Test behavior when template is missing"""
        self.inlcude_file.unlink()

        result = self.run_insert_lines(str(self.source_file), "--search", str(self.test_dir), capture_output=True)

        # Should succeed but not modify file
        self.assertEqual(result.returncode, 0)
        self.assertIn("<<< header", self.source_file.read_text())
        self.assertIn("Error", result.stderr)

    # @unittest.skip
    def test_multiple_files(self):
        """Test processing multiple files"""
        # Create second test file
        source2 = self.test_dir / "test2.txt"
        source2.write_text("# <<< header\n# >>>\n")

        result = self.run_insert_lines(str(self.source_file), str(source2), "--search", str(self.test_dir), "--act")

        # Both files should be processed
        self.assertIn("INSERTED CONTENT", self.source_file.read_text())
        self.assertIn("INSERTED CONTENT", source2.read_text())


if __name__ == "__main__":
    unittest.main()
