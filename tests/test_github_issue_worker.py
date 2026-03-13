"""Tests for GitHubIssueWorker."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from auto_slopp.utils.task_executor import ExecutionStep, IssueTracker, StepStatus
from auto_slopp.workers.github_issue_worker import GitHubIssueWorker


class TestIssueTracker:
    """Tests for IssueTracker class."""

    def test_issue_tracker_creation(self):
        """Test creating a new issue tracker."""
        tracker = IssueTracker(
            issue_number=123,
            issue_title="Test Issue",
            branch_name="ai/issue-123-test-issue",
            max_iterations=3,
        )

        assert tracker.issue_number == 123
        assert tracker.issue_title == "Test Issue"
        assert tracker.branch_name == "ai/issue-123-test-issue"
        assert tracker.max_iterations == 3
        assert tracker.iteration == 0
        assert len(tracker.errors) == 0

    def test_issue_tracker_mark_step(self):
        """Test marking steps in issue tracker."""
        tracker = IssueTracker(
            issue_number=1,
            issue_title="Test",
            branch_name="ai/issue-1-test",
        )

        tracker.mark_step(ExecutionStep.FETCH, StepStatus.COMPLETED)
        assert tracker.get_step_status(ExecutionStep.FETCH) == StepStatus.COMPLETED
        assert tracker.is_step_completed(ExecutionStep.FETCH)

    def test_issue_tracker_add_error(self):
        """Test adding errors to tracker."""
        tracker = IssueTracker(
            issue_number=1,
            issue_title="Test",
            branch_name="ai/issue-1-test",
        )

        tracker.add_error("Test error")
        assert len(tracker.errors) == 1
        assert tracker.errors[0] == "Test error"

    def test_issue_tracker_iteration(self):
        """Test iteration counter."""
        tracker = IssueTracker(
            issue_number=1,
            issue_title="Test",
            branch_name="ai/issue-1-test",
            max_iterations=2,
        )

        assert tracker.can_retry() is True
        tracker.increment_iteration()
        assert tracker.iteration == 1
        assert tracker.can_retry() is True
        tracker.increment_iteration()
        assert tracker.iteration == 2
        assert tracker.can_retry() is False

    def test_issue_tracker_to_markdown(self):
        """Test converting tracker to markdown."""
        tracker = IssueTracker(
            issue_number=42,
            issue_title="Fix Bug",
            branch_name="ai/issue-42-fix-bug",
            max_iterations=3,
        )

        tracker.mark_step(ExecutionStep.FETCH, StepStatus.COMPLETED)
        tracker.mark_step(ExecutionStep.VALIDATE, StepStatus.COMPLETED)

        markdown = tracker.to_markdown()

        assert IssueTracker.TRACKER_MARKER in markdown
        assert "Issue #42" in markdown
        assert "Fix Bug" in markdown
        assert "ai/issue-42-fix-bug" in markdown
        assert "FETCH" in markdown
        assert "completed" in markdown

    def test_issue_tracker_from_markdown(self):
        """Test parsing tracker from markdown."""
        markdown = f"""{IssueTracker.TRACKER_MARKER}
# Implementation Tracker: Issue #42

**Issue**: ai/issue-42-fix-bug
**Title**: Fix Bug
**Created**: 2024-01-01T00:00:00
**Updated**: 2024-01-01T00:00:00
**Iteration**: 1/3

## Execution Steps

- ✅ **FETCH**: completed
- ✅ **VALIDATE**: completed
- 🔄 **PREPARE**: in_progress

