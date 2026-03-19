"""Tests for GitHub operations utilities."""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from auto_slopp.utils.github_operations import (
    GitHubOperationError,
    close_issue,
    comment_on_issue,
    create_pull_request,
    get_issue_comments,
    get_open_issues,
    get_open_pr_branches,
    get_open_prs,
    get_pr_for_branch,
)


class TestGitHubOperationsCloseIssue:
    """Tests for close_issue function."""

    def test_close_issue_success(self):
        """Test successful issue closing."""
        repo_dir = Path("/tmp/repo")

        mock_result = MagicMock()
        mock_result.returncode = 0

        with patch(
            "auto_slopp.utils.github_operations._run_gh_command",
            return_value=mock_result,
        ):
            result = close_issue(repo_dir, 123)
            assert result is True

    def test_close_issue_failure(self):
        """Test issue closing failure."""
        repo_dir = Path("/tmp/repo")

        mock_result = MagicMock()
        mock_result.returncode = 1

        with patch(
            "auto_slopp.utils.github_operations._run_gh_command",
            return_value=mock_result,
        ):
            result = close_issue(repo_dir, 123)
            assert result is False

    def test_close_issue_github_operation_error(self):
        """Test close_issue handles GitHubOperationError."""
        repo_dir = Path("/tmp/repo")

        with patch(
            "auto_slopp.utils.github_operations._run_gh_command",
            side_effect=GitHubOperationError("Command failed"),
        ):
            result = close_issue(repo_dir, 123)
            assert result is False

    def test_close_issue_unexpected_error(self):
        """Test close_issue handles unexpected errors."""
        repo_dir = Path("/tmp/repo")

        with patch(
            "auto_slopp.utils.github_operations._run_gh_command",
            side_effect=ValueError("Unexpected error"),
        ):
            result = close_issue(repo_dir, 123)
            assert result is False

    def test_close_issue_called_process_error(self):
        """Test close_issue handles subprocess.CalledProcessError."""
        repo_dir = Path("/tmp/repo")

        mock_error = subprocess.CalledProcessError(
            returncode=1,
            cmd=["gh", "issue", "close", "123"],
            stderr="Command failed",
        )

        with patch(
            "auto_slopp.utils.github_operations._run_gh_command",
            side_effect=mock_error,
        ):
            with patch("auto_slopp.utils.github_operations.logger") as mock_logger:
                result = close_issue(repo_dir, 123)

                assert result is False
                mock_logger.error.assert_called_once()


class TestGitHubOperationsCommentOnIssue:
    """Tests for comment_on_issue function."""

    def test_comment_on_issue_success(self):
        """Test successful comment posting."""
        repo_dir = Path("/tmp/repo")

        mock_result = MagicMock()
        mock_result.returncode = 0

        with patch(
            "auto_slopp.utils.github_operations._run_gh_command",
            return_value=mock_result,
        ):
            result = comment_on_issue(repo_dir, 123, "Test comment")
            assert result is True

    def test_comment_on_issue_failure(self):
        """Test comment posting failure."""
        repo_dir = Path("/tmp/repo")

        mock_result = MagicMock()
        mock_result.returncode = 1

        with patch(
            "auto_slopp.utils.github_operations._run_gh_command",
            return_value=mock_result,
        ):
            result = comment_on_issue(repo_dir, 123, "Test comment")
            assert result is False

    def test_comment_on_issue_github_operation_error(self):
        """Test comment_on_issue handles GitHubOperationError."""
        repo_dir = Path("/tmp/repo")

        with patch(
            "auto_slopp.utils.github_operations._run_gh_command",
            side_effect=GitHubOperationError("Command failed"),
        ):
            result = comment_on_issue(repo_dir, 123, "Test comment")
            assert result is False

    def test_comment_on_issue_unexpected_error(self):
        """Test comment_on_issue handles unexpected errors."""
        repo_dir = Path("/tmp/repo")

        with patch(
            "auto_slopp.utils.github_operations._run_gh_command",
            side_effect=TypeError("Unexpected error"),
        ):
            result = comment_on_issue(repo_dir, 123, "Test comment")
            assert result is False


