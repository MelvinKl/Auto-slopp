"""Tests for main application functionality."""

from pathlib import Path

import pytest

from auto_slopp.main import find_task_files, mark_task_used, process_task_file, run


class TestFindTaskFiles:
    """Tests for find_task_files function."""

    def test_returns_empty_list_for_nonexistent_directory(self, tmp_path):
        """Test that nonexistent directory returns empty list."""
        result = find_task_files(tmp_path / "nonexistent")
        assert result == []

    def test_finds_txt_files(self, tmp_path):
        """Test that .txt files are found."""
        (tmp_path / "task1.txt").write_text("task 1")
        (tmp_path / "task2.txt").write_text("task 2")
        (tmp_path / "readme.md").write_text("readme")

        result = find_task_files(tmp_path)

        assert len(result) == 2
        assert all(f.suffix == ".txt" for f in result)

    def test_returns_sorted_files(self, tmp_path):
        """Test that files are returned sorted."""
        (tmp_path / "z_task.txt").write_text("z")
        (tmp_path / "a_task.txt").write_text("a")

        result = find_task_files(tmp_path)

        assert result[0].name == "a_task.txt"
        assert result[1].name == "z_task.txt"


class TestProcessTaskFile:
    """Tests for process_task_file function."""

    def test_returns_true_for_valid_file(self, tmp_path):
        """Test that valid file returns True."""
        file_path = tmp_path / "task.txt"
        file_path.write_text("task content")

        result = process_task_file(file_path)

        assert result is True

    def test_returns_false_for_empty_file(self, tmp_path):
        """Test that empty file returns False."""
        file_path = tmp_path / "empty.txt"
        file_path.write_text("")

        result = process_task_file(file_path)

        assert result is False

    def test_returns_false_for_nonexistent_file(self, tmp_path):
        """Test that nonexistent file returns False."""
        result = process_task_file(tmp_path / "nonexistent.txt")
        assert result is False


class TestMarkTaskUsed:
    """Tests for mark_task_used function."""

    def test_renames_file_to_used(self, tmp_path):
        """Test that file is renamed to .txt.used."""
        file_path = tmp_path / "task.txt"
        file_path.write_text("content")

        mark_task_used(file_path)

        assert file_path.with_suffix(".txt.used").exists()
        assert not file_path.exists()


class TestRun:
    """Tests for run function."""

    def test_run_processes_task_files(self, tmp_path):
        """Test that run processes task files."""
        (tmp_path / "task1.txt").write_text("task 1")
        (tmp_path / "task2.txt").write_text("task 2")

        count = run(tmp_path)

        assert count == 2
