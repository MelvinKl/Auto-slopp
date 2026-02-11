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
)


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
    def test_checkout_failure_after_reset(self, mock_subprocess_run):
        """Test checkout failure even after reset."""
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

    @patch("auto_slopp.utils.git_operations.subprocess.run")
    def test_checkout_reset_failure(self, mock_subprocess_run):
        """Test checkout failure when reset itself fails."""
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
