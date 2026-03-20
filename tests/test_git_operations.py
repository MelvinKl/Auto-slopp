"""Tests for git operations utilities."""

from pathlib import Path
from unittest.mock import Mock, patch

from auto_slopp.utils.git_operations import (
    branch_exists,
    checkout_branch_resilient,
    delete_branch,
    get_ahead_behind,
    get_current_branch,
    get_default_branch,
    get_local_branches,
    get_remotes,
    has_changes,
    is_bare_repository,
    is_git_repo,
    merge_main_into_branch,
    pull_from_remote,
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
    def test_delete_branch_failure(self, mock_run_git):
        """Test delete_branch failure."""
        from auto_slopp.utils.git_operations import GitOperationError

        mock_run_git.side_effect = [
            Mock(stdout="feature-branch", returncode=0),
            GitOperationError("Delete failed"),
        ]
        result = delete_branch(Path("/tmp/repo"), "old-branch")
        assert result is False

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
