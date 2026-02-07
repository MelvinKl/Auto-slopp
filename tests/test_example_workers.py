"""Tests for example Worker implementations."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from auto_slopp.example_workers import FileMonitor, HeartbeatWorker, SimpleLogger, TaskProcessor


class TestSimpleLogger:
    """Test cases for SimpleLogger worker."""

    def test_init_default(self):
        """Test initialization with default parameters."""
        worker = SimpleLogger()
        assert worker.name == "SimpleLogger"
        assert worker.logger is not None

    def test_init_custom_name(self):
        """Test initialization with custom name."""
        worker = SimpleLogger("CustomLogger")
        assert worker.name == "CustomLogger"

    def test_run_with_existing_paths(self, tmp_path):
        """Test running with existing repository and task paths."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        task_path = tmp_path / "task"
        task_path.mkdir()

        worker = SimpleLogger()
        result = worker.run(repo_path, task_path)

        assert result["worker_name"] == "SimpleLogger"
        assert result["repo_path"] == str(repo_path)
        assert result["task_path"] == str(task_path)
        assert result["repo_exists"] is True
        assert result["task_exists"] is True
        assert result["execution_time"] > 0
        assert "timestamp" in result

    def test_run_with_nonexistent_paths(self):
        """Test running with non-existent paths."""
        repo_path = Path("/nonexistent/repo")
        task_path = Path("/nonexistent/task")

        worker = SimpleLogger()
        result = worker.run(repo_path, task_path)

        assert result["repo_exists"] is False
        assert result["task_exists"] is False
        assert result["file_count"] == 0


class TestFileMonitor:
    """Test cases for FileMonitor worker."""

    def test_init_default(self):
        """Test initialization with default file patterns."""
        worker = FileMonitor()
        assert "*.py" in worker.file_patterns
        assert "*.md" in worker.file_patterns

    def test_init_custom_patterns(self):
        """Test initialization with custom file patterns."""
        patterns = ["*.txt", "*.log"]
        worker = FileMonitor(patterns)
        assert worker.file_patterns == patterns

    def test_run_with_files(self, tmp_path):
        """Test running with files in repository."""
        # Create test files
        (tmp_path / "test.py").write_text("print('hello')")
        (tmp_path / "readme.md").write_text("# Test")
        (tmp_path / "data.json").write_text('{"key": "value"}')

        worker = FileMonitor(["*.py", "*.md"])
        result = worker.run(tmp_path, Path("dummy_task"))

        assert result["worker_name"] == "FileMonitor"
        assert result["total_files_found"] == 2
        assert result["file_breakdown"]["*.py"]["count"] == 1
        assert result["file_breakdown"]["*.md"]["count"] == 1
        assert result["file_breakdown"]["*.py"]["size_bytes"] > 0

    def test_run_with_nonexistent_repo(self):
        """Test running with non-existent repository."""
        worker = FileMonitor()
        result = worker.run(Path("/nonexistent"), Path("dummy_task"))

        assert "error" in result
        assert result["repo_path"] == "/nonexistent"


class TestTaskProcessor:
    """Test cases for TaskProcessor worker."""

    def test_init_default(self):
        """Test initialization with default file size limit."""
        worker = TaskProcessor()
        assert worker.max_file_size == 10 * 1024 * 1024  # 10MB

    def test_init_custom_size(self):
        """Test initialization with custom file size limit."""
        worker = TaskProcessor(1024)  # 1KB
        assert worker.max_file_size == 1024

    def test_run_single_file(self, tmp_path):
        """Test processing a single file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!\nLine 2\nLine 3")

        worker = TaskProcessor()
        result = worker.run(tmp_path, test_file)

        assert result["worker_name"] == "TaskProcessor"
        assert result["total_files_processed"] == 1
        assert len(result["processed_files"]) == 1

        file_info = result["processed_files"][0]
        assert file_info["file_path"] == str(test_file)
        assert file_info["file_type"] == ".txt"
        assert file_info["line_count"] == 3
        assert "Hello, World!" in file_info["content_preview"]

    def test_run_directory(self, tmp_path):
        """Test processing a directory with multiple files."""
        (tmp_path / "file1.py").write_text("print('hello')")
        (tmp_path / "file2.md").write_text("# Title")

        worker = TaskProcessor()
        result = worker.run(tmp_path, tmp_path)

        assert result["total_files_processed"] == 2
        assert len(result["processed_files"]) == 2

    def test_run_with_large_file(self, tmp_path):
        """Test processing a file that exceeds size limit."""
        # Create a large file (smaller than our test limit)
        worker = TaskProcessor(100)  # 100 byte limit
        large_file = tmp_path / "large.txt"
        large_file.write_text("x" * 200)  # 200 bytes

        result = worker.run(tmp_path, large_file)

        file_info = result["processed_files"][0]
        assert "too large" in file_info["error"].lower()

    def test_run_nonexistent_task(self):
        """Test processing non-existent task path."""
        worker = TaskProcessor()
        result = worker.run(Path("/dummy/repo"), Path("/nonexistent/task"))

        assert "error" in result
        assert "does not exist" in result["error"]

    def test_binary_file_handling(self, tmp_path):
        """Test handling of binary files."""
        binary_file = tmp_path / "binary.bin"
        binary_file.write_bytes(b"\x00\x01\x02\x03\x04")

        worker = TaskProcessor()
        result = worker.run(tmp_path, binary_file)

        file_info = result["processed_files"][0]
        assert file_info["file_type"] == ".bin"
        # Binary files should either have line_count as None or 1 (since counting lines on binary content is unreliable)
        assert file_info["line_count"] in [None, 1]


class TestHeartbeatWorker:
    """Test cases for HeartbeatWorker."""

    def test_init_default(self):
        """Test initialization with default message."""
        worker = HeartbeatWorker()
        assert "Auto-slopp is running" in worker.message

    def test_init_custom_message(self):
        """Test initialization with custom message."""
        message = "Custom heartbeat"
        worker = HeartbeatWorker(message)
        assert worker.message == message

    def test_run(self, tmp_path):
        """Test running heartbeat worker."""
        worker = HeartbeatWorker("Test heartbeat")
        result = worker.run(tmp_path / "repo", tmp_path / "task")

        assert result["worker_name"] == "HeartbeatWorker"
        assert result["message"] == "Test heartbeat"
        assert result["repo_path"] == str(tmp_path / "repo")
        assert result["task_path"] == str(tmp_path / "task")
        assert "timestamp" in result
        assert result["timestamp"] is not None