class TestGitHubOperationsGetIssueComments:
    """Tests for get_issue_comments function."""

    def test_get_issue_comments_success(self):
        """Test successful comment retrieval."""
        repo_dir = Path("/tmp/repo")

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = (
            '{"comments": [{"body": "Test comment", "author": {"login": "user1"}, "createdAt": "2024-01-01"}]}'
        )

        with patch(
            "auto_slopp.utils.github_operations._run_gh_command",
            return_value=mock_result,
        ):
            result = get_issue_comments(repo_dir, 123)
            assert len(result) == 1
            assert result[0]["body"] == "Test comment"

    def test_get_issue_comments_failure(self):
        """Test comment retrieval failure."""
        repo_dir = Path("/tmp/repo")

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Error occurred"

        with patch(
            "auto_slopp.utils.github_operations._run_gh_command",
            return_value=mock_result,
        ):
            result = get_issue_comments(repo_dir, 123)
            assert result == []

    def test_get_issue_comments_invalid_json(self):
        """Test comment retrieval with invalid JSON."""
        repo_dir = Path("/tmp/repo")

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "not valid json"

        with patch(
            "auto_slopp.utils.github_operations._run_gh_command",
            return_value=mock_result,
        ):
            result = get_issue_comments(repo_dir, 123)
            assert result == []

    def test_get_issue_comments_github_operation_error(self):
        """Test get_issue_comments handles GitHubOperationError."""
        repo_dir = Path("/tmp/repo")

        with patch(
            "auto_slopp.utils.github_operations._run_gh_command",
            side_effect=GitHubOperationError("Command failed"),
        ):
            result = get_issue_comments(repo_dir, 123)
            assert result == []

    def test_get_issue_comments_unexpected_error(self):
        """Test get_issue_comments handles unexpected errors."""
        repo_dir = Path("/tmp/repo")

        with patch(
            "auto_slopp.utils.github_operations._run_gh_command",
            side_effect=RuntimeError("Unexpected error"),
        ):
            result = get_issue_comments(repo_dir, 123)
            assert result == []


class TestGitHubOperationsGetPRForBranch:
    """Tests for get_pr_for_branch function."""

    def test_get_pr_for_branch_success(self):
        """Test successful PR retrieval for branch."""
        repo_dir = Path("/tmp/repo")

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '{"url": "https://github.com/test/repo/pull/123", "number": 123, "state": "OPEN"}'

        with patch(
            "auto_slopp.utils.github_operations._run_gh_command",
            return_value=mock_result,
        ):
            result = get_pr_for_branch(repo_dir, "feature-branch")
            assert result is not None
            assert result["number"] == 123
            assert result["state"] == "OPEN"

    def test_get_pr_for_branch_not_found(self):
        """Test PR retrieval when no PR exists for branch."""
        repo_dir = Path("/tmp/repo")

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "no pull request found for this branch"

        with patch(
            "auto_slopp.utils.github_operations._run_gh_command",
            return_value=mock_result,
        ):
            result = get_pr_for_branch(repo_dir, "feature-branch")
            assert result is None

    def test_get_pr_for_branch_permission_denied(self):
        """Test PR retrieval with permission denied."""
        repo_dir = Path("/tmp/repo")

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Could not find repository"

        with patch(
            "auto_slopp.utils.github_operations._run_gh_command",
            return_value=mock_result,
        ):
            result = get_pr_for_branch(repo_dir, "feature-branch")
            assert result is None

    def test_get_pr_for_branch_invalid_json(self):
        """Test PR retrieval with invalid JSON."""
        repo_dir = Path("/tmp/repo")

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "invalid json"

        with patch(
            "auto_slopp.utils.github_operations._run_gh_command",
            return_value=mock_result,
        ):
            result = get_pr_for_branch(repo_dir, "feature-branch")
            assert result is None

    def test_get_pr_for_branch_github_operation_error(self):
        """Test get_pr_for_branch handles GitHubOperationError."""
        repo_dir = Path("/tmp/repo")

        with patch(
            "auto_slopp.utils.github_operations._run_gh_command",
            side_effect=GitHubOperationError("Command failed"),
        ):
            result = get_pr_for_branch(repo_dir, "feature-branch")
            assert result is None

    def test_get_pr_for_branch_unexpected_error(self):
        """Test get_pr_for_branch handles unexpected errors."""
        repo_dir = Path("/tmp/repo")

        with patch(
            "auto_slopp.utils.github_operations._run_gh_command",
            side_effect=OSError("Unexpected error"),
        ):
            result = get_pr_for_branch(repo_dir, "feature-branch")
            assert result is None

    def test_get_pr_for_branch_generic_error(self):
        """Test get_pr_for_branch logs error for generic failures."""
        repo_dir = MagicMock(spec=Path)
        repo_dir.name = "test-repo"

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Generic error message"
        mock_result.stdout = ""

        with patch(
            "auto_slopp.utils.github_operations._run_gh_command",
            return_value=mock_result,
        ):
            with patch("auto_slopp.utils.github_operations.logger") as mock_logger:
                result = get_pr_for_branch(repo_dir, "feature-branch")

                assert result is None
                mock_logger.error.assert_called_once()


