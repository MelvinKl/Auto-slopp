"""Tests for task_processor_worker module."""

from pathlib import Path

import pytest

from auto_slopp.workers.task_processor_worker import TaskProcessorWorker


class TestTaskProcessorWorker:
    """Test cases for TaskProcessorWorker class."""

    def test_worker_name(self):
        """Test that worker has correct name."""
        worker = TaskProcessorWorker()
        assert worker.name == "task_processor"

    def test_worker_run(self, tmp_path):
        """Test that worker run method works."""
        worker = TaskProcessorWorker()

        result = worker.run(tmp_path, tmp_path / "task.txt")

        assert result["status"] == "completed"
        assert result["repo"] == str(tmp_path)
