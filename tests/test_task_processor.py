"""Tests for the task_processor module."""

import tempfile
from pathlib import Path

from auto_slopp.task_processor import TaskProcessor


def test_find_task_files_empty_dir():
    """Test that empty directory returns no files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        processor = TaskProcessor(tmpdir)
        assert processor.find_task_files() == []


def test_find_task_files_with_files():
    """Test finding task files in a directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(tmpdir, "001-task.txt").touch()
        Path(tmpdir, "002-task.txt").touch()
        Path(tmpdir, "003-task.used").touch()
        processor = TaskProcessor(tmpdir)
        files = processor.find_task_files()
        assert len(files) == 2


def test_process_file():
    """Test processing a single task file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        task_file = Path(tmpdir, "001-test.txt")
        task_file.write_text("Test content")
        processor = TaskProcessor(tmpdir)
        result = processor.process_file(task_file)
        assert result is True
        assert not task_file.exists()
        assert Path(tmpdir, "001-test.txt.used").exists()


def test_process_file_already_processed():
    """Test that already processed files are skipped."""
    with tempfile.TemporaryDirectory() as tmpdir:
        task_file = Path(tmpdir, "001-test.txt.used")
        task_file.write_text("Already processed")
        processor = TaskProcessor(tmpdir)
        result = processor.process_file(task_file)
        assert result is False


def test_process_all():
    """Test processing all task files in a directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(tmpdir, "001-task.txt").touch()
        Path(tmpdir, "002-task.txt").touch()
        processor = TaskProcessor(tmpdir)
        count = processor.process_all()
        assert count == 2
        assert len(list(Path(tmpdir).glob("*.txt"))) == 0
        assert len(list(Path(tmpdir).glob("*.txt.used"))) == 2


def test_process_all_empty_dir():
    """Test processing an empty directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        processor = TaskProcessor(tmpdir)
        count = processor.process_all()
        assert count == 0
