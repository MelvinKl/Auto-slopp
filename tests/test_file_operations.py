"""Tests for file_operations module."""

from pathlib import Path
from unittest.mock import patch

import pytest

from auto_slopp.utils.file_operations import (
    copy_file,
    delete_file,
    ensure_directory,
    move_file,
)


class TestCopyFile:
    """Test cases for copy_file function."""

    def test_copies_file(self, tmp_path):
        """Test that file is copied."""
        src = tmp_path / "source.txt"
        src.write_text("content")
        dst = tmp_path / "dest.txt"

        result = copy_file(src, dst)

        assert result is True
        assert dst.exists()
        assert dst.read_text() == "content"

    def test_returns_false_on_error(self, tmp_path):
        """Test that error returns False."""
        src = tmp_path / "nonexistent.txt"
        dst = tmp_path / "dest.txt"

        result = copy_file(src, dst)

        assert result is False


class TestMoveFile:
    """Test cases for move_file function."""

    def test_moves_file(self, tmp_path):
        """Test that file is moved."""
        src = tmp_path / "source.txt"
        src.write_text("content")
        dst = tmp_path / "dest.txt"

        result = move_file(src, dst)

        assert result is True
        assert not src.exists()
        assert dst.exists()

    def test_returns_false_on_error(self, tmp_path):
        """Test that error returns False."""
        src = tmp_path / "nonexistent.txt"
        dst = tmp_path / "dest.txt"

        result = move_file(src, dst)

        assert result is False


class TestDeleteFile:
    """Test cases for delete_file function."""

    def test_deletes_file(self, tmp_path):
        """Test that file is deleted."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("content")

        result = delete_file(file_path)

        assert result is True
        assert not file_path.exists()

    def test_returns_false_on_error(self, tmp_path):
        """Test that error returns False."""
        file_path = tmp_path / "nonexistent.txt"

        result = delete_file(file_path)

        assert result is False


class TestEnsureDirectory:
    """Test cases for ensure_directory function."""

    def test_creates_directory(self, tmp_path):
        """Test that directory is created."""
        dir_path = tmp_path / "new" / "dir"

        result = ensure_directory(dir_path)

        assert result is True
        assert dir_path.exists()

    def test_returns_true_for_existing_directory(self, tmp_path):
        """Test that existing directory returns True."""
        result = ensure_directory(tmp_path)

        assert result is True
