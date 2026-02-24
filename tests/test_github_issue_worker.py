"""Tests for GitHubIssueWorker."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from auto_slopp.workers.github_issue_worker import GitHubIssueWorker


class TestGitHubIssueWorker:
    """Tests for GitHubIssueWorker."""

    def test_initialization_success(self):
        """Test successful worker initialization."""
        worker = GitHubIssueWorker(
            timeout=7200,
            agent_args=["--verbose"],
            dry_run=True,
        )

        assert worker.timeout == 7200
        assert worker.agent_args == ["--verbose"]
        assert worker.dry_run is True

    def test_run_with_no_issues(self):
        """Test run with no open issues."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / "repos" / "test_repo"
            repo_path.mkdir(parents=True)

            with patch("auto_slopp.workers.github_issue_worker.get_open_issues") as mock_issues:
                mock_issues.return_value = []

                worker = GitHubIssueWorker(dry_run=True)
                result = worker.run(repo_path)

                assert result["success"] is True
                assert result["repositories_processed"] == 1
                assert result["repositories_with_errors"] == 0
                assert result["issues_processed"] == 0

    def test_run_with_issues_dry_run(self):
        """Test run with open issues in dry run mode."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / "repos" / "test_repo"
            repo_path.mkdir(parents=True)

            mock_issue = {
                "number": 1,
                "title": "Test Issue",
                "body": "This is a test issue",
                "url": "https://github.com/test/repo/issues/1",
            }

            with patch("auto_slopp.workers.github_issue_worker.get_open_issues") as mock_issues:
                mock_issues.return_value = [mock_issue]

                worker = GitHubIssueWorker(dry_run=True)
                result = worker.run(repo_path)

                assert result["success"] is True
                assert result["repositories_processed"] == 1
                assert result["issues_processed"] == 1
                assert result["issue_results"][0]["issue_number"] == 1
                assert result["issue_results"][0]["issue_title"] == "Test Issue"

    def test_run_with_nonexistent_repo(self):
        """Test run with nonexistent repository path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / "nonexistent_repo"

            worker = GitHubIssueWorker(dry_run=True)
            result = worker.run(repo_path)

            assert result["success"] is False
            assert "error" in result

    def test_build_instructions(self):
        """Test instruction building."""
        worker = GitHubIssueWorker(dry_run=True)

        instructions = worker._build_instructions("Fix bug", "This is a bug")
        assert "Fix bug" in instructions
        assert "This is a bug" in instructions
        assert "ai/" in instructions

    def test_build_instructions_with_branch_name(self):
        """Test instruction building with branch name provided."""
        worker = GitHubIssueWorker(dry_run=True)

        instructions = worker._build_instructions("Fix bug", "This is a bug", branch_name="ai/issue-1-fix-bug")
        assert "Fix bug" in instructions
        assert "This is a bug" in instructions
        assert "already on branch 'ai/issue-1-fix-bug'" in instructions
        assert "Create a new branch" not in instructions

    def test_build_instructions_empty_body(self):
        """Test instruction building with empty body."""
        worker = GitHubIssueWorker(dry_run=True)

        instructions = worker._build_instructions("Test issue", "")
        assert "Test issue" in instructions
        assert "ai/" in instructions

    def test_create_error_result(self):
        """Test error result creation."""
        worker = GitHubIssueWorker(dry_run=True)
        start_time = 1000.0

        result = worker._create_error_result(
            start_time,
            Path("/test/repo"),
            "Test error",
        )

        assert result["success"] is False
        assert result["error"] == "Test error"
        assert result["worker_name"] == "GitHubIssueWorker"

    def test_run_with_no_changes(self):
        """Test run when no changes are made - should close issue with comment."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / "repos" / "test_repo"
            repo_path.mkdir(parents=True)

            mock_issue = {
                "number": 1,
                "title": "Test Issue",
                "body": "This is a test issue",
                "url": "https://github.com/test/repo/issues/1",
            }

            with (
                patch("auto_slopp.workers.github_issue_worker.get_open_issues") as mock_issues,
                patch("auto_slopp.workers.github_issue_worker.create_and_checkout_branch") as mock_create_branch,
                patch("auto_slopp.workers.github_issue_worker.execute_with_instructions") as mock_execute,
                patch("auto_slopp.workers.github_issue_worker.get_current_branch") as mock_get_branch,
                patch("auto_slopp.workers.github_issue_worker.comment_on_issue") as mock_comment,
                patch("auto_slopp.workers.github_issue_worker.close_issue") as mock_close,
                patch("auto_slopp.workers.github_issue_worker.delete_branch") as mock_delete,
                patch("auto_slopp.workers.github_issue_worker.checkout_branch_resilient") as mock_checkout,
            ):
                mock_issues.return_value = [mock_issue]
                mock_create_branch.return_value = True
                mock_execute.return_value = {"success": True}
                mock_get_branch.return_value = "main"
                mock_comment.return_value = True
                mock_close.return_value = True
                mock_delete.return_value = True
                mock_checkout.return_value = True

                worker = GitHubIssueWorker(dry_run=False)
                result = worker.run(repo_path)

                assert result["success"] is True
                assert result["issues_processed"] == 1
                assert result["issues_closed"] == 1
                assert result["issue_results"][0]["no_changes"] is True
                assert result["issue_results"][0]["issue_closed"] is True
                assert result["issue_results"][0]["issue_commented"] is True

                mock_close.assert_called_once()
                mock_comment.assert_called_once()
                mock_delete.assert_called_once()