class TestGitHubOperationsCreatePullRequest:
    """Tests for create_pull_request function."""

    def test_create_pull_request_success(self):
        """Test successful PR creation."""
        repo_dir = Path("/tmp/repo")

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "https://github.com/test/repo/pull/123"

        with patch(
            "auto_slopp.utils.github_operations._run_gh_command",
            return_value=mock_result,
        ):
            result = create_pull_request(
                repo_dir,
                title="Test PR",
                body="PR description",
                head="feature-branch",
            )
            assert result is not None
            assert result["url"] == "https://github.com/test/repo/pull/123"

    def test_create_pull_request_failure(self):
        """Test PR creation failure."""
        repo_dir = Path("/tmp/repo")

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Failed to create PR"

        with patch(
            "auto_slopp.utils.github_operations._run_gh_command",
            return_value=mock_result,
        ):
            result = create_pull_request(
                repo_dir,
                title="Test PR",
                body="PR description",
                head="feature-branch",
            )
            assert result is None

    def test_create_pull_request_invalid_pr_number(self):
        """Test PR creation with invalid PR URL format."""
        repo_dir = Path("/tmp/repo")

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "https://github.com/test/repo/pull/abc"

        with patch(
            "auto_slopp.utils.github_operations._run_gh_command",
            return_value=mock_result,
        ):
            result = create_pull_request(
                repo_dir,
                title="Test PR",
                body="PR description",
                head="feature-branch",
            )
            assert result is not None
            assert result["number"] is None

    def test_create_pull_request_empty_url(self):
        """Test PR creation with empty URL."""
        repo_dir = Path("/tmp/repo")

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""

        with patch(
            "auto_slopp.utils.github_operations._run_gh_command",
            return_value=mock_result,
        ):
            result = create_pull_request(
                repo_dir,
                title="Test PR",
                body="PR description",
                head="feature-branch",
            )
            assert result is not None

    def test_create_pull_request_github_operation_error(self):
        """Test create_pull_request handles GitHubOperationError."""
        repo_dir = Path("/tmp/repo")

        with patch(
            "auto_slopp.utils.github_operations._run_gh_command",
            side_effect=GitHubOperationError("Command failed"),
        ):
            result = create_pull_request(
                repo_dir,
                title="Test PR",
                body="PR description",
                head="feature-branch",
            )
            assert result is None

    def test_create_pull_request_unexpected_error(self):
        """Test create_pull_request handles unexpected errors."""
        repo_dir = Path("/tmp/repo")

        with patch(
            "auto_slopp.utils.github_operations._run_gh_command",
            side_effect=MemoryError("Unexpected error"),
        ):
            result = create_pull_request(
                repo_dir,
                title="Test PR",
                body="PR description",
                head="feature-branch",
            )
            assert result is None


