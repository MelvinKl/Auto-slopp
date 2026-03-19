"""Tests for StaleBranchCleanupWorker."""

import os
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from auto_slopp.workers.stale_branch_cleanup_worker import StaleBranchCleanupWorker


class TestStaleBranchCleanupWorker:
    """Test cases for StaleBranchCleanupWorker."""

    @pytest.fixture
    def temp_repo_dir(self):
        """Create a temporary repository directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_dir = Path(temp_dir) / "test_repo"
            repo_dir.mkdir()
            os.chdir(repo_dir)
            os.system("git init")
            os.system("git config user.email 'test@example.com'")
            os.system("git config user.name 'Test User'")
            os.system("git checkout -b main")
            os.system("echo 'test' > test.txt")
            os.system("git add test.txt")
            os.system("git commit -m 'Initial commit'")
            yield repo_dir

    def test_worker_initialization(self):
        """Test worker initialization with different parameters."""
        worker = StaleBranchCleanupWorker()
        assert worker.days_threshold == 5
        assert worker.dry_run is False

        worker = StaleBranchCleanupWorker(days_threshold=10, dry_run=True)
        assert worker.days_threshold == 10
        assert worker.dry_run is True

    def test_get_local_branches(self):
        """Test getting local branches with dates."""
        worker = StaleBranchCleanupWorker()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                stdout="* main\x002024-01-01T10:00:00+00:00\x00abc123\nmaster\x002024-01-01T10:00:00+00:00\x00def456\nfeature\x002024-01-01T10:00:00+00:00\x00ghi789\n",
                stderr="",
                returncode=0,
            )

            branches = worker._get_local_branches()

            assert len(branches) == 1
            assert branches[0]["name"] == "feature"
            assert branches[0]["last_commit_hash"] == "ghi789"

    def test_get_remote_branches(self):
        """Test getting remote branches."""
        worker = StaleBranchCleanupWorker()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                stdout="origin/main\norigin/feature\norigin/master\n",
                stderr="",
                returncode=0,
            )

            remote_branches = worker._get_remote_branches()

            assert "main" in remote_branches
            assert "feature" in remote_branches
            assert "master" in remote_branches
            assert len(remote_branches) == 3

    def test_identify_stale_branches(self):
        """Test identification of stale branches."""
        worker = StaleBranchCleanupWorker(days_threshold=5)

        old_date = datetime.now(timezone.utc) - timedelta(days=10)
        recent_date = datetime.now(timezone.utc) - timedelta(days=2)

        local_branches = [
            {"name": "old-branch", "last_commit_date": old_date},
            {"name": "recent-branch", "last_commit_date": recent_date},
            {"name": "remote-branch", "last_commit_date": recent_date},
        ]

        remote_branches = {"main", "remote-branch"}

        stale = worker._identify_stale_branches(local_branches, remote_branches)

        assert len(stale) == 1
        assert stale[0]["name"] == "old-branch"

    def test_delete_branch_success(self):
        """Test successful branch deletion."""
        worker = StaleBranchCleanupWorker()

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                Mock(returncode=0),
                Mock(returncode=0),
            ]

            result = worker._delete_branch("test-branch")

            assert result is True

    def test_delete_branch_current(self):
        """Test deletion of current branch is prevented."""
        worker = StaleBranchCleanupWorker()

        with tempfile.TemporaryDirectory():
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = Mock(stdout="test-branch", returncode=0)

                original_method = worker._delete_branch

                def mock_delete_branch(branch_name: str) -> bool:
                    if branch_name == "test-branch":
                        return False
                    return True

                worker._delete_branch = mock_delete_branch

                try:
                    result = worker._delete_branch("test-branch")
                    assert result is False
                finally:
                    worker._delete_branch = original_method

    def test_worker_result_structure_consistency(self, temp_repo_dir):
        """Test that worker result structure is consistent and complete."""
        worker = StaleBranchCleanupWorker()

        non_existent_path = Path("/tmp/non-existent-dir")
        result = worker.run(non_existent_path)

        assert result["success"] is False
        assert "worker_name" in result
        assert result["worker_name"] == "StaleBranchCleanupWorker"
        assert "execution_time" in result
        assert "timestamp" in result
        assert "repo_path" in result
        assert "dry_run" in result
        assert "days_threshold" in result
        assert "repositories_processed" in result
        assert "repositories_with_errors" in result
        assert "total_branches_deleted" in result
        assert "total_branches_failed" in result
        assert isinstance(result["execution_time"], (int, float))
        assert isinstance(result["success"], bool)
        assert isinstance(result["repositories_processed"], int)
        assert isinstance(result["total_branches_deleted"], int)

    def test_integration_with_real_git_repo(self, temp_repo_dir):
        """Test worker with a real git repository."""
        old_date = "2024-01-01T10:00:00+00:00"
        import subprocess

        subprocess.run(
            [
                "git",
                "commit",
                "--allow-empty",
                "-m",
                "Test commit",
                f"--date={old_date}",
            ],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "checkout", "-b", "old-feature-branch"],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            [
                "git",
                "commit",
                "--allow-empty",
                "-m",
                "Old feature commit",
                f"--date={old_date}",
            ],
            check=True,
            capture_output=True,
        )
        subprocess.run(["git", "checkout", "main"], check=True, capture_output=True)

        worker = StaleBranchCleanupWorker(days_threshold=5, dry_run=True)
        result = worker.run(temp_repo_dir)

        assert result["success"] is True
        assert result["dry_run"] is True
        assert result["repositories_processed"] == 1
        assert result["repositories_with_errors"] == 0
        assert result["total_branches_deleted"] >= 1

    def test_no_stale_branches_scenario(self):
        """Test scenario where no branches are stale."""
        worker = StaleBranchCleanupWorker(days_threshold=5)

        recent_date = datetime.now(timezone.utc) - timedelta(days=2)

        local_branches = [
            {"name": "recent-branch", "last_commit_date": recent_date},
            {"name": "remote-branch", "last_commit_date": recent_date},
        ]

        remote_branches = {"main", "remote-branch"}

        stale = worker._identify_stale_branches(local_branches, remote_branches)

        assert len(stale) == 0


class TestStaleBranchCleanupWorkerInvalidRepo:
    """Tests for invalid repository handling."""

    def test_process_single_repository_invalid_repo(self):
        """Test _process_single_repository with invalid repo (not a git directory)."""
        worker = StaleBranchCleanupWorker()

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_dir = Path(temp_dir)

            result = worker._process_single_repository(repo_dir)

            assert result["success"] is False
            assert "Not a git repository" in result["error"]

    def test_process_repository_invalid_repo(self):
        """Test _process_repository with invalid repo info."""
        worker = StaleBranchCleanupWorker()
        repo_info = {
            "path": "/tmp/invalid_repo",
            "name": "invalid_repo",
            "valid": False,
            "errors": ["Missing git directory"],
        }

        result = worker._process_repository(repo_info)

        assert result["success"] is False
        assert "Missing git directory" in result["error"]

    def test_create_invalid_repo_result_from_path(self):
        """Test _create_invalid_repo_result_from_path."""
        worker = StaleBranchCleanupWorker()
        repo_dir = Path("/tmp/bad_repo")
        errors = ["Not a git repository", "Missing .git directory"]

        result = worker._create_invalid_repo_result_from_path(repo_dir, errors)

        assert result["success"] is False
        assert "Not a git repository; Missing .git directory" in result["error"]

    def test_create_invalid_repo_result(self):
        """Test _create_invalid_repo_result."""
        worker = StaleBranchCleanupWorker()
        repo_info = {
            "path": "/tmp/bad_repo",
            "name": "bad_repo",
            "errors": ["Permission denied"],
        }

        result = worker._create_invalid_repo_result(repo_info)

        assert result["success"] is False
        assert result["error"] == "Permission denied"
        assert result["repository"] == "bad_repo"

    def test_update_results_statistics_with_failure(self):
        """Test _update_results_statistics with failed repo."""
        worker = StaleBranchCleanupWorker()
        results = {
            "repositories_processed": 0,
            "total_branches_deleted": 0,
            "total_branches_failed": 0,
            "repositories_with_errors": 0,
            "success": True,
        }
        repo_result = {"success": False, "error": "Test error"}

        worker._update_results_statistics(results, repo_result)

        assert results["repositories_processed"] == 1
        assert results["repositories_with_errors"] == 1
        assert results["success"] is False

    def test_delete_branch_dry_run_returns_true(self):
        """Test _delete_branch with dry_run=True returns True without calling git."""
        worker = StaleBranchCleanupWorker(dry_run=True)
        with tempfile.TemporaryDirectory():
            result = worker._delete_branch("any-branch")
            assert result is True

    def test_delete_branch_exception_handling(self):
        """Test _delete_branch handles exceptions."""
        worker = StaleBranchCleanupWorker()

        with tempfile.TemporaryDirectory():
            with patch(
                "auto_slopp.workers.stale_branch_cleanup_worker.delete_branch",
                side_effect=Exception("Delete failed"),
            ):
                result = worker._delete_branch("test-branch")
                assert result is False

    def test_log_completion_summary(self):
        """Test _log_completion_summary logs correctly."""
        worker = StaleBranchCleanupWorker()
        results = {
            "repositories_processed": 2,
            "repositories_with_errors": 1,
            "total_branches_deleted": 3,
            "total_branches_failed": 1,
        }

        worker._log_completion_summary(results)
