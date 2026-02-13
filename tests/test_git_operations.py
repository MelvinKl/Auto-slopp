"""Tests for git operations utilities."""

import subprocess
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
    has_remote,
)


class TestHasRemote:
    """Test cases for has_remote function."""

    @patch("auto_slopp.utils.git_operations.subprocess.run")
    def test_has_remote_true(self, mock_subprocess_run):
        """Test that has_remote returns True when remote exists."""
        repo_dir = Path("/tmp/test_repo")
        mock_subprocess_run.return_value = Mock(returncode=0, stdout="https://github.com/user/repo.git")

        result = has_remote(repo_dir, "origin")

        assert result is True
        mock_subprocess_run.assert_called_once()

    @patch("auto_slopp.utils.git_operations.subprocess.run")
    def test_has_remote_false(self, mock_subprocess_run):
        """Test that has_remote returns False when remote does not exist."""
        repo_dir = Path("/tmp/test_repo")
        mock_subprocess_run.side_effect = subprocess.CalledProcessError(1, "git")

        result = has_remote(repo_dir, "origin")

        assert result is False

    @patch("auto_slopp.utils.git_operations.subprocess.run")
    def test_has_remote_custom_name(self, mock_subprocess_run):
        """Test has_remote with custom remote name."""
        repo_dir = Path("/tmp/test_repo")
        mock_subprocess_run.return_value = Mock(returncode=0, stdout="https://github.com/user/repo.git")

        result = has_remote(repo_dir, "upstream")

        assert result is True
        mock_subprocess_run.assert_called_once()


class TestCheckoutBranchResilient:
    """Test cases for checkout_branch_resilient function."""

    @patch("auto_slopp.utils.git_operations.has_remote")
    @patch("auto_slopp.utils.git_operations.subprocess.run")
    def test_checkout_success_first_attempt(self, mock_subprocess_run, mock_has_remote):
        """Test successful checkout on first attempt."""
        mock_has_remote.return_value = True
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

    @patch("auto_slopp.utils.git_operations.has_remote")
    @patch("auto_slopp.utils.git_operations.subprocess.run")
    def test_checkout_without_remote(self, mock_subprocess_run, mock_has_remote):
        """Test checkout succeeds without remote (no fetch/pull)."""
        mock_has_remote.return_value = False
        repo_dir = Path("/tmp/test_repo")
        branch = "feature/test"

        mock_subprocess_run.return_value = Mock(returncode=0, stderr="")

        result = checkout_branch_resilient(repo_dir, branch)

        assert result is True
        assert mock_subprocess_run.call_count == 1

    @patch("auto_slopp.utils.git_operations.has_remote")
    @patch("auto_slopp.utils.git_operations.subprocess.run")
    @patch("auto_slopp.utils.git_operations.run_opencode")
    def test_checkout_failure_after_reset(self, mock_run_opencode, mock_subprocess_run, mock_has_remote):
        """Test checkout failure even after reset."""
        mock_has_remote.return_value = True
        mock_run_opencode.return_value = {"success": False, "error": "OpenCode failed"}
        repo_dir = Path("/tmp/test_repo")
        branch = "feature/test"

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

    @patch("auto_slopp.utils.git_operations.has_remote")
    @patch("auto_slopp.utils.git_operations.subprocess.run")
    @patch("auto_slopp.utils.git_operations.run_opencode")
    def test_checkout_reset_failure(self, mock_run_opencode, mock_subprocess_run, mock_has_remote):
        """Test checkout failure when reset itself fails."""
        mock_has_remote.return_value = True
        mock_run_opencode.return_value = {"success": False, "error": "OpenCode failed"}
        repo_dir = Path("/tmp/test_repo")
        branch = "feature/test"

        # Mock git commands: checkout fails, reset also fails
        mock_subprocess_run.side_effect = [
            Mock(returncode=0, stderr=""),  # git fetch
            Mock(returncode=1, stderr="checkout failed"),  # git checkout (fails)
            Mock(returncode=1, stderr="reset failed"),  # git reset --hard (fails)
        ]

        result = checkout_branch_resilient(repo_dir, branch)

        assert result is False
        assert mock_subprocess_run.call_count == 3

    @patch("auto_slopp.utils.git_operations.has_remote")
    @patch("auto_slopp.utils.git_operations.subprocess.run")
    def test_checkout_timeout(self, mock_subprocess_run, mock_has_remote):
        """Test checkout timeout handling."""
        mock_has_remote.return_value = True
        repo_dir = Path("/tmp/test_repo")
        branch = "feature/test"

        # Mock timeout on fetch
        mock_subprocess_run.side_effect = TimeoutError("timeout")

        result = checkout_branch_resilient(repo_dir, branch)

        assert result is False

    @patch("auto_slopp.utils.git_operations.has_remote")
    @patch("auto_slopp.utils.git_operations.subprocess.run")
    def test_checkout_without_fetch(self, mock_subprocess_run, mock_has_remote):
        """Test checkout without fetching first."""
        mock_has_remote.return_value = True
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

    @patch("auto_slopp.utils.git_operations.has_remote")
    @patch("auto_slopp.utils.git_operations.subprocess.run")
    def test_checkout_with_pull_failure(self, mock_subprocess_run, mock_has_remote):
        """Test checkout success even when pull fails."""
        mock_has_remote.return_value = True
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

    @patch("auto_slopp.utils.git_operations.has_remote")
    @patch("auto_slopp.utils.git_operations.subprocess.run")
    def test_checkout_with_clean_failure(self, mock_subprocess_run, mock_has_remote):
        """Test checkout success even when git clean fails."""
        mock_has_remote.return_value = True
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
