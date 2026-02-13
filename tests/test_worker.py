"""Tests for worker module."""

from pathlib import Path

import pytest

from auto_slopp.worker import Worker


class DummyWorker(Worker):
    """Dummy worker implementation for testing."""

    name = "dummy"

    def run(self, repo_path: Path, task_path: Path) -> dict:
        """Run the worker."""
        return {"status": "success", "repo": str(repo_path), "task": str(task_path)}


class TestWorker:
    """Test cases for Worker base class."""

    def test_worker_is_abc(self):
        """Test that Worker is an abstract class."""
        with pytest.raises(TypeError):
            Worker()

    def test_dummy_worker_run(self, tmp_path):
        """Test that DummyWorker can run."""
        worker = DummyWorker()

        result = worker.run(tmp_path, tmp_path / "task.txt")

        assert result["status"] == "success"
        assert result["repo"] == str(tmp_path)
        assert result["task"] == str(tmp_path / "task.txt")

    def test_worker_name_attribute(self):
        """Test that worker has name attribute."""
        worker = DummyWorker()
        assert worker.name == "dummy"
