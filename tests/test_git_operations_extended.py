"""Extended tests for git operations utilities to cover missing lines."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from auto_slopp.utils.git_operations import (
    GitOperationError,
    commit_and_push_changes,
    create_and_checkout_branch,
)


class TestCreateAndCheckoutBranch:
    """Test cases for create_and_checkout_branch function."""

    @patch("auto_slopp.utils.git_operations.branch_exists")
    @patch("auto_slopp.utils.git_operations.checkout_branch_resilient")
    def test_branch_already_exists(self, mock_checkout, mock_exists):
        """Test when the branch already exists."""
        repo_dir = Path("/tmp/test_repo")
        mock_exists.return_value = True
        mock_checkout.return_value = True

        result = create_and_checkout_branch(repo_dir, "feature/test")

        assert result is True
        mock_exists.assert_called_once_with(repo_dir, "feature/test")
        mock_checkout.assert_called_once_with(repo_dir, "feature/test", fetch_first=False, timeout=60)

    @patch("auto_slopp.utils.git_operations.branch_exists")
    @patch("auto_slopp.utils.git_operations._run_git_command")
    def test_create_branch_success(self, mock_run_git, mock_exists):
        """Test successful branch creation."""
        repo_dir = Path("/tmp/test_repo")
        mock_exists.return_value = False
        mock_run_git.return_value = Mock(returncode=0)

        result = create_and_checkout_branch(repo_dir, "feature/test", "main")

        assert result is True
        mock_run_git.assert_called_once_with(
            repo_dir, "checkout", "-b", "feature/test", "main", check=False, timeout=60
        )

    @patch("auto_slopp.utils.git_operations.branch_exists")
    @patch("auto_slopp.utils.git_operations._run_git_command")
    def test_create_branch_failure(self, mock_run_git, mock_exists):
        """Test failed branch creation."""
        repo_dir = Path("/tmp/test_repo")
        mock_exists.return_value = False
        mock_run_git.return_value = Mock(
            returncode=1, stderr="fatal: A branch named 'feature/test' already exists.", stdout=""
        )

        result = create_and_checkout_branch(repo_dir, "feature/test", "main")

        assert result is False

    @patch("auto_slopp.utils.git_operations.branch_exists")
    def test_create_branch_git_operation_error(self, mock_exists):
        """Test branch creation when a GitOperationError is raised."""
        repo_dir = Path("/tmp/test_repo")
        mock_exists.side_effect = GitOperationError("Failed to check if branch exists")

        result = create_and_checkout_branch(repo_dir, "feature/test", "main")

        assert result is False


class TestCommitAndPushChanges:
    """Test cases for commit_and_push_changes function."""

    @patch("auto_slopp.utils.git_operations.os.chdir")
    @patch("auto_slopp.utils.git_operations.is_git_repo")
    @patch("auto_slopp.utils.git_operations.has_changes")
    @patch("auto_slopp.utils.git_operations._run_git_command")
    def test_no_changes_to_commit(self, mock_run_git, mock_has_changes, mock_is_git_repo, mock_chdir):
        """Test when there are no changes to commit."""
        repo_dir = Path("/tmp/test_repo")
        mock_is_git_repo.return_value = True
        mock_has_changes.return_value = False

        commit_success, push_success = commit_and_push_changes(repo_dir, "Test commit message")

        assert commit_success is True
        assert push_success is None
        mock_run_git.assert_called_once_with(repo_dir, "add", ".")
        mock_chdir.assert_any_call(repo_dir)

    @patch("auto_slopp.utils.git_operations.os.chdir")
    @patch("auto_slopp.utils.git_operations.is_git_repo")
    @patch("auto_slopp.utils.git_operations.has_changes")
    @patch("auto_slopp.utils.git_operations._run_git_command")
    def test_commit_and_push_with_remote(self, mock_run_git, mock_has_changes, mock_is_git_repo, mock_chdir):
        """Test commit and push when a remote exists."""
        repo_dir = Path("/tmp/test_repo")
        mock_is_git_repo.return_value = True
        mock_has_changes.return_value = True

        # Setup mock returns for _run_git_command
        def side_effect(*args, **kwargs):
            if args[1] == "remote":
                return Mock(stdout="origin  https://github.com/repo.git (fetch)\n")
            return Mock()

        mock_run_git.side_effect = side_effect

        commit_success, push_success = commit_and_push_changes(repo_dir, "Test commit")

        assert commit_success is True
        assert push_success is True
        assert mock_run_git.call_count == 4  # add, commit, remote, push

    @patch("auto_slopp.utils.git_operations.os.chdir")
    @patch("auto_slopp.utils.git_operations.is_git_repo")
    @patch("auto_slopp.utils.git_operations.has_changes")
    @patch("auto_slopp.utils.git_operations._run_git_command")
    def test_commit_and_push_no_remote(self, mock_run_git, mock_has_changes, mock_is_git_repo, mock_chdir):
        """Test commit when no remote exists."""
        repo_dir = Path("/tmp/test_repo")
        mock_is_git_repo.return_value = True
        mock_has_changes.return_value = True

        # Setup mock returns for _run_git_command
        def side_effect(*args, **kwargs):
            if args[1] == "remote":
                return Mock(stdout="")
            return Mock()

        mock_run_git.side_effect = side_effect

        commit_success, push_success = commit_and_push_changes(repo_dir, "Test commit")

        assert commit_success is True
        assert push_success is None
        assert mock_run_git.call_count == 3  # add, commit, remote

    @patch("auto_slopp.utils.git_operations.os.chdir")
    @patch("auto_slopp.utils.git_operations.is_git_repo")
    @patch("auto_slopp.utils.git_operations._run_git_command")
    def test_not_git_repo(self, mock_run_git, mock_is_git_repo, mock_chdir):
        """Test initialization of git repo if not present."""
        repo_dir = Path("/tmp/test_repo")
        mock_is_git_repo.return_value = False

        # Raise an exception when calling has_changes so we don't need to mock it, just testing it hits `init`
        mock_run_git.side_effect = GitOperationError("Simulated error")

        with pytest.raises(GitOperationError):
            commit_and_push_changes(repo_dir, "Test commit")

        assert mock_run_git.call_args_list[0][0][1] == "init"

    @patch("auto_slopp.utils.git_operations.os.chdir")
    @patch("auto_slopp.utils.git_operations.is_git_repo")
    @patch("auto_slopp.utils.git_operations._handle_git_operation_failure")
    def test_git_operation_error(self, mock_handle_failure, mock_is_git_repo, mock_chdir):
        """Test error handling when GitOperationError is raised."""
        repo_dir = Path("/tmp/test_repo")
        mock_is_git_repo.side_effect = GitOperationError("Simulated error")

        with pytest.raises(GitOperationError):
            commit_and_push_changes(repo_dir, "Test commit")

        mock_handle_failure.assert_called_once()
