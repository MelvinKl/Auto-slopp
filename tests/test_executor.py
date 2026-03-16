"""Tests for Executor class and worker registration."""

from pathlib import Path
from unittest.mock import patch

from auto_slopp.executor import ALL_WORKERS, Executor
from auto_slopp.workers import (
    GitHubIssueWorker,
    OpenProjectWorker,
    PRWorker,
    StaleBranchCleanupWorker,
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

    def test_all_workers_includes_openproject_worker(self):
        """Test that OpenProjectWorker is registered in ALL_WORKERS."""
        worker_classes = [w.__name__ for w in ALL_WORKERS]
        assert "OpenProjectWorker" in worker_classes

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
                OpenProjectWorker,
                PRWorker,
                StaleBranchCleanupWorker,
            ], f"{worker_class.__name__} not found in workers module exports"


class TestExecutorWorkerFiltering:
    """Tests for worker enablement in the executor."""

    def test_openproject_worker_disabled_when_feature_flag_is_false(self):
        """Test that OpenProjectWorker is skipped when OpenProject is disabled."""
        executor = Executor(repo_path=Path("/tmp/repos"))

        with patch("auto_slopp.executor.settings") as mock_settings:
            mock_settings.workers_disabled = []
            mock_settings.openproject_enabled = False

            assert executor._is_worker_enabled(OpenProjectWorker) is False
            assert executor._is_worker_enabled(GitHubIssueWorker) is True

    def test_openproject_worker_enabled_when_feature_flag_is_true(self):
        """Test that OpenProjectWorker runs when enabled and not explicitly disabled."""
        executor = Executor(repo_path=Path("/tmp/repos"))

        with patch("auto_slopp.executor.settings") as mock_settings:
            mock_settings.workers_disabled = []
            mock_settings.openproject_enabled = True

            assert executor._is_worker_enabled(OpenProjectWorker) is True

    def test_worker_disabled_by_name_takes_precedence(self):
        """Test that workers_disabled still disables workers by class name."""
        executor = Executor(repo_path=Path("/tmp/repos"))

        with patch("auto_slopp.executor.settings") as mock_settings:
            mock_settings.workers_disabled = ["PRWorker"]
            mock_settings.openproject_enabled = True

            assert executor._is_worker_enabled(PRWorker) is False
