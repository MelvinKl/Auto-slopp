"""Tests for GitHubTaskSource."""

from pathlib import Path
from unittest.mock import patch

from auto_slopp.workers.github_task_source import GitHubTaskSource
from auto_slopp.workers.task_source import Task


class TestGitHubTaskSource:
    """Tests for GitHubTaskSource."""

    @patch("auto_slopp.workers.github_task_source.get_open_issues")
    @patch("auto_slopp.workers.github_task_source.get_issue_comments")
    @patch("auto_slopp.workers.github_task_source.settings")
    def test_get_tasks_filters_renovate_issues_by_author(self, mock_settings, mock_get_comments, mock_get_issues):
        """Test that get_tasks filters out renovate issues by author login."""
        mock_settings.github_issue_worker_required_label = "test-label"
        mock_settings.github_issue_worker_allowed_creator = "test-user"

        mock_issues = [
            {
                "number": 1,
                "title": "Test Issue 1",
                "author": {"login": "renovate[bot]"},
                "labels": [{"name": "test-label"}],
            },
            {
                "number": 2,
                "title": "Test Issue 2",
                "author": {"login": "test-user"},
                "labels": [{"name": "test-label"}],
            },
        ]
        mock_get_issues.return_value = mock_issues
        mock_get_comments.return_value = []

        task_source = GitHubTaskSource()
        tasks = task_source.get_tasks(Path("/test"))

        assert len(tasks) == 1
        assert tasks[0].id == 2

    @patch("auto_slopp.workers.github_task_source.get_open_issues")
    @patch("auto_slopp.workers.github_task_source.get_issue_comments")
    @patch("auto_slopp.workers.github_task_source.settings")
    def test_get_tasks_filters_renovate_issues_by_label(self, mock_settings, mock_get_comments, mock_get_issues):
        """Test that get_tasks filters out renovate issues by label."""
        mock_settings.github_issue_worker_required_label = "test-label"
        mock_settings.github_issue_worker_allowed_creator = "test-user"

        mock_issues = [
            {
                "number": 1,
                "title": "Test Issue 1",
                "author": {"login": "test-user"},
                "labels": [{"name": "renovate"}],
            },
            {
                "number": 2,
                "title": "Test Issue 2",
                "author": {"login": "test-user"},
                "labels": [{"name": "test-label"}],
            },
        ]
        mock_get_issues.return_value = mock_issues
        mock_get_comments.return_value = []

        task_source = GitHubTaskSource()
        tasks = task_source.get_tasks(Path("/test"))

        assert len(tasks) == 1
        assert tasks[0].id == 2

    @patch("auto_slopp.workers.github_task_source.get_open_issues")
    @patch("auto_slopp.workers.github_task_source.get_issue_comments")
    @patch("auto_slopp.workers.github_task_source.settings")
    def test_get_tasks_filters_by_label_and_creator(self, mock_settings, mock_get_comments, mock_get_issues):
        """Test that get_tasks filters by required label and allowed creator."""
        mock_settings.github_issue_worker_required_label = "test-label"
        mock_settings.github_issue_worker_allowed_creator = "test-user"

        mock_issues = [
            {
                "number": 1,
                "title": "Test Issue 1",
                "author": {"login": "test-user"},
                "labels": [{"name": "test-label"}],
            },
            {
                "number": 2,
                "title": "Test Issue 2",
                "author": {"login": "other-user"},
                "labels": [{"name": "test-label"}],
            },
            {
                "number": 3,
                "title": "Test Issue 3",
                "author": {"login": "test-user"},
                "labels": [{"name": "other-label"}],
            },
        ]
        mock_get_issues.return_value = mock_issues
        mock_get_comments.return_value = []

        task_source = GitHubTaskSource()
        tasks = task_source.get_tasks(Path("/test"))

        assert len(tasks) == 1
        assert tasks[0].id == 1

    @patch("auto_slopp.workers.github_task_source.get_open_issues")
    @patch("auto_slopp.workers.github_task_source.get_issue_comments")
    @patch("auto_slopp.workers.github_task_source.settings")
    def test_get_tasks_filters_label_case_insensitive(self, mock_settings, mock_get_comments, mock_get_issues):
        """Test that label filtering is case-insensitive."""
        mock_settings.github_issue_worker_required_label = "TEST-LABEL"
        mock_settings.github_issue_worker_allowed_creator = "test-user"

        mock_issues = [
            {
                "number": 1,
                "title": "Test Issue 1",
                "author": {"login": "test-user"},
                "labels": [{"name": "test-label"}],
            },
        ]
        mock_get_issues.return_value = mock_issues
        mock_get_comments.return_value = []

        task_source = GitHubTaskSource()
        tasks = task_source.get_tasks(Path("/test"))

        assert len(tasks) == 1

    @patch("auto_slopp.workers.github_task_source.get_open_issues")
    @patch("auto_slopp.workers.github_task_source.get_issue_comments")
    @patch("auto_slopp.workers.github_task_source.settings")
    def test_get_tasks_sorts_by_number_ascending(self, mock_settings, mock_get_comments, mock_get_issues):
        """Test that get_tasks sorts issues by number ascending."""
        mock_settings.github_issue_worker_required_label = "test-label"
        mock_settings.github_issue_worker_allowed_creator = "test-user"

        mock_issues = [
            {
                "number": 3,
                "title": "Test Issue 3",
                "author": {"login": "test-user"},
                "labels": [{"name": "test-label"}],
            },
            {
                "number": 1,
                "title": "Test Issue 1",
                "author": {"login": "test-user"},
                "labels": [{"name": "test-label"}],
            },
            {
                "number": 2,
                "title": "Test Issue 2",
                "author": {"login": "test-user"},
                "labels": [{"name": "test-label"}],
            },
        ]
        mock_get_issues.return_value = mock_issues
        mock_get_comments.return_value = []

        task_source = GitHubTaskSource()
        tasks = task_source.get_tasks(Path("/test"))

        assert len(tasks) == 3
        assert tasks[0].id == 1
        assert tasks[1].id == 2
        assert tasks[2].id == 3

    @patch("auto_slopp.workers.github_task_source.get_open_issues")
    @patch("auto_slopp.workers.github_task_source.get_issue_comments")
    @patch("auto_slopp.workers.github_task_source.settings")
    def test_get_tasks_constructs_task_objects(self, mock_settings, mock_get_comments, mock_get_issues):
        """Test that get_tasks constructs Task dataclass objects correctly."""
        mock_settings.github_issue_worker_required_label = "test-label"
        mock_settings.github_issue_worker_allowed_creator = "test-user"

        mock_issues = [
            {
                "number": 1,
                "title": "Test Issue",
                "body": "Test Body",
                "author": {"login": "test-user"},
                "labels": [{"name": "test-label"}],
            }
        ]
        mock_get_issues.return_value = mock_issues
        mock_get_comments.return_value = []

        task_source = GitHubTaskSource()
        tasks = task_source.get_tasks(Path("/test"))

        assert len(tasks) == 1
        task = tasks[0]
        assert task.id == 1
        assert task.title == "Test Issue"
        assert task.body == "Test Body"
        assert task.comments == []
        assert task.raw is not None
        assert task.raw.get("_repo_path") == Path("/test")

    @patch("auto_slopp.workers.github_task_source.get_open_issues")
    @patch("auto_slopp.workers.github_task_source.get_issue_comments")
    @patch("auto_slopp.workers.github_task_source.settings")
    def test_get_tasks_filters_comments_by_author(self, mock_settings, mock_get_comments, mock_get_issues):
        """Test that only author's comments are included in task comments."""
        mock_settings.github_issue_worker_required_label = "test-label"
        mock_settings.github_issue_worker_allowed_creator = "test-user"

        mock_issues = [
            {
                "number": 1,
                "title": "Test Issue",
                "body": "Test Body",
                "author": {"login": "test-user"},
                "labels": [{"name": "test-label"}],
            }
        ]
        mock_get_issues.return_value = mock_issues
        mock_get_comments.return_value = [
            {"author": "test-user", "body": "Author comment"},
            {"author": "other-user", "body": "Other comment"},
        ]

        task_source = GitHubTaskSource()
        tasks = task_source.get_tasks(Path("/test"))

        assert len(tasks) == 1
        task = tasks[0]
        assert len(task.comments) == 1
        assert task.comments[0] == "Author comment"

    @patch("auto_slopp.workers.github_task_source.get_open_issues")
    def test_get_tasks_returns_empty_on_no_issues(self, mock_get_issues):
        """Test that get_tasks returns empty list when no issues found."""
        mock_get_issues.return_value = []

        task_source = GitHubTaskSource()
        tasks = task_source.get_tasks(Path("/test"))

        assert tasks == []

    def test_get_branch_name(self):
        """Test that get_branch_name returns correct format."""
        task_source = GitHubTaskSource()
        task = Task(id=42, title="Test Issue Title", body="", comments=[], raw={})

        branch_name = task_source.get_branch_name(task)

        assert branch_name == "ai/issue-42-test-issue-title"

    def test_get_ralph_file_prefix(self):
        """Test that get_ralph_file_prefix returns 'github'."""
        task_source = GitHubTaskSource()

        assert task_source.get_ralph_file_prefix() == "github"

    def test_get_default_pr_body(self):
        """Test that get_default_pr_body returns correct format."""
        task_source = GitHubTaskSource()
        task = Task(id=42, title="Test Issue", body="Test Body", comments=[], raw={})

        pr_body = task_source.get_default_pr_body(task)

        assert pr_body == "Closes #42\n\nTest Body"

    @patch("auto_slopp.workers.github_task_source.settings")
    def test_on_task_start_is_noop(self, mock_settings):
        """Test that on_task_start is a no-op."""
        mock_settings.github_issue_worker_required_label = "test-label"
        task_source = GitHubTaskSource()
        task = Task(id=42, title="Test", body="", comments=[], raw={})

        result = task_source.on_task_start(task, "ai/issue-42-test")

        assert result is None

    @patch("auto_slopp.workers.github_task_source.close_issue")
    @patch("auto_slopp.workers.github_task_source.comment_on_issue")
    def test_on_task_complete_closes_issue_and_comments(self, mock_comment, mock_close):
        """Test that on_task_complete closes issue and adds comment."""
        mock_close.return_value = True
        task_source = GitHubTaskSource()
        task = Task(id=42, title="Test", body="", comments=[], raw={"_repo_path": Path("/test")})

        task_source.on_task_complete(task, "ai/issue-42-test", "https://github.com/test/pr/1")

        mock_close.assert_called_once_with(Path("/test"), 42)
        mock_comment.assert_called_once_with(Path("/test"), 42, "Completed by PR: https://github.com/test/pr/1")

    @patch("auto_slopp.workers.github_task_source.close_issue")
    @patch("auto_slopp.workers.github_task_source.comment_on_issue")
    def test_on_task_complete_handles_missing_repo_path(self, mock_comment, mock_close):
        """Test that on_task_complete handles missing repo_path in task."""
        task_source = GitHubTaskSource()
        task = Task(id=42, title="Test", body="", comments=[], raw={})

        task_source.on_task_complete(task, "ai/issue-42-test", "https://github.com/test/pr/1")

        mock_close.assert_not_called()
        mock_comment.assert_not_called()

    @patch("auto_slopp.workers.github_task_source.settings")
    def test_on_task_failure_is_noop(self, mock_settings):
        """Test that on_task_failure is a no-op."""
        mock_settings.github_issue_worker_required_label = "test-label"
        task_source = GitHubTaskSource()
        task = Task(id=42, title="Test", body="", comments=[], raw={})

        result = task_source.on_task_failure(task, "Test error")

        assert result is None

    @patch("auto_slopp.workers.github_task_source.comment_on_issue")
    @patch("auto_slopp.workers.github_task_source.close_issue")
    def test_on_no_changes_comments_and_closes_issue(self, mock_close, mock_comment):
        """Test that on_no_changes adds comment and closes issue."""
        task_source = GitHubTaskSource()
        task = Task(id=42, title="Test", body="", comments=[], raw={"_repo_path": Path("/test")})

        task_source.on_no_changes(task)

        mock_comment.assert_called_once()
        mock_close.assert_called_once_with(Path("/test"), 42)

    @patch("auto_slopp.workers.github_task_source.comment_on_issue")
    @patch("auto_slopp.workers.github_task_source.remove_label_from_issue")
    @patch("auto_slopp.workers.github_task_source.settings")
    def test_on_max_iterations_reached_comments_and_removes_label(self, mock_settings, mock_remove, mock_comment):
        """Test that on_max_iterations_reached adds comment and removes label."""
        mock_settings.github_issue_worker_required_label = "test-label"
        mock_remove.return_value = True
        task_source = GitHubTaskSource()
        task = Task(id=42, title="Test", body="", comments=[], raw={"_repo_path": Path("/test")})

        task_source.on_max_iterations_reached(task, 8, 15, "Max iterations reached")

        mock_comment.assert_called_once()
        mock_remove.assert_called_once_with(Path("/test"), 42, "test-label")

    @patch("auto_slopp.workers.github_task_source.comment_on_issue")
    @patch("auto_slopp.workers.github_task_source.remove_label_from_issue")
    @patch("auto_slopp.workers.github_task_source.settings")
    def test_on_max_iterations_reached_handles_missing_repo_path(self, mock_settings, mock_remove, mock_comment):
        """Test that on_max_iterations_reached handles missing repo_path in task."""
        mock_settings.github_issue_worker_required_label = "test-label"
        task_source = GitHubTaskSource()
        task = Task(id=42, title="Test", body="", comments=[], raw={})

        task_source.on_max_iterations_reached(task, 8, 15, "Max iterations reached")

        mock_comment.assert_not_called()
        mock_remove.assert_not_called()