{IssueTracker.TRACKER_MARKER}"""

        tracker = IssueTracker.from_markdown(markdown)

        assert tracker is not None
        assert tracker.issue_number == 42
        assert tracker.issue_title == "Fix Bug"
        assert tracker.branch_name == "ai/issue-42-fix-bug"
        assert tracker.iteration == 1
        assert tracker.max_iterations == 3
        assert tracker.get_step_status(ExecutionStep.FETCH) == StepStatus.COMPLETED
        assert tracker.get_step_status(ExecutionStep.VALIDATE) == StepStatus.COMPLETED
        assert tracker.get_step_status(ExecutionStep.PREPARE) == StepStatus.IN_PROGRESS

    def test_issue_tracker_from_markdown_invalid(self):
        """Test parsing invalid markdown."""
        markdown = "This is not a valid tracker"
        tracker = IssueTracker.from_markdown(markdown)
        assert tracker is None

    def test_issue_tracker_roundtrip(self):
        """Test markdown to tracker to markdown roundtrip."""
        original = IssueTracker(
            issue_number=99,
            issue_title="Roundtrip Test",
            branch_name="ai/issue-99-roundtrip-test",
            max_iterations=5,
        )

        original.mark_step(ExecutionStep.FETCH, StepStatus.COMPLETED)
        original.mark_step(ExecutionStep.EXECUTE, StepStatus.FAILED)
        original.add_error("Test error")
        original.iteration = 2

        markdown = original.to_markdown()
        parsed = IssueTracker.from_markdown(markdown)

        assert parsed is not None
        assert parsed.issue_number == original.issue_number
        assert parsed.issue_title == original.issue_title
        assert parsed.branch_name == original.branch_name
        assert parsed.iteration == original.iteration
        assert parsed.max_iterations == original.max_iterations
        assert parsed.get_step_status(ExecutionStep.FETCH) == StepStatus.COMPLETED
        assert parsed.get_step_status(ExecutionStep.EXECUTE) == StepStatus.FAILED
        assert len(parsed.errors) == 1


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
                "author": {"login": "MelvinKl"},
                "labels": [{"name": "ai"}],
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
                "author": {"login": "MelvinKl"},
                "labels": [{"name": "ai"}],
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

                worker = GitHubIssueWorker(dry_run=False, verify_tests=False)
                result = worker.run(repo_path)

                assert result["success"] is True
                assert result["issues_processed"] == 1
                assert result["issue_results"][0]["issue_number"] == 1

    def test_branch_name_sanitization(self):
        """Test that branch names are properly sanitized from issue titles."""
        worker = GitHubIssueWorker(dry_run=True)

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / "repos" / "test_repo"
            repo_path.mkdir(parents=True)

            test_cases = [
                {"title": "Fix bug", "expected": "ai/issue-1-fix-bug"},
                {"title": "Fix: bug", "expected": "ai/issue-2-fix-bug"},
                {
                    "title": "Feature: Add new functionality",
                    "expected": "ai/issue-3-feature-add-new-functio",
                },
                {
                    "title": "Issue with:colon",
                    "expected": "ai/issue-4-issue-with-colon",
                },
                {
                    "title": "Issue with?question",
                    "expected": "ai/issue-5-issue-with-question",
                },
                {
                    "title": "Issue with*asterisk",
                    "expected": "ai/issue-6-issue-with-asterisk",
                },
                {
                    "title": "Issue with[brackets]",
                    "expected": "ai/issue-7-issue-with-brackets",
                },
                {
                    "title": "Issue\\with\\backslash",
                    "expected": "ai/issue-8-issue-with-backslash",
                },
                {
                    "title": "  Issue with spaces  ",
                    "expected": "ai/issue-9-issue-with-spaces",
                },
                {
                    "title": "Issue---with---dashes",
                    "expected": "ai/issue-10-issue-with-dashes",
                },
            ]

            for i, test_case in enumerate(test_cases, start=1):
                issue = {
                    "number": i,
                    "title": test_case["title"],
                    "body": "Test body",
                    "url": f"https://github.com/test/repo/issues/{i}",
                    "author": {"login": "MelvinKl"},
                    "labels": [{"name": "ai"}],
                }

                with patch("auto_slopp.workers.github_issue_worker.get_open_issues") as mock_issues:
                    mock_issues.return_value = [issue]

                    result = worker.run(repo_path)

                    assert result["success"] is True
                    assert result["issues_processed"] == 1

                    from auto_slopp.utils.git_operations import sanitize_branch_name

                    sanitized_title = sanitize_branch_name(test_case["title"][:30].lower())
                    expected_branch = f"ai/issue-{i}-{sanitized_title}"

                    assert result["issue_results"][0]["issue_title"] == test_case["title"]

    def test_should_process_issue_with_required_label(self):
        """Test that issues with required label from allowed creator are processed."""
        from unittest.mock import patch

        with patch("auto_slopp.workers.github_issue_worker.settings") as mock_settings:
            mock_settings.github_issue_worker_required_label = "ai"
            mock_settings.github_issue_worker_allowed_creator = "MelvinKl"

            worker = GitHubIssueWorker(dry_run=True)

            issue_with_label = {
                "number": 1,
                "title": "AI Task",
                "author": {"login": "MelvinKl"},
                "labels": [{"name": "ai"}],
            }

            assert worker._should_process_issue(issue_with_label) is True

    def test_should_process_issue_with_allowed_creator(self):
        """Test that issues without 'ai' label are skipped even if from allowed creator."""
        from unittest.mock import patch

        with patch("auto_slopp.workers.github_issue_worker.settings") as mock_settings:
            mock_settings.github_issue_worker_required_label = "ai"
            mock_settings.github_issue_worker_allowed_creator = "MelvinKl"

            worker = GitHubIssueWorker(dry_run=True)

            issue_from_allowed_creator = {
                "number": 2,
                "title": "Regular Task",
                "author": {"login": "MelvinKl"},
                "labels": [{"name": "bug"}],
            }

            assert worker._should_process_issue(issue_from_allowed_creator) is False

    def test_should_process_issue_without_label_and_not_allowed_creator(self):
        """Test that issues without required label and not from allowed creator are skipped."""
        from unittest.mock import patch

        with patch("auto_slopp.workers.github_issue_worker.settings") as mock_settings:
            mock_settings.github_issue_worker_required_label = "ai"
            mock_settings.github_issue_worker_allowed_creator = "MelvinKl"

            worker = GitHubIssueWorker(dry_run=True)

            issue_without_label = {
                "number": 3,
                "title": "Regular Task",
                "author": {"login": "other_user"},
                "labels": [{"name": "bug"}],
            }

            assert worker._should_process_issue(issue_without_label) is False

    def test_should_process_issue_with_both_label_and_allowed_creator(self):
        """Test that issues with both label and allowed creator are processed."""
        from unittest.mock import patch

        with patch("auto_slopp.workers.github_issue_worker.settings") as mock_settings:
            mock_settings.github_issue_worker_required_label = "ai"
            mock_settings.github_issue_worker_allowed_creator = "MelvinKl"

            worker = GitHubIssueWorker(dry_run=True)

            issue_with_both = {
                "number": 4,
                "title": "AI Task",
                "author": {"login": "MelvinKl"},
                "labels": [{"name": "ai"}],
            }

            assert worker._should_process_issue(issue_with_both) is True

    def test_filter_by_label_and_creator(self):
        """Test filtering issues by label and creator."""
        from unittest.mock import patch

        with patch("auto_slopp.workers.github_issue_worker.settings") as mock_settings:
            mock_settings.github_issue_worker_required_label = "ai"
            mock_settings.github_issue_worker_allowed_creator = "MelvinKl"

            worker = GitHubIssueWorker(dry_run=True)

            issues = [
                {
                    "number": 1,
                    "title": "AI Task",
                    "author": {"login": "other_user"},
                    "labels": [{"name": "ai"}],
                },
                {
                    "number": 2,
                    "title": "MelvinKl Task",
                    "author": {"login": "MelvinKl"},
                    "labels": [{"name": "bug"}],
                },
                {
                    "number": 3,
                    "title": "Other Task",
                    "author": {"login": "other_user"},
                    "labels": [{"name": "bug"}],
                },
                {
                    "number": 4,
                    "title": "AI Task by MelvinKl",
                    "author": {"login": "MelvinKl"},
                    "labels": [{"name": "ai"}],
                },
            ]

            filtered = worker._filter_by_label_and_creator(issues)

            assert len(filtered) == 1
            assert filtered[0]["number"] == 4

    def test_should_process_issue_case_insensitive_label(self):
        """Test that label check is case-insensitive."""
        from unittest.mock import patch

        with patch("auto_slopp.workers.github_issue_worker.settings") as mock_settings:
            mock_settings.github_issue_worker_required_label = "ai"
            mock_settings.github_issue_worker_allowed_creator = "MelvinKl"

            worker = GitHubIssueWorker(dry_run=True)

            test_cases = [
                {"label": "ai", "expected": True},
                {"label": "AI", "expected": True},
                {"label": "Ai", "expected": True},
                {"label": "aI", "expected": True},
                {"label": "bug", "expected": False},
            ]

            for test_case in test_cases:
                issue = {
                    "number": 1,
                    "title": "Test Issue",
                    "author": {"login": "MelvinKl"},
                    "labels": [{"name": test_case["label"]}],
                }

                result = worker._should_process_issue(issue)
                assert result == test_case["expected"], f"Failed for label '{test_case['label']}'"

    def test_run_filters_issues_by_label_and_creator(self):
        """Test that run method filters issues by label and creator."""
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / "repos" / "test_repo"
            repo_path.mkdir(parents=True)

            issues = [
                {
                    "number": 1,
                    "title": "AI Task",
                    "author": {"login": "MelvinKl"},
                    "labels": [{"name": "ai"}],
                    "url": "https://github.com/test/repo/issues/1",
                },
                {
                    "number": 2,
                    "title": "Other Task",
                    "author": {"login": "other_user"},
                    "labels": [{"name": "bug"}],
                    "url": "https://github.com/test/repo/issues/2",
                },
            ]

            with (
                patch("auto_slopp.workers.github_issue_worker.settings") as mock_settings,
                patch("auto_slopp.workers.github_issue_worker.get_open_issues") as mock_issues,
            ):
                mock_settings.github_issue_worker_required_label = "ai"
                mock_settings.github_issue_worker_allowed_creator = "MelvinKl"
                mock_issues.return_value = issues

                worker = GitHubIssueWorker(dry_run=True)
                result = worker.run(repo_path)

                assert result["success"] is True
                assert result["issues_processed"] == 1
                assert result["issue_results"][0]["issue_number"] == 1

    def test_run_ignores_comments_not_from_issue_author(self):
        """Test that only issue-author comments are included in instructions."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / "repos" / "test_repo"
            repo_path.mkdir(parents=True)

            issue = {
                "number": 1,
                "title": "Test issue",
                "body": "Issue body",
                "url": "https://github.com/test/repo/issues/1",
                "author": {"login": "MelvinKl"},
                "labels": [{"name": "ai"}],
            }

            with (
                patch("auto_slopp.workers.github_issue_worker.get_open_issues") as mock_issues,
                patch("auto_slopp.workers.github_issue_worker.get_issue_comments") as mock_comments,
                patch.object(GitHubIssueWorker, "_build_instructions") as mock_build_instructions,
            ):
                mock_issues.return_value = [issue]
                mock_comments.return_value = [
                    {"body": "Author comment", "author": "MelvinKl"},
                    {"body": "Other user comment", "author": "other-user"},
                    {"body": "Bot comment", "author": "some-bot"},
                ]
                mock_build_instructions.return_value = "instructions"

                worker = GitHubIssueWorker(dry_run=True)
                result = worker.run(repo_path)

                assert result["success"] is True
                assert result["issues_processed"] == 1

                call_args = mock_build_instructions.call_args
                assert call_args.args[0] == "Test issue"
                assert call_args.args[1] == "Issue body"
                assert call_args.args[2] == ["Author comment"]
