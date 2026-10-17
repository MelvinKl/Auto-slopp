"""Tests for GitHub operations utilities."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from auto_slopp.utils.github_operations import (
    GitHubOperationError,
    get_failed_workflow_logs,
    get_open_prs_with_label,
    get_pr_files,
    get_pull_requests_for_issue,
    get_workflow_runs_for_branch,
    merge_pull_request,
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
    @patch("auto_slopp.utils.github_operations.subprocess.run")
    def test_get_workflow_runs_for_branch_success(self, mock_subprocess_run, mock_run_gh):
        """Test successful retrieval of workflow runs for branch."""
        mock_subprocess_run.return_value = Mock(returncode=0, stdout="abc123")
        mock_run_gh.return_value = Mock(
            returncode=0,
            stdout=(
                '[{"conclusion": "success", "name": "CI", "headSha": "abc123", "event": "pull_request", '
                '"status": "completed", "databaseId": 123}]'
            ),
        )
        repo_dir = Path("/tmp/test_repo")
        result = get_workflow_runs_for_branch(repo_dir, "main")
        assert len(result) == 1
        assert result[0]["conclusion"] == "success"
        assert result[0]["name"] == "CI"
        assert result[0]["headSha"] == "abc123"
        assert result[0]["event"] == "pull_request"
        assert result[0]["status"] == "completed"
        assert result[0]["databaseId"] == 123

    @patch("auto_slopp.utils.github_operations._run_gh_command")
    @patch("auto_slopp.utils.github_operations.subprocess.run")
    def test_get_workflow_runs_for_branch_with_event_filter(self, mock_subprocess_run, mock_run_gh):
        """Test retrieval of workflow runs for branch with event filter."""
        mock_subprocess_run.return_value = Mock(returncode=0, stdout="abc123")
        mock_run_gh.return_value = Mock(
            returncode=0,
            stdout=(
                '[{"conclusion": "success", "name": "CI", "headSha": "abc123", "event": "pull_request", '
                '"status": "completed", "databaseId": 123}, '
                '{"conclusion": "failure", "name": "Lint", "headSha": "def456", "event": "push", '
                '"status": "completed", "databaseId": 124}]'
            ),
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
        """Test get_workflow_runs_for_branch handles JSON decode errors."""
        mock_run_gh.return_value = Mock(returncode=0, stdout="invalid json")
        repo_dir = Path("/tmp/test_repo")
        result = get_workflow_runs_for_branch(repo_dir, "main")
        assert result == []


class TestGetFailedWorkflowLogs:
    """Test cases for get_failed_workflow_logs function."""

    @patch("auto_slopp.utils.github_operations._run_gh_command")
    def test_get_failed_workflow_logs_success(self, mock_run_gh):
        """Test successful retrieval of failed workflow logs."""
        mock_run_gh.return_value = Mock(returncode=0, stdout="error output")
        repo_dir = Path("/tmp/test_repo")
        run = {"conclusion": "failure", "name": "CI", "status": "completed", "databaseId": 123}
        result = get_failed_workflow_logs(repo_dir, run)
        assert result == "error output"
        mock_run_gh.assert_called_once_with(repo_dir, "run", "view", "123", "--log-failed", check=False, timeout=120)

    @patch("auto_slopp.utils.github_operations._run_gh_command")
    def test_get_failed_workflow_logs_failure(self, mock_run_gh):
        """Test get_failed_workflow_logs returns empty string when gh and fallback both fail."""
        mock_run_gh.side_effect = [
            Mock(returncode=1, stderr="error"),
            Mock(returncode=1, stderr="no jobs"),
        ]
        repo_dir = Path("/tmp/test_repo")
        run = {"conclusion": "failure", "name": "CI", "status": "completed", "databaseId": 123}
        result = get_failed_workflow_logs(repo_dir, run)
        assert result == ""

    @patch("auto_slopp.utils.github_operations._run_gh_command")
    def test_get_failed_workflow_logs_falls_back_to_job_logs(self, mock_run_gh):
        """Test get_failed_workflow_logs falls back to per-job logs when --log-failed is empty."""
        jobs_json = (
            '{"jobs": [{"name": "Build", "conclusion": "failure", "databaseId": 1}, '
            '{"name": "Test", "conclusion": "success", "databaseId": 2}]}'
        )
        mock_run_gh.side_effect = [
            Mock(returncode=0, stdout=""),
            Mock(returncode=0, stdout=jobs_json),
            Mock(returncode=0, stdout="job failure log"),
        ]
        repo_dir = Path("/tmp/test_repo")
        run = {"conclusion": "failure", "name": "CI", "status": "completed", "databaseId": 123}
        result = get_failed_workflow_logs(repo_dir, run)
        assert "job failure log" in result
        assert "Build" in result
        mock_run_gh.assert_any_call(repo_dir, "run", "view", "123", "--json", "jobs", check=False, timeout=120)
        mock_run_gh.assert_any_call(
            repo_dir, "run", "view", "123", "--job", "1", "--log-failed", check=False, timeout=120
        )

    @patch("auto_slopp.utils.github_operations._run_gh_command")
    def test_get_failed_workflow_logs_missing_database_id(self, mock_run_gh):
        """Test get_failed_workflow_logs returns empty string when the run has no databaseId."""
        repo_dir = Path("/tmp/test_repo")
        run = {"conclusion": "failure", "name": "CI", "status": "completed"}
        result = get_failed_workflow_logs(repo_dir, run)
        assert result == ""
        mock_run_gh.assert_not_called()

    @patch("auto_slopp.utils.github_operations._run_gh_command")
    def test_get_failed_workflow_logs_handles_github_operation_error(self, mock_run_gh):
        """Test get_failed_workflow_logs handles GitHubOperationError."""
        mock_run_gh.side_effect = GitHubOperationError("API error")
        repo_dir = Path("/tmp/test_repo")
        run = {"conclusion": "failure", "name": "CI", "status": "completed", "databaseId": 123}
        result = get_failed_workflow_logs(repo_dir, run)
        assert result == ""

    @patch("auto_slopp.utils.github_operations._run_gh_command")
    def test_get_failed_workflow_logs_handles_unexpected_exception(self, mock_run_gh):
        """Test get_failed_workflow_logs handles unexpected exceptions."""
        mock_run_gh.side_effect = RuntimeError("Unexpected error")
        repo_dir = Path("/tmp/test_repo")
        run = {"conclusion": "failure", "name": "CI", "status": "completed", "databaseId": 123}
        result = get_failed_workflow_logs(repo_dir, run)
        assert result == ""


class TestGetPullRequestsForIssue:
    """Test cases for get_pull_requests_for_issue function."""

    @patch("auto_slopp.utils.github_operations._run_gh_command")
    def test_get_pull_requests_for_issue_success(self, mock_run_gh):
        """Test success returns the linked PRs as a list."""
        mock_run_gh.return_value = Mock(
            returncode=0, stdout='[{"number": 7, "title": "Fix", "state": "CLOSED", "url": "u"}]'
        )
        repo_dir = Path("/tmp/test_repo")
        result = get_pull_requests_for_issue(repo_dir, 42)
        assert result == [{"number": 7, "title": "Fix", "state": "CLOSED", "url": "u"}]
        mock_run_gh.assert_called_once_with(
            repo_dir,
            "issue",
            "view",
            "42",
            "--pulls",
            "--json=number,title,state,url",
            check=False,
        )

    @patch("auto_slopp.utils.github_operations._run_gh_command")
    def test_get_pull_requests_for_issue_object_with_pulls_key(self, mock_run_gh):
        """Test object-form response (gh <2) is unwrapped into a list."""
        mock_run_gh.return_value = Mock(
            returncode=0, stdout='{"pulls": [{"number": 7, "title": "Fix", "state": "CLOSED", "url": "u"}]}'
        )
        repo_dir = Path("/tmp/test_repo")
        result = get_pull_requests_for_issue(repo_dir, 42)
        assert result == [{"number": 7, "title": "Fix", "state": "CLOSED", "url": "u"}]

    @patch("auto_slopp.utils.github_operations._run_gh_command")
    def test_get_pull_requests_for_issue_empty_output(self, mock_run_gh):
        """Test empty output returns an empty list."""
        mock_run_gh.return_value = Mock(returncode=0, stdout="")
        repo_dir = Path("/tmp/test_repo")
        result = get_pull_requests_for_issue(repo_dir, 42)
        assert result == []

    @patch("auto_slopp.utils.github_operations._run_gh_command")
    def test_get_pull_requests_for_issue_failure(self, mock_run_gh):
        """Test failure returns empty list."""
        mock_run_gh.return_value = Mock(returncode=1, stderr="no linked pull requests")
        repo_dir = Path("/tmp/test_repo")
        result = get_pull_requests_for_issue(repo_dir, 42)
        assert result == []

    @patch("auto_slopp.utils.github_operations._run_gh_command")
    def test_get_pull_requests_for_issue_handles_exceptions(self, mock_run_gh):
        """Test unexpected errors return an empty list without raising."""
        mock_run_gh.side_effect = RuntimeError("boom")
        repo_dir = Path("/tmp/test_repo")
        result = get_pull_requests_for_issue(repo_dir, 42)
        assert result == []


class TestMergePullRequest:
    """Test cases for merge_pull_request function."""

    @patch("auto_slopp.utils.github_operations._run_gh_command")
    def test_merge_pull_request_default_squash(self, mock_run_gh):
        """Test default merge method is squash and returns success."""
        mock_run_gh.return_value = Mock(returncode=0)
        repo_dir = Path("/tmp/test_repo")
        result = merge_pull_request(repo_dir, 7)
        assert result is True
        mock_run_gh.assert_called_once_with(repo_dir, "pr", "merge", "7", "--squash", check=False)

    @patch("auto_slopp.utils.github_operations._run_gh_command")
    def test_merge_pull_request_method_flags(self, mock_run_gh):
        """Test that the merge method and options map to gh flags."""
        mock_run_gh.return_value = Mock(returncode=0)
        repo_dir = Path("/tmp/test_repo")
        result = merge_pull_request(repo_dir, 7, merge_method="rebase", delete_branch=True, skip_status_checks=True)
        assert result is True
        mock_run_gh.assert_called_once_with(
            repo_dir, "pr", "merge", "7", "--rebase", "--delete-branch", "--skip-checks", check=False
        )

    @patch("auto_slopp.utils.github_operations._run_gh_command")
    def test_merge_pull_request_failure(self, mock_run_gh):
        """Test merge returns False on failure."""
        mock_run_gh.return_value = Mock(returncode=1, stderr="conflict")
        repo_dir = Path("/tmp/test_repo")
        result = merge_pull_request(repo_dir, 7)
        assert result is False

    @patch("auto_slopp.utils.github_operations._run_gh_command")
    def test_merge_pull_request_handles_exceptions(self, mock_run_gh):
        """Test merge returns False on unexpected errors without raising."""
        mock_run_gh.side_effect = RuntimeError("boom")
        repo_dir = Path("/tmp/test_repo")
        result = merge_pull_request(repo_dir, 7)
        assert result is False
