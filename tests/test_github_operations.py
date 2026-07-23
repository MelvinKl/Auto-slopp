"""Tests for GitHub operations utilities."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from auto_slopp.utils.github_operations import (
    GitHubOperationError,
    add_label_to_issue,
    create_pull_request,
    get_open_prs_with_label,
    get_pr_files,
    remove_label_from_issue,
    submit_pr_review,
)


class TestRemoveLabelFromIssue:
    """Test cases for remove_label_from_issue function."""

    @patch("auto_slopp.utils.github_operations._run_gh_command")
    def test_remove_label_success(self, mock_run_gh):
        """Test successful label removal."""
        mock_run_gh.return_value = Mock(returncode=0)
        repo_dir = Path("/tmp/test_repo")

        result = remove_label_from_issue(repo_dir, 42, "ai")

        assert result is True
        mock_run_gh.assert_called_once_with(repo_dir, "issue", "edit", "42", "--remove-label", "ai", check=False)

    @patch("auto_slopp.utils.github_operations._run_gh_command")
    def test_remove_label_failure_nonzero_exit(self, mock_run_gh):
        """Test label removal with non-zero exit code."""
        mock_run_gh.return_value = Mock(returncode=1)
        repo_dir = Path("/tmp/test_repo")

        result = remove_label_from_issue(repo_dir, 42, "ai")

        assert result is False

    @patch("auto_slopp.utils.github_operations._run_gh_command")
    def test_remove_label_handles_github_operation_error(self, mock_run_gh):
        """Test label removal handles GitHubOperationError."""
        mock_run_gh.side_effect = GitHubOperationError("API error")
        repo_dir = Path("/tmp/test_repo")

        result = remove_label_from_issue(repo_dir, 42, "ai")

        assert result is False

    @patch("auto_slopp.utils.github_operations._run_gh_command")
    def test_remove_label_handles_unexpected_exception(self, mock_run_gh):
        """Test label removal handles unexpected exceptions."""
        mock_run_gh.side_effect = RuntimeError("Unexpected error")
        repo_dir = Path("/tmp/test_repo")

        result = remove_label_from_issue(repo_dir, 42, "ai")

        assert result is False


class TestAddLabelToIssue:
    """Test cases for add_label_to_issue function."""

    @patch("auto_slopp.utils.github_operations._run_gh_command")
    def test_add_label_success(self, mock_run_gh):
        """Test successful label addition."""
        mock_run_gh.return_value = Mock(returncode=0)
        repo_dir = Path("/tmp/test_repo")

        result = add_label_to_issue(repo_dir, 42, "ai")

        assert result is True
        mock_run_gh.assert_called_once_with(repo_dir, "issue", "edit", "42", "--add-label", "ai", check=False)

    @patch("auto_slopp.utils.github_operations._run_gh_command")
    def test_add_label_failure_nonzero_exit(self, mock_run_gh):
        """Test label addition with non-zero exit code."""
        mock_run_gh.return_value = Mock(returncode=1)
        repo_dir = Path("/tmp/test_repo")

        result = add_label_to_issue(repo_dir, 42, "ai")

        assert result is False

    @patch("auto_slopp.utils.github_operations._run_gh_command")
    def test_add_label_handles_github_operation_error(self, mock_run_gh):
        """Test label addition handles GitHubOperationError."""
        mock_run_gh.side_effect = GitHubOperationError("API error")
        repo_dir = Path("/tmp/test_repo")

        result = add_label_to_issue(repo_dir, 42, "ai")

        assert result is False

    @patch("auto_slopp.utils.github_operations._run_gh_command")
    def test_add_label_handles_unexpected_exception(self, mock_run_gh):
        """Test label addition handles unexpected exceptions."""
        mock_run_gh.side_effect = RuntimeError("Unexpected error")
        repo_dir = Path("/tmp/test_repo")

        result = add_label_to_issue(repo_dir, 42, "ai")

        assert result is False


class TestGetOpenPRsWithLabel:
    """Test cases for get_open_prs_with_label function."""

    @patch("auto_slopp.utils.github_operations._run_gh_command")
    def test_get_open_prs_with_label_success(self, mock_run_gh):
        """Test successful retrieval of PRs with label."""
        mock_run_gh.return_value = Mock(returncode=0, stdout='[{"number": 1, "title": "test"}]')
        repo_dir = Path("/tmp/test_repo")
        result = get_open_prs_with_label(repo_dir, "test")
        assert result == [{"number": 1, "title": "test"}]

    @patch("auto_slopp.utils.github_operations._run_gh_command")
    def test_get_open_prs_with_label_failure(self, mock_run_gh):
        """Test get_open_prs_with_label returns empty list on failure."""
        mock_run_gh.return_value = Mock(returncode=1, stderr="error")
        repo_dir = Path("/tmp/test_repo")
        result = get_open_prs_with_label(repo_dir, "test")
        assert result == []


class TestGetPRFiles:
    """Test cases for get_pr_files function."""

    @patch("auto_slopp.utils.github_operations._run_gh_command")
    def test_get_pr_files_success(self, mock_run_gh):
        """Test successful retrieval of PR files."""
        mock_run_gh.return_value = Mock(returncode=0, stdout="diff content")
        repo_dir = Path("/tmp/test_repo")
        result = get_pr_files(repo_dir, 123)
        assert result == "diff content"

    @patch("auto_slopp.utils.github_operations._run_gh_command")
    def test_get_pr_files_failure(self, mock_run_gh):
        """Test get_pr_files raises GitHubOperationError on failure."""
        mock_run_gh.return_value = Mock(returncode=1, stderr="error")
        repo_dir = Path("/tmp/test_repo")
        with pytest.raises(GitHubOperationError):
            get_pr_files(repo_dir, 123)


class TestSubmitPRReview:
    """Test cases for submit_pr_review function."""

    @patch("auto_slopp.utils.github_operations._run_gh_command")
    def test_submit_pr_review_success(self, mock_run_gh):
        """Test successful submission of PR review."""
        mock_run_gh.return_value = Mock(returncode=0)
        repo_dir = Path("/tmp/test_repo")
        result = submit_pr_review(repo_dir, 123, "Looks good")
        assert result is True

    @patch("auto_slopp.utils.github_operations._run_gh_command")
    def test_submit_pr_review_failure(self, mock_run_gh):
        """Test submit_pr_review returns False on failure."""
        mock_run_gh.return_value = Mock(returncode=1)
        repo_dir = Path("/tmp/test_repo")
        result = submit_pr_review(repo_dir, 123, "Looks good")
        assert result is False


class TestCreatePullRequest:
    """Test cases for create_pull_request function."""

    @patch("auto_slopp.utils.github_operations._run_gh_command")
    @patch("auto_slopp.utils.github_operations.add_label_to_issue")
    @patch("auto_slopp.utils.github_operations.settings.pr_review_worker_required_label", "test-label")
    def test_create_pull_request_success(self, mock_add_label, mock_run_gh):
        """Test successful PR creation and label addition."""
        mock_run_gh.return_value = Mock(returncode=0, stdout="https://github.com/user/repo/pull/123")
        repo_dir = Path("/tmp/test_repo")
        result = create_pull_request(repo_dir, "title", "body", "branch")

        assert result is not None
        assert result["url"] == "https://github.com/user/repo/pull/123"
        assert result["number"] == 123
        mock_run_gh.assert_called_once_with(
            repo_dir,
            "pr",
            "create",
            "--title",
            "title",
            "--body",
            "body",
            "--head",
            "branch",
            "--base",
            "main",
            check=False,
        )
        mock_add_label.assert_called_once_with(repo_dir, 123, "test-label")

    @patch("auto_slopp.utils.github_operations._run_gh_command")
    @patch("auto_slopp.utils.github_operations.add_label_to_issue")
    @patch("auto_slopp.utils.github_operations.settings.pr_review_worker_required_label", "test-label")
    def test_create_pull_request_failure_gh_command(self, mock_add_label, mock_run_gh):
        """Test PR creation fails when gh command returns non-zero exit code."""
        mock_run_gh.return_value = Mock(returncode=1, stderr="error")
        repo_dir = Path("/tmp/test_repo")
        result = create_pull_request(repo_dir, "title", "body", "branch")

        assert result is None
        mock_run_gh.assert_called_once_with(
            repo_dir,
            "pr",
            "create",
            "--title",
            "title",
            "--body",
            "body",
            "--head",
            "branch",
            "--base",
            "main",
            check=False,
        )
        mock_add_label.assert_not_called()

    @patch("auto_slopp.utils.github_operations._run_gh_command")
    @patch("auto_slopp.utils.github_operations.add_label_to_issue")
    @patch("auto_slopp.utils.github_operations.settings.pr_review_worker_required_label", "test-label")
    def test_create_pull_request_label_failure_non_blocking(self, mock_add_label, mock_run_gh):
        """Test PR creation succeeds but label addition fails (non-blocking)."""
        mock_run_gh.return_value = Mock(returncode=0, stdout="https://github.com/user/repo/pull/42")
        mock_add_label.side_effect = Exception("Label failed")
        repo_dir = Path("/tmp/test_repo")
        result = create_pull_request(repo_dir, "title", "body", "branch")

        assert result is not None
        assert result["url"] == "https://github.com/user/repo/pull/42"
        assert result["number"] == 42
        mock_run_gh.assert_called_once_with(
            repo_dir,
            "pr",
            "create",
            "--title",
            "title",
            "--body",
            "body",
            "--head",
            "branch",
            "--base",
            "main",
            check=False,
        )
        mock_add_label.assert_called_once_with(repo_dir, 42, "test-label")
