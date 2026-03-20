"""Tests for git operations utilities."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from auto_slopp.utils.git_operations import (
    branch_exists,
    checkout_branch_resilient,
    create_and_checkout_branch,
    delete_branch,
    get_ahead_behind,
    get_current_branch,
    get_default_branch,
    get_local_branches,
    get_remote_branches,
    get_remotes,
    has_changes,
    is_bare_repository,
    is_git_repo,
    merge_main_into_branch,
    pull_from_remote,
    push_branch,
    sanitize_branch_name,
)


class TestMergeMainIntoBranch:
    """Test cases for merge_main_into_branch function."""

    @patch("auto_slopp.utils.git_operations.get_current_branch")
    @patch("auto_slopp.utils.git_operations._run_git_command")
    def test_merge_main_on_main_branch(self, mock_run_git, mock_get_branch):
        """Test merge main while on main branch."""
        repo_dir = Path("/tmp/test_repo")
        mock_get_branch.return_value = "main"

        # Mock successful fetch and merge
        mock_run_git.side_effect = [
            Mock(returncode=0, stderr=""),  # git fetch origin main
            Mock(returncode=0, stderr=""),  # git merge FETCH_HEAD
        ]

        success, message = merge_main_into_branch(repo_dir, "main")

        assert success is True
        assert message == "Merge successful"
        # Check fetch command was called without :main
        mock_run_git.assert_any_call(repo_dir, "fetch", "origin", "main", check=False, timeout=60)

    @patch("auto_slopp.utils.git_operations.get_current_branch")
    @patch("auto_slopp.utils.git_operations._run_git_command")
    def test_merge_main_on_feature_branch(self, mock_run_git, mock_get_branch):
        """Test merge main while on feature branch."""
        repo_dir = Path("/tmp/test_repo")
        mock_get_branch.return_value = "feature/test"

        # Mock successful fetch and merge
        mock_run_git.side_effect = [
            Mock(returncode=0, stderr=""),  # git fetch origin main:main
            Mock(returncode=0, stderr=""),  # git merge FETCH_HEAD
        ]

        success, message = merge_main_into_branch(repo_dir, "feature/test")

        assert success is True
        assert message == "Merge successful"
        # Check fetch command was called with :main
        mock_run_git.assert_any_call(repo_dir, "fetch", "origin", "main:main", check=False, timeout=60)

    @patch("auto_slopp.utils.git_operations.get_current_branch")
    @patch("auto_slopp.utils.git_operations._run_git_command")
    def test_merge_main_fetch_fails_fallback(self, mock_run_git, mock_get_branch):
        """Test fallback when main:main fetch fails."""
        repo_dir = Path("/tmp/test_repo")
        mock_get_branch.return_value = "feature/test"

        # Mock git commands: first fetch fails, second succeeds, merge succeeds
        mock_run_git.side_effect = [
            Mock(returncode=1, stderr="refusing to fetch into current branch"),  # git fetch origin main:main (fails)
            Mock(returncode=0, stderr=""),  # git fetch origin main (succeeds)
            Mock(returncode=0, stderr=""),  # git merge FETCH_HEAD
        ]

        success, message = merge_main_into_branch(repo_dir, "feature/test")

        assert success is True
        assert message == "Merge successful"
        assert mock_run_git.call_count == 3

    @patch("auto_slopp.utils.git_operations.get_current_branch")
    @patch("auto_slopp.utils.git_operations._run_git_command")
    @patch("auto_slopp.utils.git_operations.get_active_cli_command")
    def test_merge_main_fetch_fails_and_merge_conflict(self, mock_get_cli, mock_run_git, mock_get_branch):
        """Test merge with fetch failure and merge conflict."""
        repo_dir = Path("/tmp/test_repo")
        mock_get_branch.return_value = "feature/test"
        mock_get_cli.return_value = "cli-tool"

        # Mock git commands: first fetch fails, second succeeds, merge fails with conflict
        mock_run_git.side_effect = [
            Mock(returncode=1, stderr="refusing to fetch into current branch"),  # git fetch origin main:main (fails)
            Mock(returncode=0, stderr=""),  # git fetch origin main (succeeds)
            Mock(
                returncode=1, stderr="CONFLICT (content): Merge conflict in file.txt"
            ),  # git merge FETCH_HEAD (conflict)
        ]

        success, message = merge_main_into_branch(repo_dir, "feature/test")

        assert success is False
        assert "Merge conflict detected" in message
        assert "cli-tool attempted resolution" in message
        assert mock_run_git.call_count == 3


class TestCheckoutBranchResilient:
    """Test cases for checkout_branch_resilient function."""

    @patch("auto_slopp.utils.git_operations._run_git_command")
    def test_checkout_success_first_attempt(self, mock_run_git):
        """Test successful checkout on first attempt."""
        repo_dir = Path("/tmp/test_repo")
        branch = "feature/test"

        mock_run_git.side_effect = [
            Mock(returncode=0, stderr=""),  # git fetch
            Mock(returncode=0, stdout=""),  # git checkout
            Mock(returncode=0, stderr=""),  # git pull
        ]

        result = checkout_branch_resilient(repo_dir, branch)

        assert result is True
        assert mock_run_git.call_count == 3

    @patch("auto_slopp.utils.git_operations._run_git_command")
    def test_checkout_fetch_fails_continues(self, mock_run_git):
        """Test checkout continues when fetch fails."""
        repo_dir = Path("/tmp/test_repo")
        branch = "feature/test"

        mock_run_git.side_effect = [
            Mock(returncode=1, stderr="fetch failed"),  # git fetch (fails)
            Mock(returncode=0, stdout=""),  # git checkout (succeeds)
            Mock(returncode=0, stderr=""),  # git pull (succeeds)
        ]

        result = checkout_branch_resilient(repo_dir, branch)

        assert result is True
        assert mock_run_git.call_count == 3

    @patch("auto_slopp.utils.git_operations._run_git_command")
    def test_checkout_fetch_fails_checkout_fails_reset_succeeds_clean_succeeds_retry_succeeds(self, mock_run_git):
        """Test checkout with fetch failure, checkout failure, reset success, clean success, retry success."""
        repo_dir = Path("/tmp/test_repo")
        branch = "feature/test"

        mock_run_git.side_effect = [
            Mock(returncode=1, stderr="fetch failed"),  # git fetch (fails)
            Mock(returncode=1, stderr="checkout failed"),  # git checkout (fails)
            Mock(returncode=0, stderr=""),  # git reset --hard (succeeds)
            Mock(returncode=0, stderr=""),  # git clean -fd (succeeds)
            Mock(returncode=0, stdout=""),  # git checkout (succeeds on retry)
            Mock(returncode=0, stderr=""),  # git pull (succeeds)
        ]

        result = checkout_branch_resilient(repo_dir, branch)

        assert result is True
        assert mock_run_git.call_count == 6

    @patch("auto_slopp.utils.git_operations._run_git_command")
    def test_checkout_fetch_fails_checkout_fails_reset_fails(self, mock_run_git):
        """Test checkout with fetch failure, checkout failure, reset failure."""
        repo_dir = Path("/tmp/test_repo")
        branch = "feature/test"

        mock_run_git.side_effect = [
            Mock(returncode=1, stderr="fetch failed"),  # git fetch (fails)
            Mock(returncode=1, stderr="checkout failed"),  # git checkout (fails)
            Mock(returncode=1, stderr="reset failed"),  # git reset --hard (fails)
        ]

        with patch("auto_slopp.utils.git_operations.logger"):
            result = checkout_branch_resilient(repo_dir, branch)

        assert result is False
        assert mock_run_git.call_count == 3

    @patch("auto_slopp.utils.git_operations._run_git_command")
    @patch("auto_slopp.utils.git_operations.run_cli_executor")
    def test_push_branch_failure(self, mock_run_cli_executor, mock_run_git):
        """Test push_branch failure calls _handle_git_operation_failure."""
        repo_dir = Path("/tmp/test_repo")
        branch = "feature/test"

        mock_run_git.return_value = Mock(returncode=1, stderr="push failed")

        with patch("auto_slopp.utils.git_operations.logger"):
            result = push_branch(repo_dir, branch)

        assert result is False
        mock_run_git.assert_called_once_with(repo_dir, "push", "origin", branch, "--force", check=False, timeout=60)
        mock_run_cli_executor.assert_called_once()


class TestGitOperationsOtherFunctions:
    """Tests for other git operations functions."""

    @patch("auto_slopp.utils.git_operations._run_git_command")
    def test_has_changes_true(self, mock_run_git):
        """Test has_changes returns True when there are changes."""
        mock_run_git.return_value = Mock(stdout=" M file.txt", returncode=0)
        result = has_changes(Path("/tmp/repo"))
        assert result is True

    @patch("auto_slopp.utils.git_operations._run_git_command")
    def test_has_changes_false(self, mock_run_git):
        """Test has_changes returns False when there are no changes."""
        mock_run_git.return_value = Mock(stdout="", returncode=0)
        result = has_changes(Path("/tmp/repo"))
        assert result is False

    @patch("auto_slopp.utils.git_operations._run_git_command")
    def test_get_current_branch(self, mock_run_git):
        """Test get_current_branch."""
        mock_run_git.return_value = Mock(stdout="feature-branch", returncode=0)
        result = get_current_branch(Path("/tmp/repo"))
        assert result == "feature-branch"

    @patch("auto_slopp.utils.git_operations._run_git_command")
    def test_get_local_branches(self, mock_run_git):
        """Test get_local_branches."""
        mock_run_git.return_value = Mock(
            stdout="* main\x002024-01-01T10:00:00+00:00\x00abc123\nfeature\x002024-01-01T10:00:00+00:00\x00def456\n",
            returncode=0,
        )
        result = get_local_branches(Path("/tmp/repo"))
        assert len(result) == 1
        assert result[0]["name"] == "feature"

    @patch("auto_slopp.utils.git_operations._run_git_command")
    def test_get_local_branches_exception(self, mock_run_git):
        """Test get_local_branches exception handling."""
        from auto_slopp.utils.git_operations import GitOperationError

        mock_run_git.side_effect = GitOperationError("Git command failed")
        with patch("auto_slopp.utils.git_operations.logger"):
            with pytest.raises(GitOperationError):
                get_local_branches(Path("/tmp/repo"))

    @patch("auto_slopp.utils.git_operations._run_git_command")
    def test_create_and_checkout_branch_exception(self, mock_run_git):
        """Test create_and_checkout_branch exception handling."""
        from auto_slopp.utils.git_operations import GitOperationError

        mock_run_git.side_effect = GitOperationError("Git command failed")
        with patch("auto_slopp.utils.git_operations.logger"):
            result = create_and_checkout_branch(Path("/tmp/repo"), "feature")
        assert result is False

    @patch("auto_slopp.utils.git_operations._run_git_command")
    def test_delete_branch_current(self, mock_run_git):
        """Test delete_branch returns False for current branch."""
        mock_run_git.return_value = Mock(stdout="main", returncode=0)
        result = delete_branch(Path("/tmp/repo"), "main")
        assert result is False

    @patch("auto_slopp.utils.git_operations._run_git_command")
    def test_delete_branch_success(self, mock_run_git):
        """Test delete_branch success."""
        mock_run_git.side_effect = [
            Mock(stdout="feature-branch", returncode=0),
            Mock(returncode=0),
        ]
        result = delete_branch(Path("/tmp/repo"), "old-branch")
        assert result is True

    @patch("auto_slopp.utils.git_operations._run_git_command")
    @patch("auto_slopp.utils.git_operations._handle_git_operation_failure")
    def test_delete_branch_failure(self, mock_handle, mock_run_git):
        """Test delete_branch failure calls _handle_git_operation_failure."""
        from auto_slopp.utils.git_operations import GitOperationError

        mock_run_git.side_effect = [
            Mock(stdout="feature-branch", returncode=0),
            GitOperationError("Delete failed"),
        ]
        result = delete_branch(Path("/tmp/repo"), "old-branch")
        assert result is False
        mock_handle.assert_called_once_with(
            "delete_branch",
            Path("/tmp/repo"),
            "Failed to delete branch 'old-branch': Delete failed",
        )

    @patch("auto_slopp.utils.git_operations._run_git_command")
    def test_is_bare_repository_true(self, mock_run_git):
        """Test is_bare_repository returns True for bare repo."""
        mock_run_git.return_value = Mock(stdout="true", returncode=0)
        result = is_bare_repository(Path("/tmp/bare"))
        assert result is True

    @patch("auto_slopp.utils.git_operations._run_git_command")
    def test_is_bare_repository_false(self, mock_run_git):
        """Test is_bare_repository returns False for non-bare repo."""
        mock_run_git.return_value = Mock(stdout="false", returncode=0)
        result = is_bare_repository(Path("/tmp/repo"))
        assert result is False

    @patch("auto_slopp.utils.git_operations._run_git_command")
    def test_get_remotes(self, mock_run_git):
        """Test get_remotes."""
        mock_run_git.return_value = Mock(
            stdout="origin\thttps://github.com/test/repo.git (fetch)\norigin\thttps://github.com/test/repo.git (push)",
            returncode=0,
        )
        result = get_remotes(Path("/tmp/repo"))
        assert len(result) == 2  # fetch and push entries
        assert result[0]["name"] == "origin"
        assert result[0]["url"] == "https://github.com/test/repo.git"

    @patch("auto_slopp.utils.git_operations._run_git_command")
    def test_get_remotes_exception(self, mock_run_git):
        """Test get_remotes exception handling."""
        from auto_slopp.utils.git_operations import GitOperationError

        mock_run_git.side_effect = GitOperationError("Git command failed")
        with patch("auto_slopp.utils.git_operations.logger"):
            with pytest.raises(GitOperationError):
                get_remotes(Path("/tmp/repo"))

    @patch("auto_slopp.utils.git_operations._run_git_command")
    def test_get_remote_branches_exception(self, mock_run_git):
        """Test get_remote_branches exception handling."""
        from auto_slopp.utils.git_operations import GitOperationError

        mock_run_git.side_effect = GitOperationError("Git command failed")
        with patch("auto_slopp.utils.git_operations.logger"):
            with pytest.raises(GitOperationError):
                get_remote_branches(Path("/tmp/repo"))

    @patch("auto_slopp.utils.git_operations._run_git_command")
    def test_get_default_branch_main(self, mock_run_git):
        """Test get_default_branch returns main."""
        mock_run_git.side_effect = [
            Mock(stdout="main", returncode=0),
        ]
        result = get_default_branch(Path("/tmp/repo"))
        assert result == "main"

    @patch("auto_slopp.utils.git_operations._run_git_command")
    def test_get_default_branch_master(self, mock_run_git):
        """Test get_default_branch returns master."""
        mock_run_git.side_effect = [
            Mock(returncode=128, stderr="ref not found"),
            Mock(returncode=0),
        ]
        result = get_default_branch(Path("/tmp/repo"))
        assert result == "main"

    @patch("auto_slopp.utils.git_operations._run_git_command")
    def test_branch_exists_true(self, mock_run_git):
        """Test branch_exists returns True."""
        mock_run_git.return_value = Mock(returncode=0)
        result = branch_exists(Path("/tmp/repo"), "feature")
        assert result is True

    @patch("auto_slopp.utils.git_operations._run_git_command")
    def test_branch_exists_false(self, mock_run_git):
        """Test branch_exists returns False."""
        mock_run_git.return_value = Mock(returncode=128)
        result = branch_exists(Path("/tmp/repo"), "nonexistent")
        assert result is False

    @patch("auto_slopp.utils.git_operations._run_git_command")
    def test_get_ahead_behind(self, mock_run_git):
        """Test get_ahead_behind."""
        mock_run_git.return_value = Mock(stdout="1\t2", returncode=0)
        ahead, behind = get_ahead_behind(Path("/tmp/repo"))
        assert ahead == 1
        assert behind == 2

    @patch("auto_slopp.utils.git_operations.subprocess.run")
    def test_is_git_repo_true(self, mock_run):
        """Test is_git_repo returns True for git repo."""
        mock_run.return_value = Mock(returncode=0)
        result = is_git_repo(Path("/tmp/repo"))
        assert result is True

    @patch("auto_slopp.utils.git_operations.subprocess.run")
    def test_is_git_repo_false(self, mock_run):
        """Test is_git_repo returns False for non-git repo."""
        mock_run.return_value = Mock(returncode=128)
        result = is_git_repo(Path("/tmp/non-repo"))
        assert result is False

    @patch("auto_slopp.utils.git_operations._run_git_command")
    def test_pull_from_remote_success(self, mock_run_git):
        """Test pull_from_remote success."""
        mock_run_git.return_value = Mock(returncode=0, stdout="Updating", stderr="")
        success, _ = pull_from_remote(Path("/tmp/repo"))
        assert success is True

    @patch("auto_slopp.utils.git_operations._run_git_command")
    def test_pull_from_remote_failure(self, mock_run_git):
        """Test pull_from_remote failure."""
        mock_run_git.return_value = Mock(returncode=1, stderr="Merge failed")
        success, _ = pull_from_remote(Path("/tmp/repo"))
        assert success is False

    @patch("auto_slopp.utils.git_operations._run_git_command")
    @patch("auto_slopp.utils.git_operations.run_cli_executor")
    def test_checkout_failure_after_reset(self, mock_run_cli_executor, mock_run_git):
        """Test checkout failure even after reset."""
        repo_dir = Path("/tmp/test_repo")
        branch = "feature/test"

        mock_run_cli_executor.return_value = {
            "success": False,
            "error": "CLI executor failed",
        }

        mock_run_git.side_effect = [
            Mock(returncode=0, stderr=""),  # git fetch
            Mock(returncode=1, stderr="checkout failed"),  # git checkout (fails)
            Mock(returncode=0, stderr=""),  # git reset --hard
            Mock(returncode=0, stderr=""),  # git clean
            Mock(returncode=1, stderr="checkout still failed"),  # git checkout (fails again)
        ]

        result = checkout_branch_resilient(repo_dir, branch)

        assert result is False
        assert mock_run_git.call_count == 5

    @patch("auto_slopp.utils.git_operations._run_git_command")
    @patch("auto_slopp.utils.git_operations.run_cli_executor")
    def test_checkout_reset_failure(self, mock_run_cli_executor, mock_run_git):
        """Test checkout failure when reset itself fails."""
        repo_dir = Path("/tmp/test_repo")
        branch = "feature/test"

        mock_run_cli_executor.return_value = {
            "success": False,
            "error": "CLI executor failed",
        }

        mock_run_git.side_effect = [
            Mock(returncode=0, stderr=""),  # git fetch
            Mock(returncode=1, stderr="checkout failed"),  # git checkout (fails)
            Mock(returncode=1, stderr="reset failed"),  # git reset --hard (fails)
        ]

        result = checkout_branch_resilient(repo_dir, branch)

        assert result is False
        assert mock_run_git.call_count == 3

    @patch("auto_slopp.utils.git_operations._run_git_command")
    def test_checkout_timeout(self, mock_run_git):
        """Test checkout timeout handling."""
        from auto_slopp.utils.git_operations import GitOperationError

        repo_dir = Path("/tmp/test_repo")
        branch = "feature/test"

        mock_run_git.side_effect = GitOperationError("Git command timed out: timeout")

        result = checkout_branch_resilient(repo_dir, branch)

        assert result is False

    @patch("auto_slopp.utils.git_operations._run_git_command")
    def test_checkout_without_fetch(self, mock_run_git):
        """Test checkout without fetching first."""
        repo_dir = Path("/tmp/test_repo")
        branch = "feature/test"

        mock_run_git.side_effect = [
            Mock(returncode=0, stdout=""),  # git checkout
            Mock(returncode=0, stderr=""),  # git pull
        ]

        result = checkout_branch_resilient(repo_dir, branch, fetch_first=False)

        assert result is True
        assert mock_run_git.call_count == 2

    @patch("auto_slopp.utils.git_operations._run_git_command")
    def test_checkout_with_pull_failure(self, mock_run_git):
        """Test checkout success even when pull fails."""
        repo_dir = Path("/tmp/test_repo")
        branch = "feature/test"

        mock_run_git.side_effect = [
            Mock(returncode=0, stderr=""),  # git fetch
            Mock(returncode=0, stdout=""),  # git checkout
            Mock(returncode=1, stderr="pull failed"),  # git pull (fails but shouldn't affect checkout)
        ]

        result = checkout_branch_resilient(repo_dir, branch)

        assert result is True
        assert mock_run_git.call_count == 3

    @patch("auto_slopp.utils.git_operations._run_git_command")
    def test_checkout_with_clean_failure(self, mock_run_git):
        """Test checkout success even when git clean fails."""
        repo_dir = Path("/tmp/test_repo")
        branch = "feature/test"

        mock_run_git.side_effect = [
            Mock(returncode=0, stderr=""),  # git fetch
            Mock(returncode=1, stderr="checkout failed"),  # git checkout (fails)
            Mock(returncode=0, stderr=""),  # git reset --hard
            Mock(returncode=1, stderr="clean failed"),  # git clean (fails but shouldn't stop retry)
            Mock(returncode=0, stdout=""),  # git checkout (succeeds)
            Mock(returncode=0, stderr=""),  # git pull
        ]

        result = checkout_branch_resilient(repo_dir, branch)

        assert result is True
        assert mock_run_git.call_count == 6


class TestSanitizeBranchName:
    """Tests for sanitize_branch_name function."""

    def test_sanitize_branch_name_basic(self):
        """Test basic sanitization."""
        result = sanitize_branch_name("feature-branch")
        assert result == "feature-branch"

    def test_sanitize_branch_name_with_spaces(self):
        """Test sanitization removes spaces."""
        result = sanitize_branch_name("feature branch")
        assert result == "feature-branch"

    def test_sanitize_branch_name_special_chars(self):
        """Test sanitization removes special characters."""
        result = sanitize_branch_name("feature@#$%branch")
        assert result == "feature-branch"

    def test_sanitize_branch_name_multiple_dashes(self):
        """Test sanitization collapses multiple dashes."""
        result = sanitize_branch_name("feature---branch")
        assert result == "feature-branch"

    def test_sanitize_branch_name_strips_dashes(self):
        """Test sanitization strips leading/trailing dashes."""
        result = sanitize_branch_name("-feature-branch-")
        assert result == "feature-branch"

    def test_sanitize_branch_name_max_length(self):
        """Test sanitization truncates to max length."""
        result = sanitize_branch_name("a" * 100, max_length=50)
        assert len(result) == 50

    def test_sanitize_branch_name_empty(self):
        """Test sanitization returns 'branch' for empty string."""
        result = sanitize_branch_name("")
        assert result == "branch"

    def test_sanitize_branch_name_only_special_chars(self):
        """Test sanitization returns 'branch' for string with only special chars."""
        result = sanitize_branch_name("@#$%")
        assert result == "branch"


class TestRunGitCommandTimeout:
    """Tests for _run_git_command timeout handling."""

    @patch("auto_slopp.utils.git_operations.subprocess.run")
    def test_git_command_timeout(self, mock_run):
        """Test git command timeout raises GitOperationError."""
        import subprocess

        from auto_slopp.utils.git_operations import GitOperationError, _run_git_command

        mock_run.side_effect = subprocess.TimeoutExpired("git", 60)

        with patch("auto_slopp.utils.git_operations.logger"):
            with pytest.raises(GitOperationError) as exc_info:
                _run_git_command(Path("/tmp/repo"), "status")

        assert "timed out" in str(exc_info.value).lower()

    @patch("auto_slopp.utils.git_operations.subprocess.run")
    def test_git_command_called_process_error(self, mock_run):
        """Test git command raises GitOperationError on failure."""
        import subprocess

        from auto_slopp.utils.git_operations import GitOperationError, _run_git_command

        mock_run.side_effect = subprocess.CalledProcessError(1, "git", stderr="error")

        with patch("auto_slopp.utils.git_operations.logger"):
            with pytest.raises(GitOperationError):
                _run_git_command(Path("/tmp/repo"), "status")


class TestGitOperationsAdditional:
    """Additional tests for uncovered code paths."""

    @patch("auto_slopp.utils.git_operations._run_git_command")
    def test_create_and_checkout_branch_exception(self, mock_run_git):
        """Test create_and_checkout_branch handles exception (lines 397-399)."""
        from auto_slopp.utils.git_operations import (
            GitOperationError,
            create_and_checkout_branch,
        )

        repo_dir = Path("/tmp/test_repo")
        mock_run_git.side_effect = GitOperationError("Git error")

        with patch("auto_slopp.utils.git_operations.logger"):
            with patch("auto_slopp.utils.git_operations.branch_exists", return_value=True):
                result = create_and_checkout_branch(repo_dir, "feature/test")

                assert result is False

    @patch("auto_slopp.utils.git_operations._run_git_command")
    @patch("auto_slopp.utils.git_operations.logger")
    def test_push_branch_failure(self, mock_logger, mock_run_git):
        """Test push_branch handles failure (lines 430-431)."""
        from auto_slopp.utils.git_operations import push_branch

        repo_dir = Path("/tmp/test_repo")
        mock_run_git.return_value = Mock(returncode=1, stderr="push failed", stdout="")

        result = push_branch(repo_dir, "feature/test", force=True)

        assert result is False
        mock_logger.error.assert_called()

    @patch("auto_slopp.utils.git_operations._run_git_command")
    @patch("auto_slopp.utils.git_operations.logger")
    def test_push_branch_no_force(self, mock_logger, mock_run_git):
        """Test push_branch without force push (line 418-421)."""
        from auto_slopp.utils.git_operations import push_branch

        repo_dir = Path("/tmp/test_repo")
        mock_run_git.return_value = Mock(returncode=0)

        result = push_branch(repo_dir, "feature/test", force=False)

        assert result is True
        args = mock_run_git.call_args[0]
        assert "--force" not in args

    @patch("auto_slopp.utils.git_operations._run_git_command")
    @patch("auto_slopp.utils.git_operations.logger")
    def test_merge_main_into_branch_merge_conflict(self, mock_logger, mock_run_git):
        """Test merge_main_into_branch handles merge conflict (lines 500-505)."""
        from auto_slopp.utils.git_operations import merge_main_into_branch

        repo_dir = Path("/tmp/test_repo")
        mock_run_git.side_effect = [
            Mock(returncode=0),  # git fetch origin main:main
            Mock(returncode=1, stderr="CONFLICT", stdout="CONFLICT"),  # merge conflict
            Mock(returncode=0),  # merge --abort succeeds
        ]

        with patch("auto_slopp.utils.git_operations.get_current_branch", return_value="feature"):
            with patch(
                "auto_slopp.utils.git_operations.get_active_cli_command",
                return_value="auto-slopp",
            ):
                result = merge_main_into_branch(repo_dir, "feature")

                assert result[0] is False
                assert "CONFLICT" in result[1]

    @patch("auto_slopp.utils.git_operations._run_git_command")
    @patch("auto_slopp.utils.git_operations.logger")
    def test_merge_main_into_branch_abort_fails(self, mock_logger, mock_run_git):
        """Test merge_main_into_branch handles abort failure (lines 500-505)."""
        from auto_slopp.utils.git_operations import merge_main_into_branch

        repo_dir = Path("/tmp/test_repo")
        mock_run_git.side_effect = [
            Mock(returncode=0),  # git fetch origin main:main
            Mock(returncode=1, stderr="CONFLICT", stdout="CONFLICT"),  # merge conflict
            Mock(returncode=1, stderr="abort failed", stdout=""),  # merge --abort fails
        ]

        with patch("auto_slopp.utils.git_operations.get_current_branch", return_value="feature"):
            with patch(
                "auto_slopp.utils.git_operations.get_active_cli_command",
                return_value="auto-slopp",
            ):
                result = merge_main_into_branch(repo_dir, "feature")

                assert result[0] is False

    @patch("auto_slopp.utils.git_operations._run_git_command")
    @patch("auto_slopp.utils.git_operations.logger")
    def test_merge_main_into_branch_exception(self, mock_logger, mock_run_git):
        """Test merge_main_into_branch handles GitOperationError (lines 510-514)."""
        from auto_slopp.utils.git_operations import (
            GitOperationError,
            merge_main_into_branch,
        )

        repo_dir = Path("/tmp/test_repo")
        mock_run_git.side_effect = GitOperationError("Git error")

        with patch("auto_slopp.utils.git_operations.get_current_branch", return_value="feature"):
            result = merge_main_into_branch(repo_dir, "feature")

            assert result[0] is False
            assert "Git error" in result[1]

    def test_get_remotes_failure(self):
        """Test get_remotes handles failure (line 542)."""
        from auto_slopp.utils.git_operations import get_remotes

        repo_dir = Path("/tmp/test_repo")

        with patch("auto_slopp.utils.git_operations._run_git_command") as mock_run_git:
            mock_run_git.return_value = Mock(returncode=1, stderr="error", stdout="")

            result = get_remotes(repo_dir)

            assert result == []

    def test_get_default_branch_returns_none(self):
        """Test get_default_branch returns None when no branch found (line 575)."""
        from auto_slopp.utils.git_operations import get_default_branch

        repo_dir = Path("/tmp/test_repo")

        with patch("auto_slopp.utils.git_operations._run_git_command") as mock_run_git:
            mock_run_git.side_effect = [
                Mock(returncode=1, stderr="", stdout=""),  # git config --get init.defaultBranch
                Mock(returncode=1, stderr="", stdout=""),  # git rev-parse --verify main
                Mock(returncode=1, stderr="", stdout=""),  # git rev-parse --verify master
                Mock(returncode=1, stderr="", stdout=""),  # git rev-parse --verify develop
            ]

            result = get_default_branch(repo_dir)

            assert result is None

    @patch("auto_slopp.utils.git_operations._run_git_command")
    def test_get_ahead_behind_exception(self, mock_run_git):
        """Test get_ahead_behind handles exception (lines 621-624)."""
        repo_dir = Path("/tmp/test_repo")
        mock_run_git.side_effect = Exception("Unexpected error")

        ahead, behind = get_ahead_behind(repo_dir, "origin", "feature")

        assert ahead == 0
        assert behind == 0

    def test_push_to_remote(self):
        """Test push_to_remote function (lines 658-667)."""
        from auto_slopp.utils.git_operations import push_to_remote

        repo_dir = Path("/tmp/test_repo")

        with patch("auto_slopp.utils.git_operations._run_git_command") as mock_run_git:
            mock_run_git.return_value = Mock(returncode=0)

            with patch(
                "auto_slopp.utils.git_operations.get_current_branch",
                return_value="feature",
            ):
                result = push_to_remote(repo_dir, "origin", "feature")

                assert result == (True, "Push successful")

    def test_push_to_remote_failure(self):
        """Test push_to_remote handles failure (lines 663-667)."""
        from auto_slopp.utils.git_operations import push_to_remote

        repo_dir = Path("/tmp/test_repo")

        with patch("auto_slopp.utils.git_operations._run_git_command") as mock_run_git:
            mock_run_git.return_value = Mock(returncode=1, stderr="push failed", stdout="")

            with patch(
                "auto_slopp.utils.git_operations.get_current_branch",
                return_value="feature",
            ):
                result = push_to_remote(repo_dir, "origin", "feature")

                assert result == (False, "push failed")

    @patch("auto_slopp.utils.git_operations.subprocess.run")
    def test_is_git_repo_exception(self, mock_run):
        """Test is_git_repo handles exception (lines 690-691)."""
        from auto_slopp.utils.git_operations import is_git_repo

        repo_dir = Path("/tmp/test_repo")
        mock_run.side_effect = Exception("Unexpected error")

        result = is_git_repo(repo_dir)

        assert result is False

    def test_commit_all_changes_not_git_repo(self):
        """Test commit_all_changes when directory is not a git repo (lines 764-765)."""
        from auto_slopp.utils.git_operations import commit_all_changes

        repo_dir = Path("/tmp/test_repo")

        with patch("auto_slopp.utils.git_operations.is_git_repo", return_value=False):
            result = commit_all_changes(repo_dir, "Test commit")

            assert result == (False, f"Directory is not a git repository: {repo_dir}")

    def test_commit_all_changes_no_changes(self):
        """Test commit_all_changes when there are no changes (lines 767-768)."""
        from auto_slopp.utils.git_operations import commit_all_changes

        repo_dir = Path("/tmp/test_repo")

        with patch("auto_slopp.utils.git_operations.is_git_repo", return_value=True):
            with patch("auto_slopp.utils.git_operations.has_changes", return_value=False):
                result = commit_all_changes(repo_dir, "Test commit")

                assert result == (True, "No changes to commit")

    @patch("auto_slopp.utils.git_operations._run_git_command")
    def test_commit_all_changes_exception(self, mock_run_git):
        """Test commit_all_changes handles exception (lines 774-776)."""
        from auto_slopp.utils.git_operations import (
            GitOperationError,
            commit_all_changes,
        )

        repo_dir = Path("/tmp/test_repo")

        with patch("auto_slopp.utils.git_operations.is_git_repo", return_value=True):
            with patch("auto_slopp.utils.git_operations.has_changes", return_value=True):
                mock_run_git.side_effect = [
                    Mock(returncode=0),  # git add .
                    GitOperationError("Commit failed"),  # git commit fails
                ]

                result = commit_all_changes(repo_dir, "Test commit")

                assert result[0] is False
                assert "Commit failed" in result[1]
