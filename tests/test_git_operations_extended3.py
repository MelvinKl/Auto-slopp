"""Even more extended tests for git operations utilities."""

from pathlib import Path
from unittest.mock import patch

from auto_slopp.utils.git_operations import (
    commit_all_changes,
    get_ahead_behind,
    is_git_repo,
)


class TestGetAheadBehind:
    """Tests for get_ahead_behind function."""

    @patch("auto_slopp.utils.git_operations._run_git_command")
    def test_get_ahead_behind_exception(self, mock_run_git):
        """Test get_ahead_behind raises exception and returns 0, 0."""
        repo_dir = Path("/tmp/test_repo")
        mock_run_git.side_effect = Exception("unexpected error")

        behind, ahead = get_ahead_behind(repo_dir, "origin", "main")

        assert behind == 0
        assert ahead == 0


class TestIsGitRepo:
    """Tests for is_git_repo function."""

    @patch("auto_slopp.utils.git_operations.subprocess.run")
    def test_is_git_repo_exception(self, mock_subprocess_run):
        """Test is_git_repo raises exception and returns False."""
        repo_dir = Path("/tmp/test_repo")
        mock_subprocess_run.side_effect = Exception("subprocess error")

        result = is_git_repo(repo_dir)

        assert result is False


class TestCommitAllChanges:
    """Tests for commit_all_changes function."""

    @patch("auto_slopp.utils.git_operations.is_git_repo")
    def test_commit_all_changes_not_git_repo(self, mock_is_git_repo):
        """Test commit_all_changes when not a git repo."""
        repo_dir = Path("/tmp/test_repo")
        mock_is_git_repo.return_value = False

        success, message = commit_all_changes(repo_dir, "message")

        assert success is False
        assert "not a git repository" in message

    @patch("auto_slopp.utils.git_operations.is_git_repo")
    @patch("auto_slopp.utils.git_operations.has_changes")
    def test_commit_all_changes_no_changes(self, mock_has_changes, mock_is_git_repo):
        """Test commit_all_changes when no changes."""
        repo_dir = Path("/tmp/test_repo")
        mock_is_git_repo.return_value = True
        mock_has_changes.return_value = False

        success, message = commit_all_changes(repo_dir, "message")

        assert success is True
        assert message == "No changes to commit"
