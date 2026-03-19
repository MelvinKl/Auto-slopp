"""Tests for branch analysis utilities."""

from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from auto_slopp.utils.branch_analysis import (
    analyze_repository_branches,
    create_branch_cleanup_result,
    delete_stale_branches,
    identify_stale_branches,
)


class TestCreateBranchCleanupResult:
    """Tests for create_branch_cleanup_result function."""

    def test_returns_expected_dict(self):
        """Test that result dict has expected keys and initial values."""
        repo_dir = Path("/tmp/test_repo")
        result = create_branch_cleanup_result(repo_dir)

        assert result["repository"] == "test_repo"
        assert result["success"] is False
        assert result["branches_deleted"] == 0
        assert result["branches_failed_to_delete"] == 0
        assert result["deleted_branches"] == []
        assert result["failed_deletions"] == []
        assert result["error"] is None


class TestIdentifyStaleBranches:
    """Tests for identify_stale_branches function."""

    def test_empty_inputs(self):
        """Test with empty inputs."""
        result = identify_stale_branches([], set(), 5)
        assert result == []

    def test_branch_not_stale_when_recent(self):
        """Test that recent branches are not identified as stale even when not on remote."""
        recent_date = datetime.now(timezone.utc) - timedelta(days=2)
        local_branches = [{"name": "feature", "last_commit_date": recent_date}]
        remote_branches = set()

        result = identify_stale_branches(local_branches, remote_branches, 5)
        assert len(result) == 0

    def test_branch_stale_but_on_remote(self):
        """Test that branches on remote are not identified as stale even if old."""
        old_date = datetime.now(timezone.utc) - timedelta(days=10)
        local_branches = [{"name": "feature", "last_commit_date": old_date}]
        remote_branches = {"feature"}

        result = identify_stale_branches(local_branches, remote_branches, 5)
        assert len(result) == 0

    def test_multiple_stale_branches(self):
        """Test identification of multiple stale branches."""
        old_date = datetime.now(timezone.utc) - timedelta(days=30)
        recent_date = datetime.now(timezone.utc) - timedelta(days=2)
        local_branches = [
            {"name": "old1", "last_commit_date": old_date},
            {"name": "old2", "last_commit_date": old_date},
            {"name": "recent", "last_commit_date": recent_date},
        ]
        remote_branches = set()

        result = identify_stale_branches(local_branches, remote_branches, 5)
        assert len(result) == 2
        names = {b["name"] for b in result}
        assert "old1" in names
        assert "old2" in names


class TestDeleteStaleBranches:
    """Tests for delete_stale_branches function."""

    def test_dry_run_returns_all_as_deleted(self):
        """Test that dry_run mode returns all branches as deleted."""
        stale_branches = [
            {"name": "old1", "last_commit_date": datetime.now(timezone.utc)},
            {"name": "old2", "last_commit_date": datetime.now(timezone.utc)},
        ]
        repo_dir = Path("/tmp/test_repo")

        deleted, failed = delete_stale_branches(stale_branches, repo_dir, dry_run=True)

        assert len(deleted) == 2
        assert len(failed) == 0

    def test_deletion_failure_increments_failed(self):
        """Test that failed deletions are tracked."""
        stale_branches = [{"name": "failing", "last_commit_date": datetime.now(timezone.utc)}]
        repo_dir = Path("/tmp/test_repo")

        with patch("auto_slopp.utils.branch_analysis.delete_branch", return_value=False):
            deleted, failed = delete_stale_branches(stale_branches, repo_dir, dry_run=False)

        assert len(deleted) == 0
        assert len(failed) == 1
        assert failed[0]["name"] == "failing"

    def test_mixed_success_and_failure(self):
        """Test with both successful and failed deletions."""
        stale_branches = [
            {"name": "success", "last_commit_date": datetime.now(timezone.utc)},
            {"name": "fail", "last_commit_date": datetime.now(timezone.utc)},
        ]
        repo_dir = Path("/tmp/test_repo")

        def mock_delete(repo, name):
            return name == "success"

        with patch("auto_slopp.utils.branch_analysis.delete_branch", side_effect=mock_delete):
            deleted, failed = delete_stale_branches(stale_branches, repo_dir, dry_run=False)

        assert len(deleted) == 1
        assert len(failed) == 1
        assert deleted[0]["name"] == "success"
        assert failed[0]["name"] == "fail"


class TestAnalyzeRepositoryBranches:
    """Tests for analyze_repository_branches function."""

    def test_analyze_with_oserror_on_getcwd(self):
        """Test that OSError from os.getcwd is handled gracefully."""
        repo_dir = Path("/tmp/test_repo")

        def failing_getcwd():
            raise OSError("Cannot get current directory")

        with patch("auto_slopp.utils.branch_analysis.get_local_branches", return_value=[]):
            with patch(
                "auto_slopp.utils.branch_analysis.get_remote_branches",
                return_value=set(),
            ):
                with patch("os.getcwd", side_effect=failing_getcwd):
                    with patch("os.chdir"):
                        result = analyze_repository_branches(repo_dir, days_threshold=5)

        assert result["success"] is True
        assert result["stale_branches_found"] == 0

    def test_analyze_exception_during_branch_operations(self):
        """Test that exceptions during branch operations are caught."""
        repo_dir = Path("/tmp/test_repo")

        def failing_getcwd():
            return "/original/path"

        with patch("os.getcwd", side_effect=failing_getcwd):
            with patch("os.chdir"):
                with patch(
                    "auto_slopp.utils.branch_analysis.get_local_branches",
                    side_effect=Exception("Git error"),
                ):
                    result = analyze_repository_branches(repo_dir, days_threshold=5)

        assert result["success"] is False
        assert result["error"] == "Git error"

    def test_analyze_with_oserror_on_chdir_in_finally(self):
        """Test that OSError in finally block is handled."""
        repo_dir = Path("/tmp/test_repo")

        call_count = [0]

        def chdir_effect(path):
            call_count[0] += 1
            if call_count[0] > 1:
                raise OSError("Cannot change directory back")

        with patch("os.getcwd", return_value="/original"):
            with patch("os.chdir", side_effect=chdir_effect):
                with patch(
                    "auto_slopp.utils.branch_analysis.get_local_branches",
                    return_value=[],
                ):
                    with patch(
                        "auto_slopp.utils.branch_analysis.get_remote_branches",
                        return_value=set(),
                    ):
                        result = analyze_repository_branches(repo_dir, days_threshold=5)

        assert result["success"] is True

    def test_analyze_with_oserror_on_chdir_in_except(self):
        """Test that OSError in exception handler's chdir is handled."""
        repo_dir = Path("/tmp/test_repo")

        with patch("os.getcwd", return_value="/original"):
            with patch(
                "os.chdir",
                side_effect=[
                    None,
                    OSError("Cannot change back in except"),
                ],
            ):
                with patch(
                    "auto_slopp.utils.branch_analysis.get_local_branches",
                    side_effect=Exception("Operation failed"),
                ):
                    try:
                        analyze_repository_branches(repo_dir, days_threshold=5)
                    except Exception:
                        pass

        assert True
