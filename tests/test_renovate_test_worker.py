"""Tests for renovate_test_worker module."""

from pathlib import Path

import pytest

from auto_slopp.workers.renovate_test_worker import RenovateTestWorker


class TestRenovateTestWorker:
    """Test cases for RenovateTestWorker class."""

    def test_worker_name(self):
        """Test that worker has correct name."""
        worker = RenovateTestWorker()
        assert worker.name == "renovate_test"

    def test_worker_run(self, tmp_path):
        """Test that worker run method works."""
        worker = RenovateTestWorker()

        result = worker.run(tmp_path, tmp_path / "task.txt")

        assert result["status"] == "completed"
        assert result["repo"] == str(tmp_path)