class TestGitHubOperationsGetOpenIssues:
    """Tests for get_open_issues function."""

    def test_get_open_issues_success(self):
        """Test successful issue retrieval."""
        repo_dir = Path("/tmp/repo")

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '[{"number": 1, "title": "Issue 1"}]'

        with patch(
            "auto_slopp.utils.github_operations._run_gh_command",
            return_value=mock_result,
        ):
            result = get_open_issues(repo_dir)
            assert len(result) == 1
            assert result[0]["number"] == 1

    def test_get_open_issues_permission_denied(self):
        """Test issue retrieval with permission denied."""
        repo_dir = Path("/tmp/repo")

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Could not resolve to a Repository"

        with patch(
            "auto_slopp.utils.github_operations._run_gh_command",
            return_value=mock_result,
        ):
            result = get_open_issues(repo_dir)
            assert result == []

    def test_get_open_issues_failure(self):
        """Test issue retrieval failure."""
        repo_dir = Path("/tmp/repo")

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Error occurred"

        with patch(
            "auto_slopp.utils.github_operations._run_gh_command",
            return_value=mock_result,
        ):
            result = get_open_issues(repo_dir)
            assert result == []

    def test_get_open_issues_invalid_json(self):
        """Test issue retrieval with invalid JSON."""
        repo_dir = Path("/tmp/repo")

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "not valid json"

        with patch(
            "auto_slopp.utils.github_operations._run_gh_command",
            return_value=mock_result,
        ):
            result = get_open_issues(repo_dir)
            assert result == []

    def test_get_open_issues_github_operation_error(self):
        """Test get_open_issues handles GitHubOperationError."""
        repo_dir = Path("/tmp/repo")

        with patch(
            "auto_slopp.utils.github_operations._run_gh_command",
            side_effect=GitHubOperationError("Command failed"),
        ):
            result = get_open_issues(repo_dir)
            assert result == []

    def test_get_open_issues_unexpected_error(self):
        """Test get_open_issues handles unexpected errors."""
        repo_dir = Path("/tmp/repo")

        with patch(
            "auto_slopp.utils.github_operations._run_gh_command",
            side_effect=PermissionError("Unexpected error"),
        ):
            result = get_open_issues(repo_dir)
            assert result == []


class TestGitHubOperationsGetOpenPRs:
    """Tests for get_open_prs function."""

    def test_get_open_prs_success(self):
        """Test successful PR retrieval."""
        repo_dir = Path("/tmp/repo")

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '[{"number": 1, "title": "PR 1"}]'

        with patch(
            "auto_slopp.utils.github_operations._run_gh_command",
            return_value=mock_result,
        ):
            result = get_open_prs(repo_dir)
            assert len(result) == 1
            assert result[0]["number"] == 1

    def test_get_open_prs_permission_denied(self):
        """Test PR retrieval with permission denied."""
        repo_dir = Path("/tmp/repo")

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Could not resolve to a Repository"

        with patch(
            "auto_slopp.utils.github_operations._run_gh_command",
            return_value=mock_result,
        ):
            result = get_open_prs(repo_dir)
            assert result == []

    def test_get_open_prs_failure(self):
        """Test PR retrieval failure."""
        repo_dir = Path("/tmp/repo")

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Error occurred"

        with patch(
            "auto_slopp.utils.github_operations._run_gh_command",
            return_value=mock_result,
        ):
            result = get_open_prs(repo_dir)
            assert result == []

    def test_get_open_prs_invalid_json(self):
        """Test PR retrieval with invalid JSON."""
        repo_dir = Path("/tmp/repo")

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "not valid json"

        with patch(
            "auto_slopp.utils.github_operations._run_gh_command",
            return_value=mock_result,
        ):
            result = get_open_prs(repo_dir)
            assert result == []

    def test_get_open_prs_github_operation_error(self):
        """Test get_open_prs handles GitHubOperationError."""
        repo_dir = Path("/tmp/repo")

        with patch(
            "auto_slopp.utils.github_operations._run_gh_command",
            side_effect=GitHubOperationError("Command failed"),
        ):
            result = get_open_prs(repo_dir)
            assert result == []

    def test_get_open_prs_unexpected_error(self):
        """Test get_open_prs handles unexpected errors."""
        repo_dir = Path("/tmp/repo")

        with patch(
            "auto_slopp.utils.github_operations._run_gh_command",
            side_effect=IOError("Unexpected error"),
        ):
            result = get_open_prs(repo_dir)
            assert result == []


