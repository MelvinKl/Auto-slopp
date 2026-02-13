"""Tests for processor module."""

from pathlib import Path

import pytest

from auto_slopp.processor import Processor


class TestProcessor:
    """Test cases for Processor class."""

    def test_get_pending_tasks_empty_directory(self, tmp_path):
        """Test that empty directory returns no pending tasks."""
        processor = Processor(tmp_path)
        assert processor.get_pending_tasks() == []

    def test_get_pending_tasks_with_files(self, tmp_path):
        """Test that pending tasks are found."""
        (tmp_path / "task1.txt").write_text("task 1")
        (tmp_path / "task2.txt").write_text("task 2")

        processor = Processor(tmp_path)
        result = processor.get_pending_tasks()

        assert len(result) == 2

    def test_get_completed_tasks(self, tmp_path):
        """Test that completed tasks are found."""
        (tmp_path / "task1.txt.used").write_text("task 1")

        processor = Processor(tmp_path)
        result = processor.get_completed_tasks()

        assert len(result) == 1

    def test_process_returns_count(self, tmp_path):
        """Test that process returns count of processed tasks."""
        (tmp_path / "task1.txt").write_text("task 1")
        (tmp_path / "task2.txt").write_text("task 2")

        processor = Processor(tmp_path)
        count = processor.process()

        assert count == 2

    def test_count_pending(self, tmp_path):
        """Test count_pending returns correct count."""
        (tmp_path / "task1.txt").write_text("task 1")
        (tmp_path / "task2.txt").write_text("task 2")

        processor = Processor(tmp_path)
        assert processor.count_pending() == 2

    def test_count_completed(self, tmp_path):
        """Test count_completed returns correct count."""
        (tmp_path / "task1.txt.used").write_text("task 1")

        processor = Processor(tmp_path)
        assert processor.count_completed() == 1
