"""More extended tests for git operations utilities."""

from pathlib import Path
from unittest.mock import Mock, patch

from auto_slopp.utils.git_operations import (
    GitOperationError,
    checkout_branch_resilient,
    merge_main_into_branch,
    push_to_remote,
)


class TestPushBranch:
    """Test cases for push_to_remote function."""

    @patch("auto_slopp.utils.git_operations.get_current_branch")
    @patch("auto_slopp.utils.git_operations._run_git_command")
    def test_push_to_remote_default(self, mock_run_git, mock_get_branch):
        """Test pushing branch without specifying branch name."""
        repo_dir = Path("/tmp/test_repo")
        mock_get_branch.return_value = "feature/test"
        mock_run_git.return_value = Mock(returncode=0)

        success, message = push_to_remote(repo_dir)

        assert success is True
        assert message == "Push successful"
        mock_run_git.assert_called_once_with(repo_dir, "push", "origin", "feature/test", check=False)

    @patch("auto_slopp.utils.git_operations._run_git_command")
    def test_push_to_remote_failure(self, mock_run_git):
        """Test failing to push branch."""
        repo_dir = Path("/tmp/test_repo")
        mock_run_git.return_value = Mock(returncode=1, stderr="fatal: remote error", stdout="")

        success, message = push_to_remote(repo_dir, branch="main")

        assert success is False
        assert message == "fatal: remote error"


class TestMergeMainIntoBranchEdgeCases:
    """Edge case tests for merge_main_into_branch function."""

    @patch("auto_slopp.utils.git_operations.get_current_branch")
    @patch("auto_slopp.utils.git_operations._run_git_command")
    @patch("auto_slopp.utils.git_operations._handle_git_operation_failure")
    def test_merge_main_fetch_fails_completely(self, mock_handle_failure, mock_run_git, mock_get_branch):
        """Test when fetch main completely fails."""
        repo_dir = Path("/tmp/test_repo")
        mock_get_branch.return_value = "feature/test"

        # Mock fetch to fail both times
        mock_run_git.side_effect = [
            Mock(returncode=1, stderr="fetch error 1", stdout=""),
            Mock(returncode=1, stderr="fetch error 2", stdout=""),
        ]

        success, message = merge_main_into_branch(repo_dir, "feature/test")

        assert success is False
        assert message == "fetch error 2"
        mock_handle_failure.assert_called_once()

    @patch("auto_slopp.utils.git_operations.get_current_branch")
    @patch("auto_slopp.utils.git_operations._run_git_command")
    @patch("auto_slopp.utils.git_operations.get_active_cli_command")
    def test_merge_main_abort_failure(self, mock_get_cli, mock_run_git, mock_get_branch):
        """Test merge failure and then abort merge also fails."""
        repo_dir = Path("/tmp/test_repo")
        mock_get_branch.return_value = "feature/test"
        mock_get_cli.return_value = None

        def side_effect(*args, **kwargs):
            if args[1] == "fetch":
                return Mock(returncode=0, stdout="", stderr="")
            if args[1] == "merge" and "--abort" not in args:
                return Mock(returncode=1, stdout="", stderr="merge conflict")
            if args[1] == "merge" and "--abort" in args:
                return Mock(returncode=1, stdout="", stderr="abort failed")
            return Mock(returncode=0, stdout="", stderr="")

        mock_run_git.side_effect = side_effect

        success, message = merge_main_into_branch(repo_dir, "feature/test")

        assert success is False
        assert message == "merge conflict"

    @patch("auto_slopp.utils.git_operations.get_current_branch")
    @patch("auto_slopp.utils.git_operations._run_git_command")
    @patch("auto_slopp.utils.git_operations._handle_git_operation_failure")
    def test_merge_main_git_operation_error(self, mock_handle_failure, mock_run_git, mock_get_branch):
        """Test merge main throwing GitOperationError."""
        repo_dir = Path("/tmp/test_repo")
        mock_get_branch.return_value = "feature/test"

        mock_run_git.side_effect = GitOperationError("simulate git error")

        success, message = merge_main_into_branch(repo_dir, "feature/test")

        assert success is False
        assert "simulate git error" in message
        mock_handle_failure.assert_called_once()


class TestCheckoutBranchResilientEdgeCases:
    """Edge cases for checkout_branch_resilient."""

    @patch("auto_slopp.utils.git_operations._run_git_command")
    def test_checkout_pull_fails(self, mock_run_git):
        """Test checkout continues and returns True when pull fails after successful checkout."""
        repo_dir = Path("/tmp/test_repo")

        def side_effect(*args, **kwargs):
            if args[1] == "fetch":
                return Mock(returncode=1, stdout="", stderr="fetch fail")
            elif args[1] == "checkout":
                return Mock(returncode=0, stdout="", stderr="")
            elif args[1] == "pull":
                return Mock(returncode=1, stdout="", stderr="pull fail")
            return Mock(returncode=0)

        mock_run_git.side_effect = side_effect

        # Since fetch fails, it tries checkout. Checkout succeeds, then pull fails
        result = checkout_branch_resilient(repo_dir, "feature/test")

        assert result is True