class TestGitHubOperationsGetOpenPRBranches:
    """Tests for get_open_pr_branches function."""

    def test_get_open_pr_branches_success(self):
        """Test successful branch extraction from PRs."""
        repo_dir = Path("/tmp/repo")

        mock_prs = [
            {"headRefName": "feature-1"},
            {"headRefName": "feature-2"},
        ]

        with patch(
            "auto_slopp.utils.github_operations.get_open_prs",
            return_value=mock_prs,
        ):
            result = get_open_pr_branches(repo_dir)
            assert len(result) == 2
            assert "feature-1" in result
            assert "feature-2" in result

    def test_get_open_pr_branches_empty(self):
        """Test branch extraction when no PRs exist."""
        repo_dir = Path("/tmp/repo")

        with patch(
            "auto_slopp.utils.github_operations.get_open_prs",
            return_value=[],
        ):
            result = get_open_pr_branches(repo_dir)
            assert result == []


class TestRunGhCommandEnvHandling:
    """Tests for _run_gh_command environment variable handling."""

    def test_run_gh_command_with_env_file_and_none_values(self):
        """Test _run_gh_command filters None values from dotenv."""
        repo_dir = Path("/tmp/repo")

        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "ok"
            mock_result.stderr = ""
            mock_run.return_value = mock_result

            with patch("auto_slopp.utils.github_operations.settings") as mock_settings:
                mock_env_file = MagicMock()
                mock_env_file.exists.return_value = True
                mock_settings.additional_env_file = mock_env_file

                with patch("auto_slopp.utils.github_operations.dotenv_values") as mock_dotenv:
                    mock_dotenv.return_value = {
                        "KEY1": "value1",
                        "KEY2": None,
                        "KEY3": "value3",
                    }

                    from auto_slopp.utils.github_operations import _run_gh_command

                    _run_gh_command(repo_dir, "issue", "list")

                    call_kwargs = mock_run.call_args.kwargs
                    env = call_kwargs["env"]
                    assert env["KEY1"] == "value1"

    def test_run_gh_command_gh_token_fallback(self):
        """Test GH_TOKEN fallback when GITHUB_TOKEN is set."""
        repo_dir = Path("/tmp/repo")

        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "ok"
            mock_result.stderr = ""
            mock_run.return_value = mock_result

            with patch.dict("os.environ", {"GITHUB_TOKEN": "token123"}, clear=False):
                with patch("auto_slopp.utils.github_operations.settings") as mock_settings:
                    mock_settings.additional_env_file = None

                    from auto_slopp.utils.github_operations import _run_gh_command

                    _run_gh_command(repo_dir, "issue", "list")

                    call_kwargs = mock_run.call_args.kwargs
                    env = call_kwargs["env"]
                    assert env["GH_TOKEN"] == "token123"

    def test_run_gh_command_timeout_error(self):
        """Test _run_gh_command handles TimeoutExpired."""
        repo_dir = Path("/tmp/repo")

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired(cmd=["gh"], timeout=30)

            with patch("auto_slopp.utils.github_operations.settings") as mock_settings:
                mock_settings.additional_env_file = None

                from auto_slopp.utils.github_operations import (
                    GitHubOperationError,
                    _run_gh_command,
                )

                with pytest.raises(GitHubOperationError) as exc_info:
                    _run_gh_command(repo_dir, "issue", "list")
                assert "timed out" in str(exc_info.value)

    def test_run_gh_command_timeout_error_generic(self):
        """Test _run_gh_command handles generic TimeoutError."""
        repo_dir = Path("/tmp/repo")

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = TimeoutError("Timeout")

            with patch("auto_slopp.utils.github_operations.settings") as mock_settings:
                mock_settings.additional_env_file = None

                from auto_slopp.utils.github_operations import (
                    GitHubOperationError,
                    _run_gh_command,
                )

                with pytest.raises(GitHubOperationError) as exc_info:
                    _run_gh_command(repo_dir, "issue", "list")
                assert "timed out" in str(exc_info.value)

    def test_run_gh_command_called_process_error(self):
        """Test _run_gh_command handles CalledProcessError (lines 72-75)."""
        repo_dir = Path("/tmp/repo")

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(
                returncode=1,
                cmd=["gh", "issue", "list"],
                stderr="Command failed",
            )

            with patch("auto_slopp.utils.github_operations.settings") as mock_settings:
                mock_settings.additional_env_file = None

                from auto_slopp.utils.github_operations import (
                    GitHubOperationError,
                    _run_gh_command,
                )

                with pytest.raises(GitHubOperationError) as exc_info:
                    _run_gh_command(repo_dir, "issue", "list")
                assert "Command failed" in str(exc_info.value)
