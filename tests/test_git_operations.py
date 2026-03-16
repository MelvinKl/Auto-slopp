"""Tests for git operations utilities."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from auto_slopp.utils.git_operations import (
    GitOperationError,
    checkout_branch_resilient,
    get_current_branch,
    get_local_branches,
    get_remote_branches,
    merge_main_into_branch,
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

    @patch("auto_slopp.utils.git_operations.subprocess.run")
    def test_checkout_success_first_attempt(self, mock_subprocess_run):
        """Test successful checkout on first attempt."""
        repo_dir = Path("/tmp/test_repo")
        branch = "feature/test"

        # Mock successful git commands
        mock_subprocess_run.side_effect = [
            Mock(returncode=0, stderr=""),  # git fetch
            Mock(returncode=0, stderr=""),  # git checkout
            Mock(returncode=0, stderr=""),  # git pull
        ]

        result = checkout_branch_resilient(repo_dir, branch)

        assert result is True
        assert mock_subprocess_run.call_count == 3

    @patch("auto_slopp.utils.git_operations.subprocess.run")
    def test_checkout_success_after_reset(self, mock_subprocess_run):
        """Test successful checkout after reset on first failure."""
        repo_dir = Path("/tmp/test_repo")
        branch = "feature/test"

        # Mock git commands: first checkout fails, then reset works, retry checkout succeeds
        mock_subprocess_run.side_effect = [
            Mock(returncode=0, stderr=""),  # git fetch
            Mock(returncode=1, stderr="checkout failed"),  # git checkout (fails)
            Mock(returncode=0, stderr=""),  # git reset --hard
            Mock(returncode=0, stderr=""),  # git clean
            Mock(returncode=0, stderr=""),  # git checkout (succeeds)
            Mock(returncode=0, stderr=""),  # git pull
        ]

        result = checkout_branch_resilient(repo_dir, branch)

        assert result is True
        assert mock_subprocess_run.call_count == 6

    @patch("auto_slopp.utils.git_operations.subprocess.run")
    def test_checkout_retries_after_safe_directory_fix(self, mock_subprocess_run):
        """Test checkout retry after git safe.directory is configured."""
        repo_dir = Path("/tmp/test_repo")
        branch = "feature/test"
        dubious_error = (
            "fatal: detected dubious ownership in repository at '/tmp/test_repo'\n"
            "To add an exception for this directory, call:\n\n"
            "\tgit config --global --add safe.directory /tmp/test_repo"
        )

        mock_subprocess_run.side_effect = [
            Mock(returncode=1, stderr=dubious_error),  # git fetch
            Mock(returncode=0, stderr=""),  # git config --global --add safe.directory
            Mock(returncode=0, stderr=""),  # git fetch retry
            Mock(returncode=0, stderr=""),  # git checkout
            Mock(returncode=0, stderr=""),  # git pull
        ]

        result = checkout_branch_resilient(repo_dir, branch)

        assert result is True
        assert mock_subprocess_run.call_count == 5
        safe_directory_call = mock_subprocess_run.call_args_list[1]
        assert safe_directory_call.args[0] == [
            "git",
            "config",
            "--global",
            "--add",
            "safe.directory",
            str(repo_dir.resolve()),
        ]

    @patch("auto_slopp.utils.git_operations.subprocess.run")
    @patch("auto_slopp.utils.git_operations.run_cli_executor")
    def test_checkout_dubious_ownership_does_not_reset(self, mock_run_cli_executor, mock_subprocess_run):
        """Test dubious ownership failures do not trigger git reset --hard."""
        repo_dir = Path("/tmp/test_repo")
        branch = "feature/test"
        dubious_error = (
            "fatal: detected dubious ownership in repository at '/tmp/test_repo'\n"
            "To add an exception for this directory, call:\n\n"
            "\tgit config --global --add safe.directory /tmp/test_repo"
        )

        mock_run_cli_executor.return_value = {
            "success": False,
            "error": "CLI executor failed",
        }
        mock_subprocess_run.side_effect = [
            Mock(returncode=0, stderr=""),  # git fetch
            Mock(returncode=1, stderr=dubious_error),  # git checkout
            Mock(returncode=1, stderr="permission denied"),  # git config --global --add safe.directory
        ]

        result = checkout_branch_resilient(repo_dir, branch)

        assert result is False
        assert mock_subprocess_run.call_count == 3
        issued_commands = [call.args[0] for call in mock_subprocess_run.call_args_list]
        assert ["git", "reset", "--hard"] not in issued_commands

    @patch("auto_slopp.utils.git_operations.subprocess.run")
    @patch("auto_slopp.utils.git_operations.run_cli_executor")
    def test_checkout_failure_after_reset(self, mock_run_cli_executor, mock_subprocess_run):
        """Test checkout failure even after reset."""
        repo_dir = Path("/tmp/test_repo")
        branch = "feature/test"

        # Mock run_cli_executor to avoid actual execution
        mock_run_cli_executor.return_value = {
            "success": False,
            "error": "CLI executor failed",
        }

        # Mock git commands: both checkout attempts fail
        mock_subprocess_run.side_effect = [
            Mock(returncode=0, stderr=""),  # git fetch
            Mock(returncode=1, stderr="checkout failed"),  # git checkout (fails)
            Mock(returncode=0, stderr=""),  # git reset --hard
            Mock(returncode=0, stderr=""),  # git clean
            Mock(returncode=1, stderr="checkout still failed"),  # git checkout (fails again)
        ]

        result = checkout_branch_resilient(repo_dir, branch)

        assert result is False
        assert mock_subprocess_run.call_count == 5

    @patch("auto_slopp.utils.git_operations.subprocess.run")
    @patch("auto_slopp.utils.git_operations.run_cli_executor")
    def test_checkout_reset_failure(self, mock_run_cli_executor, mock_subprocess_run):
        """Test checkout failure when reset itself fails."""
        repo_dir = Path("/tmp/test_repo")
        branch = "feature/test"

        # Mock run_cli_executor to avoid actual execution
        mock_run_cli_executor.return_value = {
            "success": False,
            "error": "CLI executor failed",
        }

        # Mock git commands: checkout fails, reset also fails
        mock_subprocess_run.side_effect = [
            Mock(returncode=0, stderr=""),  # git fetch
            Mock(returncode=1, stderr="checkout failed"),  # git checkout (fails)
            Mock(returncode=1, stderr="reset failed"),  # git reset --hard (fails)
        ]

        result = checkout_branch_resilient(repo_dir, branch)

        assert result is False
        assert mock_subprocess_run.call_count == 3

    @patch("auto_slopp.utils.git_operations.subprocess.run")
    def test_checkout_timeout(self, mock_subprocess_run):
        """Test checkout timeout handling."""
        repo_dir = Path("/tmp/test_repo")
        branch = "feature/test"

        # Mock timeout on fetch
        mock_subprocess_run.side_effect = TimeoutError("timeout")

        result = checkout_branch_resilient(repo_dir, branch)

        assert result is False

    @patch("auto_slopp.utils.git_operations.subprocess.run")
    def test_checkout_without_fetch(self, mock_subprocess_run):
        """Test checkout without fetching first."""
        repo_dir = Path("/tmp/test_repo")
        branch = "feature/test"

        # Mock successful git commands (no fetch)
        mock_subprocess_run.side_effect = [
            Mock(returncode=0, stderr=""),  # git checkout
            Mock(returncode=0, stderr=""),  # git pull
        ]

        result = checkout_branch_resilient(repo_dir, branch, fetch_first=False)

        assert result is True
        assert mock_subprocess_run.call_count == 2

    @patch("auto_slopp.utils.git_operations.subprocess.run")
    def test_checkout_with_pull_failure(self, mock_subprocess_run):
        """Test checkout success even when pull fails."""
        repo_dir = Path("/tmp/test_repo")
        branch = "feature/test"

        # Mock git commands: checkout succeeds but pull fails
        mock_subprocess_run.side_effect = [
            Mock(returncode=0, stderr=""),  # git fetch
            Mock(returncode=0, stderr=""),  # git checkout
            Mock(returncode=1, stderr="pull failed"),  # git pull (fails but shouldn't affect checkout)
        ]

        result = checkout_branch_resilient(repo_dir, branch)

        assert result is True
        assert mock_subprocess_run.call_count == 3

    @patch("auto_slopp.utils.git_operations.subprocess.run")
    def test_checkout_with_clean_failure(self, mock_subprocess_run):
        """Test checkout success even when git clean fails."""
        repo_dir = Path("/tmp/test_repo")
        branch = "feature/test"

        # Mock git commands: first checkout fails, reset works, clean fails, retry checkout succeeds
        mock_subprocess_run.side_effect = [
            Mock(returncode=0, stderr=""),  # git fetch
            Mock(returncode=1, stderr="checkout failed"),  # git checkout (fails)
            Mock(returncode=0, stderr=""),  # git reset --hard
            Mock(returncode=1, stderr="clean failed"),  # git clean (fails but shouldn't stop retry)
            Mock(returncode=0, stderr=""),  # git checkout (succeeds)
            Mock(returncode=0, stderr=""),  # git pull
        ]

        result = checkout_branch_resilient(repo_dir, branch)

        assert result is True
        assert mock_subprocess_run.call_count == 6
