"""Tests for stale_branch_cleanup_worker module."""

from pathlib import Path

import pytest

from auto_slopp.workers.stale_branch_cleanup_worker import StaleBranchCleanupWorker


class TestStaleBranchCleanupWorker:
    """Test cases for StaleBranchCleanupWorker class."""

    def test_worker_name(self):
        """Test that worker has correct name."""
        worker = StaleBranchCleanupWorker()
        assert worker.name == "stale_branch_cleanup"

    def test_worker_run(self, tmp_path):
        """Test that worker run method works."""
        worker = StaleBranchCleanupWorker()

        result = worker.run(tmp_path, tmp_path / "task.txt")

        assert result["status"] == "completed"
        assert result["repo"] == str(tmp_path)
