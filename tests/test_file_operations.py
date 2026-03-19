#!/usr/bin/env python3
"""Tests for file operations functions related to task processing."""

import tempfile
from pathlib import Path
from unittest.mock import patch

from auto_slopp.utils.file_operations import (
    cleanup_temp_file,
    create_file_counter_name,
    ensure_directory_exists,
    find_text_files,
    get_next_counter,
    read_file_content,
    rename_processed_file,
    write_temp_instruction_file,
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

    def test_find_text_files(self):
        """Test finding .txt files in directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_path = Path(temp_dir)

            # Create test files
            (test_path / "file1.txt").write_text("Content 1")
            (test_path / "file2.txt").write_text("Content 2")
            (test_path / "readme.md").write_text("README")

            # Create subdirectory with txt file
            subdir = test_path / "subdir"
            subdir.mkdir()
            (subdir / "nested.txt").write_text("Nested content")

            result = find_text_files(test_path)

            assert len(result) == 3
            assert all(f.suffix == ".txt" for f in result)

    def test_find_text_files_empty_directory(self):
        """Test finding .txt files in empty directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_path = Path(temp_dir)

            result = find_text_files(test_path)

            assert result == []

    def test_find_text_files_exception(self):
        """Test find_text_files handles exceptions."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_path = Path(temp_dir)

            with patch.object(Path, "rglob", side_effect=PermissionError("Access denied")):
                result = find_text_files(test_path)

                assert result == []

    def test_read_file_content(self):
        """Test reading file content."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Test content")
            temp_path = Path(f.name)

        try:
            result = read_file_content(temp_path)
            assert result == "Test content"
        finally:
            temp_path.unlink()

    def test_read_file_content_empty(self):
        """Test reading empty file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("")
            temp_path = Path(f.name)

        try:
            result = read_file_content(temp_path)
            assert result is None
        finally:
            temp_path.unlink()

    def test_read_file_content_nonexistent(self):
        """Test reading nonexistent file."""
        result = read_file_content(Path("/nonexistent/file.txt"))
        assert result is None

    def test_read_file_content_exception(self):
        """Test read_file_content handles exceptions."""
        with patch.object(Path, "read_text", side_effect=IOError("Read error")):
            result = read_file_content(Path("/some/file.txt"))
            assert result is None

    def test_ensure_directory_exists(self):
        """Test ensuring directory exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            new_dir = Path(temp_dir) / "new" / "nested" / "dir"

            result = ensure_directory_exists(new_dir)

            assert result is True
            assert new_dir.exists()
            assert new_dir.is_dir()

    def test_ensure_directory_exists_already_exists(self):
        """Test ensuring existing directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = ensure_directory_exists(Path(temp_dir))
            assert result is True

    def test_ensure_directory_exists_exception(self):
        """Test ensure_directory_exists handles exceptions."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(Path, "mkdir", side_effect=OSError("Cannot create")):
                result = ensure_directory_exists(Path(temp_dir) / "invalid")
                assert result is False

    def test_write_temp_instruction_file(self):
        """Test writing instruction file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_dir = Path(temp_dir)
            instructions = "Test instructions"

            result = write_temp_instruction_file(test_dir, instructions)

            assert result.exists()
            assert result.name == ".agent_instructions.txt"
            assert result.read_text() == instructions

    def test_write_temp_instruction_file_exception(self):
        """Test write_temp_instruction_file handles exceptions."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_dir = Path(temp_dir)

            with patch.object(Path, "write_text", side_effect=IOError("Write error")):
                with patch("auto_slopp.utils.file_operations.logger"):
                    try:
                        write_temp_instruction_file(test_dir, "instructions")
                    except IOError:
                        pass

    def test_cleanup_temp_file(self):
        """Test cleanup of temporary file."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = Path(f.name)

        cleanup_temp_file(temp_path)
        assert not temp_path.exists()

    def test_cleanup_temp_file_missing(self):
        """Test cleanup of missing file."""
        cleanup_temp_file(Path("/nonexistent/file.txt"))  # Should not raise

    def test_cleanup_temp_file_exception(self):
        """Test cleanup handles exceptions."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = Path(temp_dir) / "test.txt"
            temp_file.write_text("content")

            with patch.object(Path, "unlink", side_effect=OSError("Cannot delete")):
                cleanup_temp_file(temp_file)

    def test_get_next_counter_custom_start(self):
        """Test counter generation with custom start."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_path = Path(temp_dir)
            (test_path / "0010_file.used").write_text("Content")

            counter = get_next_counter(test_path, counter_start=5)
            assert counter == 11

    def test_rename_processed_file_with_custom_counter(self):
        """Test file renaming with custom counter."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_path = Path(temp_dir)
            original_file = test_path / "test.txt"
            original_file.write_text("Content")

            renamed_file = rename_processed_file(original_file, counter_start=100)

            assert renamed_file is not None
            assert renamed_file.name.startswith("0100_")
