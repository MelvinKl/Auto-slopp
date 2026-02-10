#!/usr/bin/env python3
"""Tests for file operations functions related to task processing."""

import tempfile
from pathlib import Path

import pytest

from auto_slopp.utils.file_operations import (
    create_file_counter_name,
    get_next_counter,
    rename_processed_file,
)


class TestFileOperations:
    """Test file operations for task processing."""

    def test_rename_processed_file(self):
        """Test file renaming with .used suffix."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_path = Path(temp_dir)
            original_file = test_path / "original.txt"
            original_file.write_text("Content")

            renamed_file = rename_processed_file(original_file)

            assert renamed_file is not None
            assert renamed_file.name.startswith("0001_")
            assert renamed_file.name.endswith(".used")
            assert "original" in renamed_file.name
            assert not original_file.exists()
            assert renamed_file.exists()

    def test_get_next_counter_no_existing_files(self):
        """Test counter generation when no existing files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_path = Path(temp_dir)
            counter = get_next_counter(test_path)
            assert counter == 1

    def test_get_next_counter_with_existing_files(self):
        """Test counter generation with existing .used files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_path = Path(temp_dir)

            # Create existing used files
            (test_path / "0001_file1.used").write_text("Content 1")
            (test_path / "0003_file2.used").write_text("Content 2")

            counter = get_next_counter(test_path)
            assert counter == 4  # Should be max existing + 1

    def test_create_file_counter_name(self):
        """Test file counter name generation."""
        test_cases = [
            (Path("test.txt"), 1, "0001_test.used"),
            (Path("README.md"), 2, "0002_README.used"),
            (Path("script.py"), 3, "0003_script.used"),
        ]

        for file_path, counter, expected in test_cases:
            result = create_file_counter_name(file_path, counter)
            assert result == expected
            assert result.endswith(".used")

    def test_get_next_counter_ignores_non_used_files(self):
        """Test that counter generation ignores non-.used files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_path = Path(temp_dir)

            # Create various files that should be ignored
            (test_path / "0001_file1.txt").write_text("Content 1")
            (test_path / "0003_file2.md").write_text("Content 2")
            (test_path / "other_file.used").write_text("Content 3")  # No counter

            counter = get_next_counter(test_path)
            assert counter == 1  # Should ignore non-pattern files

    def test_rename_processed_file_sequence(self):
        """Test sequential file renaming with correct counters."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_path = Path(temp_dir)

            # Create and rename first file
            file1 = test_path / "first.txt"
            file1.write_text("Content 1")
            renamed1 = rename_processed_file(file1)

            # Create and rename second file
            file2 = test_path / "second.txt"
            file2.write_text("Content 2")
            renamed2 = rename_processed_file(file2)

            assert renamed1.name == "0001_first.used"
            assert renamed2.name == "0002_second.used"
