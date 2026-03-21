#!/usr/bin/env python3
"""Tests for file operations functions related to task processing."""

import tempfile
from pathlib import Path

import pytest

from auto_slopp.utils.file_operations import get_next_counter


class TestFileOperations:
    """Test file operations for task processing."""

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
