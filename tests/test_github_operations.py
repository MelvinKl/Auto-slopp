"""Tests for GitHub operations utilities."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from auto_slopp.utils.github_operations import (
    GitHubOperationError,
    get_open_prs_with_label,
    get_pr_files,
    get_workflow_runs_for_branch,
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


class TestGetWorkflowRunsForBranch:
    """Test cases for get_workflow_runs_for_branch function."""

    @patch("auto_slopp.utils.github_operations._run_gh_command")
    def test_get_workflow_runs_for_branch_success(self, mock_run_gh):
        """Test successful retrieval of workflow runs for branch."""
        mock_run_gh.return_value = Mock(
            returncode=0,
            stdout='[{"conclusion": "success", "workflowName": "CI", "headSha": "abc123", "event": "pull_request", "status": "completed", "databaseId": 123}]',
        )
        repo_dir = Path("/tmp/test_repo")
        result = get_workflow_runs_for_branch(repo_dir, "main")
        assert len(result) == 1
        assert result[0]["conclusion"] == "success"
        assert result[0]["workflowName"] == "CI"
        assert result[0]["headSha"] == "abc123"
        assert result[0]["event"] == "pull_request"
        assert result[0]["status"] == "completed"
        assert result[0]["databaseId"] == 123

    @patch("auto_slopp.utils.github_operations._run_gh_command")
    def test_get_workflow_runs_for_branch_with_event_filter(self, mock_run_gh):
        """Test retrieval of workflow runs for branch with event filter."""
        mock_run_gh.return_value = Mock(
            returncode=0,
            stdout='[{"conclusion": "success", "workflowName": "CI", "headSha": "abc123", "event": "pull_request", "status": "completed", "databaseId": 123}, {"conclusion": "failure", "workflowName": "Lint", "headSha": "def456", "event": "push", "status": "completed", "databaseId": 124}]',
        )
        repo_dir = Path("/tmp/test_repo")
        result = get_workflow_runs_for_branch(repo_dir, "main", event="pull_request")
        assert len(result) == 1
        assert result[0]["event"] == "pull_request"

    @patch("auto_slopp.utils.github_operations._run_gh_command")
    def test_get_workflow_runs_for_branch_failure(self, mock_run_gh):
        """Test get_workflow_runs_for_branch returns empty list on failure."""
        mock_run_gh.return_value = Mock(returncode=1, stderr="error")
        repo_dir = Path("/tmp/test_repo")
        result = get_workflow_runs_for_branch(repo_dir, "main")
        assert result == []

    @patch("auto_slopp.utils.github_operations._run_gh_command")
    def test_get_workflow_runs_for_branch_handles_github_operation_error(self, mock_run_gh):
        """Test get_workflow_runs_for_branch handles GitHubOperationError."""
        mock_run_gh.side_effect = GitHubOperationError("API error")
        repo_dir = Path("/tmp/test_repo")
        result = get_workflow_runs_for_branch(repo_dir, "main")
        assert result == []

    @patch("auto_slopp.utils.github_operations._run_gh_command")
    def test_get_workflow_runs_for_branch_handles_unexpected_exception(self, mock_run_gh):
        """Test get_workflow_runs_for_branch handles unexpected exceptions."""
        mock_run_gh.side_effect = RuntimeError("Unexpected error")
        repo_dir = Path("/tmp/test_repo")
        result = get_workflow_runs_for_branch(repo_dir, "main")
        assert result == []

    @patch("auto_slopp.utils.github_operations._run_gh_command")
    def test_get_workflow_runs_for_branch_handles_json_decode_error(self, mock_run_gh):
        """Test get_workflow_runs_for_branch handles JSON decode error."""
        mock_run_gh.return_value = Mock(returncode=0, stdout="invalid json")
        repo_dir = Path("/tmp/test_repo")
        result = get_workflow_runs_for_branch(repo_dir, "main")
        assert result == []
