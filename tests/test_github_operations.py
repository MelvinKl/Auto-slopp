"""Tests for GitHub operations utilities."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from auto_slopp.utils.github_operations import (
    GitHubOperationError,
    comment_on_issue,
    comment_on_pr,
    create_pull_request,
    get_failed_workflow_logs,
    get_open_prs_with_label,
    get_pr_files,
    get_workflow_runs_for_branch,
    looks_like_error_message,
    remove_label_from_issue,
    submit_pr_review,
)


class TestLooksLikeErrorMessage:
    """Test cases for looks_like_error_message function."""

    def test_plain_text_is_not_error(self):
        assert looks_like_error_message("Completed by PR: https://github.com/user/repo/pull/123") is False
        assert looks_like_error_message("Please increase the timeout value to 60 seconds.") is False
        assert looks_like_error_message("No changes required for this issue.") is False

    def test_empty_text_is_not_error(self):
        assert looks_like_error_message("") is False

    def test_traceback_is_error(self):
        text = 'Traceback (most recent call last):\n  File "main.py", line 3, in <module>'
        assert looks_like_error_message(text) is True

    def test_error_prefix_is_error(self):
        assert looks_like_error_message("Error: gh command failed with exit code 1") is True

    def test_exception_text_is_error(self):
        assert looks_like_error_message("Unhandled exception while running the task") is True

    def test_cli_failure_output_is_error(self):
        assert looks_like_error_message("Fatal: GitHub command timed out after 30s") is True

    def test_extended_indicators_are_errors(self):
        assert looks_like_error_message("Error occurred while connecting to the API") is True
        assert looks_like_error_message("Fatal error: out of memory while running tests") is True
        assert looks_like_error_message("Command not found: foo") is True
        assert looks_like_error_message("Command aborted by the user") is True
        assert looks_like_error_message("Exit status 1: build step") is True
        assert looks_like_error_message("Process ended with a non-zero exit code") is True
        assert looks_like_error_message("Stack dump saved to /tmp/core.dump") is True
        assert looks_like_error_message("Panic: runtime error in worker") is True
        assert looks_like_error_message("Permission denied: /etc/passwd") is True
        assert looks_like_error_message("Connection refused by host") is True
        assert looks_like_error_message("No such file or directory: main.py") is True
        assert looks_like_error_message("Assertion failed: value == expected") is True

    def test_extended_indicators_do_not_flag_plain_text(self):
        assert looks_like_error_message("Completed by PR: https://github.com/user/repo/pull/123") is False
        assert looks_like_error_message("Please increase the timeout value to 60 seconds.") is False
        assert looks_like_error_message("No changes required for this issue.") is False


class TestCommentOnIssue:
    """Test cases for comment_on_issue function."""

    @patch("auto_slopp.utils.github_operations._run_gh_command")
    def test_comment_on_issue_success(self, mock_run_gh):
        """Test successful comment posting."""
        mock_run_gh.return_value = Mock(returncode=0)
        repo_dir = Path("/tmp/test_repo")

        result = comment_on_issue(repo_dir, 42, "Completed by PR: https://example.com/pull/1")

        assert result is True
        mock_run_gh.assert_called_once_with(
            repo_dir, "issue", "comment", "42", "--body", "Completed by PR: https://example.com/pull/1", check=False
        )

    @patch("auto_slopp.utils.github_operations._run_gh_command")
    def test_comment_on_issue_refuses_error_message(self, mock_run_gh):
        """Test that raw error messages are never posted to the issue."""
        mock_run_gh.return_value = Mock(returncode=0)
        repo_dir = Path("/tmp/test_repo")

        result = comment_on_issue(
            repo_dir, 42, 'Traceback (most recent call last):\n  File "main.py", line 3\nException: boom'
        )

        assert result is False
        mock_run_gh.assert_not_called()

    @patch("auto_slopp.utils.github_operations._run_gh_command")
    def test_comment_on_issue_failure_nonzero_exit(self, mock_run_gh):
        """Test comment posting with non-zero exit code."""
        mock_run_gh.return_value = Mock(returncode=1)
        repo_dir = Path("/tmp/test_repo")

        result = comment_on_issue(repo_dir, 42, "Plain comment")

        assert result is False

    @patch("auto_slopp.utils.github_operations._run_gh_command")
    def test_comment_on_issue_handles_unexpected_exception(self, mock_run_gh):
        """Test comment posting handles unexpected exceptions."""
        mock_run_gh.side_effect = RuntimeError("Unexpected error")
        repo_dir = Path("/tmp/test_repo")

        result = comment_on_issue(repo_dir, 42, "Plain comment")

        assert result is False


class TestCommentOnPR:
    """Test cases for comment_on_pr function."""

    @patch("auto_slopp.utils.github_operations._run_gh_command")
    def test_comment_on_pr_success(self, mock_run_gh):
        """Test successful PR comment posting."""
        mock_run_gh.return_value = Mock(returncode=0)
        repo_dir = Path("/tmp/test_repo")

        result = comment_on_pr(repo_dir, 42, "Looks good, thanks!")

        assert result is True
        mock_run_gh.assert_called_once_with(
            repo_dir, "pr", "comment", "42", "--body", "Looks good, thanks!", check=False
        )

    @patch("auto_slopp.utils.github_operations._run_gh_command")
    def test_comment_on_pr_refuses_error_message(self, mock_run_gh):
        """Test that raw error messages are never posted to the PR."""
        mock_run_gh.return_value = Mock(returncode=0)
        repo_dir = Path("/tmp/test_repo")

        result = comment_on_pr(
            repo_dir, 42, 'Traceback (most recent call last):\n  File "main.py", line 3\nException: boom'
        )

        assert result is False
        mock_run_gh.assert_not_called()

    @patch("auto_slopp.utils.github_operations._run_gh_command")
    def test_comment_on_pr_failure_nonzero_exit(self, mock_run_gh):
        """Test PR comment posting with non-zero exit code."""
        mock_run_gh.return_value = Mock(returncode=1)
        repo_dir = Path("/tmp/test_repo")

        result = comment_on_pr(repo_dir, 42, "Plain comment")

        assert result is False


class TestCreatePullRequest:
    """Test cases for create_pull_request function."""

    @patch("auto_slopp.utils.github_operations._run_gh_command")
    def test_create_pull_request_success(self, mock_run_gh):
        """Test successful PR creation."""
        mock_run_gh.return_value = Mock(returncode=0, stdout="https://github.com/user/repo/pull/123")
        repo_dir = Path("/tmp/test_repo")

        result = create_pull_request(repo_dir, "#42: Fix bug", "Changes described here", head="ai/issue-42-fix-bug")

        assert result == {"url": "https://github.com/user/repo/pull/123", "number": 123}
        mock_run_gh.assert_called_once_with(
            repo_dir,
            "pr",
            "create",
            "--title",
            "#42: Fix bug",
            "--body",
            "Changes described here",
            "--head",
            "ai/issue-42-fix-bug",
            "--base",
            "main",
            check=False,
        )

    @patch("auto_slopp.utils.github_operations._run_gh_command")
    def test_create_pull_request_refuses_error_title(self, mock_run_gh):
        """Test that a PR with an error-like title is never created."""
        mock_run_gh.return_value = Mock(returncode=0)
        repo_dir = Path("/tmp/test_repo")

        result = create_pull_request(repo_dir, "Error: gh command failed", "Plain body", head="feature")

        assert result is None
        mock_run_gh.assert_not_called()

    @patch("auto_slopp.utils.github_operations._run_gh_command")
    def test_create_pull_request_refuses_error_body(self, mock_run_gh):
        """Test that a PR with an error-like body is never created."""
        mock_run_gh.return_value = Mock(returncode=0)
        repo_dir = Path("/tmp/test_repo")

        result = create_pull_request(
            repo_dir, "#42: Fix bug", "Traceback (most recent call last):\nException: boom", head="feature"
        )

        assert result is None
        mock_run_gh.assert_not_called()

    @patch("auto_slopp.utils.github_operations._run_gh_command")
    def test_create_pull_request_failure_nonzero_exit(self, mock_run_gh):
        """Test PR creation with non-zero exit code."""
        mock_run_gh.return_value = Mock(returncode=1, stderr="error")
        repo_dir = Path("/tmp/test_repo")

        result = create_pull_request(repo_dir, "#42: Fix bug", "Plain body", head="feature")

        assert result is None


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

    @patch("auto_slopp.utils.github_operations._run_gh_command")
    def test_submit_pr_review_refuses_error_body(self, mock_run_gh):
        """Test that a review with an error-like body is never submitted."""
        mock_run_gh.return_value = Mock(returncode=0)
        repo_dir = Path("/tmp/test_repo")

        result = submit_pr_review(repo_dir, 123, "Traceback (most recent call last):\nException: boom", event="COMMENT")

        assert result is False
        mock_run_gh.assert_not_called()


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
