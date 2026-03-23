"""Tests for Executor class and worker registration."""

from auto_slopp.executor import ALL_WORKERS
from auto_slopp.workers import (
    GitHubIssueWorker,
    PRWorker,
    StaleBranchCleanupWorker,
    VikunjaWorker,
)


class TestWorkerRegistration:
    """Test cases for worker registration in executor."""

    def test_all_workers_includes_github_issue_worker(self):
        """Test that GitHubIssueWorker is registered in ALL_WORKERS."""
        worker_classes = [w.__name__ for w in ALL_WORKERS]
        assert "GitHubIssueWorker" in worker_classes

    def test_all_workers_includes_pr_worker(self):
        """Test that PRWorker is registered in ALL_WORKERS."""
        worker_classes = [w.__name__ for w in ALL_WORKERS]
        assert "PRWorker" in worker_classes

    def test_all_workers_includes_stale_branch_cleanup_worker(self):
        """Test that StaleBranchCleanupWorker is registered in ALL_WORKERS."""
        worker_classes = [w.__name__ for w in ALL_WORKERS]
        assert "StaleBranchCleanupWorker" in worker_classes

    def test_all_workers_includes_vikunja_worker(self):
        """Test that VikunjaWorker is registered in ALL_WORKERS."""
        worker_classes = [w.__name__ for w in ALL_WORKERS]
        assert "VikunjaWorker" in worker_classes

    def test_all_workers_count(self):
        """Test that ALL_WORKERS contains all expected workers."""
        expected_count = 4
        assert len(ALL_WORKERS) == expected_count, (
            f"Expected {expected_count} workers in ALL_WORKERS, "
            f"but found {len(ALL_WORKERS)}: {[w.__name__ for w in ALL_WORKERS]}"
        )

    def test_all_workers_are_worker_subclasses(self):
        """Test that all items in ALL_WORKERS are Worker subclasses."""
        from auto_slopp.worker import Worker

        for worker_class in ALL_WORKERS:
            assert issubclass(worker_class, Worker), f"{worker_class.__name__} is not a Worker subclass"

    def test_all_workers_importable_from_workers_module(self):
        """Test that all workers in ALL_WORKERS can be imported from workers module."""
        for worker_class in ALL_WORKERS:
            assert worker_class in [
                GitHubIssueWorker,
                PRWorker,
                StaleBranchCleanupWorker,
                VikunjaWorker,
            ], f"{worker_class.__name__} not found in workers module exports"
