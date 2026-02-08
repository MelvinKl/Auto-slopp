"""Tests for StaleBranchCleanupWorker."""

import os
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import Mock, patch

from auto_slopp.workers.stale_branch_cleanup_worker import (
    StaleBranchCleanupWorker,
)


class TestStaleBranchCleanupWorker:
    """Test cases for StaleBranchCleanupWorker."""

    def test_worker_inherits_from_base_class(self):
        """Test that StaleBranchCleanupWorker properly inherits from Worker base."""
        worker = StaleBranchCleanupWorker()
        assert hasattr(worker, "run")
        assert callable(getattr(worker, "run"))

    def test_worker_initialization_default_values(self):
        """Test worker initialization with default values."""
        worker = StaleBranchCleanupWorker()
        assert worker.days_threshold == 5
        assert worker.dry_run is False
        assert worker.logger is not None

    def test_worker_initialization_custom_values(self):
        """Test worker initialization with custom values."""
        worker = StaleBranchCleanupWorker(days_threshold=10, dry_run=True)
        assert worker.days_threshold == 10
        assert worker.dry_run is True

    def test_get_local_branches_success(self):
        """Test successful parsing of local branches output."""
        worker = StaleBranchCleanupWorker()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                stdout="* main\x002024-02-01T10:00:00+00:00\x00abc123\nfeature-1\x002024-01-01T10:00:00+00:00\x00def456\n",
                stderr="",
                returncode=0,
            )

            branches = worker._get_local_branches()

            assert len(branches) == 1  # main/master branches are filtered out
            assert branches[0]["name"] == "feature-1"
            assert branches[0]["last_commit_hash"] == "def456"
            assert isinstance(branches[0]["last_commit_date"], datetime)
            assert branches[0]["days_old"] > 0

    def test_get_local_branches_handles_empty_output(self):
        """Test handling of empty git branch output."""
        worker = StaleBranchCleanupWorker()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(stdout="", stderr="", returncode=0)

            branches = worker._get_local_branches()
            assert branches == []

    def test_get_remote_branches_success(self):
        """Test successful parsing of remote branches output."""
        worker = StaleBranchCleanupWorker()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                stdout="origin/main\norigin/feature-1\norigin/HEAD -> origin/main\n",
                stderr="",
                returncode=0,
            )

            branches = worker._get_remote_branches()

            assert "main" in branches
            assert "feature-1" in branches
            assert "HEAD" not in branches  # HEAD entries should be filtered out

    def test_identify_stale_branches(self):
        """Test identification of stale branches."""
        worker = StaleBranchCleanupWorker(days_threshold=5)

        old_date = datetime.now(timezone.utc) - timedelta(days=10)
        recent_date = datetime.now(timezone.utc) - timedelta(days=2)

        local_branches = [
            {"name": "old-branch", "last_commit_date": old_date},
            {"name": "recent-branch", "last_commit_date": recent_date},
            {"name": "remote-branch", "last_commit_date": old_date},
        ]

        remote_branches = {"main", "remote-branch"}

        stale = worker._identify_stale_branches(local_branches, remote_branches)

        assert len(stale) == 1
        assert stale[0]["name"] == "old-branch"

    def test_identify_stale_branches_with_custom_threshold(self):
        """Test stale branch identification with custom threshold."""
        worker = StaleBranchCleanupWorker(days_threshold=15)

        old_date = datetime.now(timezone.utc) - timedelta(days=10)
        very_old_date = datetime.now(timezone.utc) - timedelta(days=20)

        local_branches = [
            {"name": "somewhat-old", "last_commit_date": old_date},
            {"name": "very-old", "last_commit_date": very_old_date},
        ]

        remote_branches = set()

        stale = worker._identify_stale_branches(local_branches, remote_branches)

        assert len(stale) == 1
        assert stale[0]["name"] == "very-old"

    def test_delete_branch_success(self):
        """Test successful branch deletion."""
        worker = StaleBranchCleanupWorker()

        with patch("subprocess.run") as mock_run:
            # Mock current branch check and deletion
            mock_run.side_effect = [
                Mock(stdout="main\n", stderr="", returncode=0),  # current branch
                Mock(stdout="", stderr="", returncode=0),  # deletion
            ]

            result = worker._delete_branch("feature-branch")
            assert result is True

    def test_delete_branch_current_branch_protection(self):
        """Test that current branch cannot be deleted."""
        worker = StaleBranchCleanupWorker()

        with patch("subprocess.run") as mock_run:
            # Mock current branch as the one being deleted
            mock_run.return_value = Mock(
                stdout="feature-branch\n", stderr="", returncode=0
            )

            result = worker._delete_branch("feature-branch")
            assert result is False

    def test_delete_branch_git_failure(self):
        """Test handling of git deletion failure."""
        worker = StaleBranchCleanupWorker()

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                Mock(stdout="main\n", stderr="", returncode=0),  # current branch
                subprocess.CalledProcessError(
                    1, "git", "branch not found"
                ),  # deletion failure
            ]

            result = worker._delete_branch("non-existent-branch")
            assert result is False

    def test_integration_with_real_git_repo(self, temp_repo_dir, temp_task_dir):
        """Test integration with a real git repository."""
        # Initialize a git repository
        os.chdir(temp_repo_dir)
        subprocess.run(["git", "init"], check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            check=True,
            capture_output=True,
        )

        # Create initial commit
        subprocess.run(
            ["git", "commit", "--allow-empty", "-m", "Initial commit"],
            check=True,
            capture_output=True,
        )

        # Create a feature branch with an old commit
        subprocess.run(
            ["git", "checkout", "-b", "old-feature"],
            check=True,
            capture_output=True,
        )

        # Use environment variable to override the date for testing
        old_date = "2024-01-01T10:00:00Z"
        subprocess.run(
            [
                "git",
                "commit",
                "--allow-empty",
                "-m",
                "Old feature",
                "--date",
                old_date,
            ],
            env=dict(
                os.environ,
                GIT_COMMITTER_DATE=old_date,
                GIT_AUTHOR_DATE=old_date,
            ),
            check=True,
            capture_output=True,
        )

        # Go back to main
        subprocess.run(["git", "checkout", "main"], check=True, capture_output=True)

        # Test with a worker
        worker = StaleBranchCleanupWorker(days_threshold=5, dry_run=True)
        result = worker.run(temp_repo_dir, temp_task_dir)

        # Should find the old branch as stale (since it's not on remote)
        assert result["success"] is True
        assert result["dry_run"] is True
        assert result["total_local_branches"] >= 1  # Should find our test branch
        assert (
            result["branches_deleted"] >= 1
        )  # In dry run, branches_deleted means "would be deleted"

    def test_worker_result_structure_consistency(self, temp_repo_dir, temp_task_dir):
        """Test that worker result structure is consistent and complete."""
        worker = StaleBranchCleanupWorker()

        # Test with non-existent directory to trigger error path
        non_existent_path = Path("/tmp/non-existent-dir")
        result = worker.run(non_existent_path, temp_task_dir)

        # Should handle error gracefully
        assert result["success"] is False
        assert "worker_name" in result
        assert result["worker_name"] == "StaleBranchCleanupWorker"
        assert "execution_time" in result
        assert "timestamp" in result
        assert "repo_path" in result
        assert "task_path" in result
        assert "dry_run" in result
        assert "days_threshold" in result
        assert isinstance(result["execution_time"], (int, float))
        assert isinstance(result["success"], bool)
        assert isinstance(result["branches_deleted"], list)
        assert isinstance(result["failed_deletions"], list)

    def test_branch_filtering_excludes_main_branches(self):
        """Test that main/master branches are excluded from consideration."""
        worker = StaleBranchCleanupWorker()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                stdout="* main\x002024-01-01T10:00:00+00:00\x00abc123\nmaster\x002024-01-01T10:00:00+00:00\x00def456\nfeature\x002024-01-01T10:00:00+00:00\x00ghi789\n",
                stderr="",
                returncode=0,
            )

            branches = worker._get_local_branches()

            # Should only include feature branch, not main or master
            assert len(branches) == 1
            assert branches[0]["name"] == "feature"

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

    def test_all_stale_branches_scenario(self):
        """Test scenario where all eligible branches are stale."""
        worker = StaleBranchCleanupWorker(days_threshold=5)

        old_date = datetime.now(timezone.utc) - timedelta(days=10)

        local_branches = [
            {"name": "old-branch-1", "last_commit_date": old_date},
            {"name": "old-branch-2", "last_commit_date": old_date},
        ]

        remote_branches = {"main"}  # Neither branch exists on remote

        stale = worker._identify_stale_branches(local_branches, remote_branches)

        assert len(stale) == 2
        assert {b["name"] for b in stale} == {"old-branch-1", "old-branch-2"}
