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
    @patch("auto_slopp.workers.github_task_source.execute_with_instructions")
    @patch("auto_slopp.workers.github_task_source.settings")
    def test_get_tasks_condenses_author_comments(self, mock_settings, mock_execute, mock_get_comments, mock_get_issues):
        """Test that comments from issue author/allowed creator are condensed."""
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
        # Multiple comments from allowed creator + one from other user (should be ignored)
        mock_get_comments.return_value = [
            {"author": "test-user", "body": "Author comment 1", "databaseId": 1},
            {"author": "test-user", "body": "Author comment 2", "databaseId": 2},
            {"author": "other-user", "body": "Other comment", "databaseId": 3},
        ]
        mock_execute.return_value = {"stdout": "Condensed summary", "success": True}

        task_source = GitHubTaskSource()
        tasks = task_source.get_tasks(Path("/test"))

        assert len(tasks) == 1
        task = tasks[0]
        assert len(task.comments) == 1
        assert task.comments[0] == "Condensed summary"
        mock_execute.assert_called_once()

    @patch("auto_slopp.workers.github_task_source.get_open_issues")
    @patch("auto_slopp.workers.github_task_source.get_issue_comments")
    @patch("auto_slopp.workers.github_task_source.settings")
    def test_get_tasks_single_comment_no_condensing(self, mock_settings, mock_get_comments, mock_get_issues):
        """Test that a single comment is returned as-is without condensing."""
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
            {"author": "test-user", "body": "Single comment", "databaseId": 1},
        ]

        task_source = GitHubTaskSource()
        tasks = task_source.get_tasks(Path("/test"))

        assert len(tasks) == 1
        task = tasks[0]
        assert len(task.comments) == 1
        assert task.comments[0] == "Single comment"

    @patch("auto_slopp.workers.github_task_source.get_open_issues")
    @patch("auto_slopp.workers.github_task_source.get_issue_comments")
    @patch("auto_slopp.workers.github_task_source.execute_with_instructions")
    @patch("auto_slopp.workers.github_task_source.settings")
    def test_get_tasks_empty_condensation_fallback(
        self, mock_settings, mock_execute, mock_get_comments, mock_get_issues
    ):
        """Test fallback when condensation produces empty result."""
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
        # Multiple comments from allowed creator + one from other user (should be ignored)
        mock_get_comments.return_value = [
            {"author": "test-user", "body": "Comment 1", "databaseId": 1},
            {"author": "test-user", "body": "Comment 2", "databaseId": 2},
            {"author": "other-user", "body": "Other comment", "databaseId": 3},
        ]
        mock_execute.return_value = {"stdout": "", "success": True}

        task_source = GitHubTaskSource()
        tasks = task_source.get_tasks(Path("/test"))

        assert len(tasks) == 1
        task = tasks[0]
        assert len(task.comments) == 1
        # Only filtered comments (from test-user) should be joined in fallback
        assert task.comments[0] == "Comment 1\n\n---\n\nComment 2"

    @patch("auto_slopp.workers.github_task_source.get_open_issues")
    @patch("auto_slopp.workers.github_task_source.get_issue_comments")
    @patch("auto_slopp.workers.github_task_source.execute_with_instructions")
    @patch("auto_slopp.workers.github_task_source.settings")
    def test_get_tasks_execute_with_instructions_called_with_path(
        self, mock_settings, mock_execute, mock_get_comments, mock_get_issues
    ):
        """Test that execute_with_instructions is called with Path object for work_dir."""
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
        # Multiple comments from allowed creator to trigger condensation
        mock_get_comments.return_value = [
            {"author": "test-user", "body": "Comment 1", "databaseId": 1},
            {"author": "test-user", "body": "Comment 2", "databaseId": 2},
        ]
        mock_execute.return_value = {"stdout": "Condensed summary", "success": True}

        task_source = GitHubTaskSource()
        tasks = task_source.get_tasks(Path("/test"))

        assert len(tasks) == 1
        mock_execute.assert_called_once()
        call_args = mock_execute.call_args
        assert call_args.kwargs["work_dir"] == Path("/test")
        assert isinstance(call_args.kwargs["work_dir"], Path)

    @patch("auto_slopp.workers.github_task_source.delete_issue_comment")
    @patch("auto_slopp.workers.github_task_source.comment_on_issue")
    @patch("auto_slopp.workers.github_task_source.execute_with_instructions")
    @patch("auto_slopp.workers.github_task_source.get_open_issues")
    @patch("auto_slopp.workers.github_task_source.get_issue_comments")
    @patch("auto_slopp.workers.github_task_source.settings")
    def test_condense_comments_posts_summary_and_deletes_filtered_only(
        self, mock_settings, mock_get_comments, mock_get_issues, mock_execute, mock_comment, mock_delete
    ):
        """Test that _condense_comments() posts a summary and deletes only filtered comments."""
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
        # Multiple comments from allowed creator + one from other user
        mock_get_comments.return_value = [
            {"author": "test-user", "body": "Comment 1", "id": "comment-100", "databaseId": 100},
            {"author": "test-user", "body": "Comment 2", "id": "comment-200", "databaseId": 200},
            {"author": "other-user", "body": "Other comment", "id": "comment-300", "databaseId": 300},
        ]
        mock_execute.return_value = {"stdout": "Condensed summary", "success": True}

        task_source = GitHubTaskSource()
        tasks = task_source.get_tasks(Path("/test"))

        assert len(tasks) == 1
        assert tasks[0].comments == ["Condensed summary"]
        # Verify the condensed summary was posted as a new comment
        mock_comment.assert_called_once_with(Path("/test"), 1, "Condensed summary")
        # Verify only filtered comments (from allowed creator) were deleted, not all comments
        assert mock_delete.call_count == 2
        mock_delete.assert_any_call(Path("/test"), 1, 100)
        mock_delete.assert_any_call(Path("/test"), 1, 200)
        # Comment from other-user should NOT be deleted
        assert (Path("/test"), 1, 300) not in [(c[0][0], c[0][1], c[0][2]) for c in mock_delete.call_args_list]

    @patch("auto_slopp.workers.github_task_source.get_open_issues")
    @patch("auto_slopp.workers.github_task_source.get_issue_comments")
    @patch("auto_slopp.workers.github_task_source.settings")
    def test_get_tasks_ignores_comments_from_other_users(self, mock_settings, mock_get_comments, mock_get_issues):
        """Test that comments from non-author/non-allowed users are ignored and not condensed."""
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
        # Only comments from other users - should result in empty comments list
        mock_get_comments.return_value = [
            {"author": "other-user", "body": "Other comment 1", "databaseId": 1},
            {"author": "another-user", "body": "Other comment 2", "databaseId": 2},
        ]

        task_source = GitHubTaskSource()
        tasks = task_source.get_tasks(Path("/test"))

        assert len(tasks) == 1
        task = tasks[0]
        # No relevant comments, so comments should be empty
        assert task.comments == []

    @patch("auto_slopp.workers.github_task_source.get_open_issues")
    @patch("auto_slopp.workers.github_task_source.get_issue_comments")
    @patch("auto_slopp.workers.github_task_source.execute_with_instructions")
    @patch("auto_slopp.workers.github_task_source.settings")
    def test_get_tasks_condenses_only_allowed_creator_comments(
        self, mock_settings, mock_execute, mock_get_comments, mock_get_issues
    ):
        """Test that only comments from issue author or allowed creator are condensed."""
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
        # Comments from issue author (who is also allowed creator) and other users
        mock_get_comments.return_value = [
            {"author": "test-user", "body": "Author comment", "databaseId": 1},
            {"author": "test-user", "body": "Another author comment", "databaseId": 2},
            {"author": "other-user", "body": "Other comment", "databaseId": 3},
        ]
        mock_execute.return_value = {"stdout": "Condensed summary", "success": True}

        task_source = GitHubTaskSource()
        tasks = task_source.get_tasks(Path("/test"))

        assert len(tasks) == 1
        task = tasks[0]
        assert len(task.comments) == 1
        assert task.comments[0] == "Condensed summary"
        mock_execute.assert_called_once()

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

    def test_get_pr_title(self):
        """Test that get_pr_title returns correct format for GitHub issues."""
        task_source = GitHubTaskSource()
        task = Task(id=42, title="Test Issue", body="Test Body", comments=[], raw={})

        pr_title = task_source.get_pr_title(task)

        assert pr_title == "#42: Test Issue"

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

    @patch("auto_slopp.workers.github_task_source.comment_on_issue")
    @patch("auto_slopp.workers.github_task_source.remove_label_from_issue")
    @patch("auto_slopp.workers.github_task_source.settings")
    def test_on_skip_no_comment(self, mock_settings, mock_remove, mock_comment):
        """Test that on_skip posts a GitHub comment but does NOT remove the required label."""
        mock_settings.github_issue_worker_required_label = "test-label"
        task_source = GitHubTaskSource()
        task = Task(id=42, title="Test", body="", comments=[], raw={"_repo_path": Path("/test")})

        task_source.on_skip(task, "LLM unavailable")

        mock_comment.assert_called_once()
        mock_remove.assert_not_called()

    @patch("auto_slopp.workers.github_task_source.comment_on_issue")
    @patch("auto_slopp.workers.github_task_source.remove_label_from_issue")
    @patch("auto_slopp.workers.github_task_source.settings")
    def test_on_skip_handles_missing_repo_path(self, mock_settings, mock_remove, mock_comment):
        """Test that on_skip handles missing repo_path in task."""
        mock_settings.github_issue_worker_required_label = "test-label"
        task_source = GitHubTaskSource()
        task = Task(id=42, title="Test", body="", comments=[], raw={})

        task_source.on_skip(task, "LLM unavailable")

        mock_comment.assert_not_called()
        mock_remove.assert_not_called()

    def test_pr_mentions_issue_in_title(self):
        """Test that _pr_mentions_issue returns True when issue number is in PR title."""
        task_source = GitHubTaskSource()
        prs = [
            {"title": "#42: Fix bug", "body": "", "headRefName": ""},
        ]
        assert task_source._pr_mentions_issue(prs, 42) is True
        assert task_source._pr_mentions_issue(prs, 99) is False

    def test_pr_mentions_issue_in_body(self):
        """Test that _pr_mentions_issue returns True when issue number is in PR body."""
        task_source = GitHubTaskSource()
        prs = [
            {"title": "Fix bug", "body": "Closes #42", "headRefName": ""},
        ]
        assert task_source._pr_mentions_issue(prs, 42) is True
        assert task_source._pr_mentions_issue(prs, 99) is False

    def test_pr_mentions_issue_in_branch(self):
        """Test that _pr_mentions_issue returns True when issue number is in branch name."""
        task_source = GitHubTaskSource()
        prs = [
            {"title": "Fix bug", "body": "", "headRefName": "ai/issue-42-fix-bug"},
        ]
        assert task_source._pr_mentions_issue(prs, 42) is True
        assert task_source._pr_mentions_issue(prs, 99) is False

    def test_pr_mentions_issue_empty_prs(self):
        """Test that _pr_mentions_issue returns False for empty PR list."""
        task_source = GitHubTaskSource()
        assert task_source._pr_mentions_issue([], 42) is False

    def test_pr_mentions_issue_no_match(self):
        """Test that _pr_mentions_issue returns False when issue number not found."""
        task_source = GitHubTaskSource()
        prs = [
            {"title": "#41: Fix bug", "body": "Closes #41", "headRefName": "ai/issue-41-fix"},
        ]
        assert task_source._pr_mentions_issue(prs, 42) is False

    @patch("auto_slopp.workers.github_task_source.get_open_prs")
    @patch("auto_slopp.workers.github_task_source.get_closed_prs")
    def test_has_prs_checks_closed_prs(self, mock_get_closed, mock_get_open):
        """Test that _has_prs also checks closed/merged PRs as evidence of work."""
        task_source = GitHubTaskSource()

        # No open PRs
        mock_get_open.return_value = []

        # But there's a closed PR that mentions the issue
        mock_get_closed.return_value = [
            {"title": "#42: Fix bug", "body": "", "headRefName": ""},
        ]

        # Should return True because closed PR is evidence of work
        assert task_source._has_prs(Path("/test"), 42) is True

    @patch("auto_slopp.workers.github_task_source.get_open_prs")
    @patch("auto_slopp.workers.github_task_source.get_closed_prs")
    def test_has_prs_open_pr_takes_precedence(self, mock_get_closed, mock_get_open):
        """Test that _has_prs returns early when open PR mentions issue."""
        task_source = GitHubTaskSource()

        mock_get_open.return_value = [
            {"title": "#42: Fix bug", "body": "", "headRefName": ""},
        ]

        assert task_source._has_prs(Path("/test"), 42) is True
        # Closed PRs shouldn't be queried if open PR already found
        mock_get_closed.assert_not_called()

    @patch("auto_slopp.workers.github_task_source.get_open_prs")
    @patch("auto_slopp.workers.github_task_source.get_closed_prs")
    def test_has_prs_no_prs_evidence(self, mock_get_closed, mock_get_open):
        """Test that _has_prs returns False when no PRs mention the issue."""
        task_source = GitHubTaskSource()

        mock_get_open.return_value = [
            {"title": "#41: Fix bug", "body": "", "headRefName": ""},
        ]
        mock_get_closed.return_value = [
            {"title": "#40: Another fix", "body": "", "headRefName": ""},
        ]

        assert task_source._has_prs(Path("/test"), 42) is False

    @patch("auto_slopp.workers.github_task_source.execute_with_instructions")
    @patch("auto_slopp.workers.github_task_source.get_issue_comments")
    def test_condense_comments_filters_by_author_only(self, mock_get_comments, mock_execute):
        """Test that _condense_comments filters to only include comments from the issue author."""
        mock_execute.return_value = {"stdout": "Condensed", "success": True}
        task_source = GitHubTaskSource()

        mock_get_comments.return_value = [
            {"author": {"login": "issue-author"}, "body": "Author comment 1", "databaseId": 1},
            {"author": {"login": "issue-author"}, "body": "Author comment 2", "databaseId": 2},
            {"author": {"login": "other-user"}, "body": "Other comment", "databaseId": 3},
        ]

        result = task_source._condense_comments(Path("/test"), 42, "issue-author", "allowed-creator")

        # Should condense the 2 issue-author comments
        assert len(result) == 1
        assert result[0] == "Condensed"
        mock_execute.assert_called_once()

    @patch("auto_slopp.workers.github_task_source.execute_with_instructions")
    @patch("auto_slopp.workers.github_task_source.get_issue_comments")
    def test_condense_comments_filters_by_allowed_creator_only(self, mock_get_comments, mock_execute):
        """Test that _condense_comments filters to only include comments from the allowed creator."""
        mock_execute.return_value = {"stdout": "Condensed", "success": True}
        task_source = GitHubTaskSource()

        mock_get_comments.return_value = [
            {"author": {"login": "issue-author"}, "body": "Author comment", "databaseId": 1},
            {"author": {"login": "allowed-creator"}, "body": "Allowed comment 1", "databaseId": 2},
            {"author": {"login": "allowed-creator"}, "body": "Allowed comment 2", "databaseId": 3},
            {"author": {"login": "other-user"}, "body": "Other comment", "databaseId": 4},
        ]

        result = task_source._condense_comments(Path("/test"), 42, "issue-author", "allowed-creator")

        # Should condense the 2 allowed-creator comments
        assert len(result) == 1
        assert result[0] == "Condensed"
        mock_execute.assert_called_once()

    @patch("auto_slopp.workers.github_task_source.execute_with_instructions")
    @patch("auto_slopp.workers.github_task_source.get_issue_comments")
    def test_condense_comments_mixed_author_and_allowed_creator(self, mock_get_comments, mock_execute):
        """Test that _condense_comments includes comments from both issue author AND allowed creator."""
        mock_execute.return_value = {"stdout": "Condensed", "success": True}
        task_source = GitHubTaskSource()

        mock_get_comments.return_value = [
            {"author": {"login": "issue-author"}, "body": "Author comment", "databaseId": 1},
            {"author": {"login": "allowed-creator"}, "body": "Allowed comment", "databaseId": 2},
            {"author": {"login": "other-user"}, "body": "Other comment", "databaseId": 3},
        ]

        result = task_source._condense_comments(Path("/test"), 42, "issue-author", "allowed-creator")

        # Should condense both the issue-author and allowed-creator comments (2 total)
        assert len(result) == 1
        assert result[0] == "Condensed"
        mock_execute.assert_called_once()

    @patch("auto_slopp.workers.github_task_source.get_issue_comments")
    def test_condense_comments_no_matching_author(self, mock_get_comments):
        """Test that _condense_comments returns empty when no comments match author or allowed creator."""
        task_source = GitHubTaskSource()

        mock_get_comments.return_value = [
            {"author": {"login": "other-user"}, "body": "Other comment 1", "databaseId": 1},
            {"author": {"login": "another-user"}, "body": "Other comment 2", "databaseId": 2},
        ]

        result = task_source._condense_comments(Path("/test"), 42, "issue-author", "allowed-creator")

        assert result == []

    @patch("auto_slopp.workers.github_task_source.get_issue_comments")
    def test_condense_comments_single_matching_comment(self, mock_get_comments):
        """Test that _condense_comments returns single comment without condensing."""
        task_source = GitHubTaskSource()

        mock_get_comments.return_value = [
            {"author": {"login": "issue-author"}, "body": "Single comment", "databaseId": 1},
            {"author": {"login": "other-user"}, "body": "Other comment", "databaseId": 2},
        ]

        result = task_source._condense_comments(Path("/test"), 42, "issue-author", "allowed-creator")

        assert result == ["Single comment"]

    @patch("auto_slopp.workers.github_task_source.get_issue_comments")
    def test_condense_comments_empty_comments_list(self, mock_get_comments):
        """Test that _condense_comments returns empty when there are no comments."""
        task_source = GitHubTaskSource()

        mock_get_comments.return_value = []

        result = task_source._condense_comments(Path("/test"), 42, "issue-author", "allowed-creator")

        assert result == []

    @patch("auto_slopp.workers.github_task_source.get_issue_comments")
    def test_condense_comments_handles_none_author(self, mock_get_comments):
        """Test that _condense_comments handles comments with None author gracefully."""
        task_source = GitHubTaskSource()

        mock_get_comments.return_value = [
            {"author": None, "body": "Comment without author", "databaseId": 1},
            {"author": {"login": "issue-author"}, "body": "Author comment", "databaseId": 2},
        ]

        result = task_source._condense_comments(Path("/test"), 42, "issue-author", "allowed-creator")

        assert result == ["Author comment"]

    @patch("auto_slopp.workers.github_task_source.comment_on_issue")
    @patch("auto_slopp.workers.github_task_source.delete_issue_comment")
    @patch("auto_slopp.workers.github_task_source.execute_with_instructions")
    @patch("auto_slopp.workers.github_task_source.get_issue_comments")
    def test_condense_comments_deletes_only_filtered_comments(
        self, mock_get_comments, mock_execute, mock_delete, mock_comment
    ):
        """Test that _condense_comments deletes only comments from author/allowed creator."""
        mock_execute.return_value = {"stdout": "Condensed", "success": True}
        task_source = GitHubTaskSource()

        mock_get_comments.return_value = [
            {"author": {"login": "issue-author"}, "body": "Author comment 1", "id": "comment-100", "databaseId": 100},
            {"author": {"login": "issue-author"}, "body": "Author comment 2", "id": "comment-101", "databaseId": 101},
            {"author": {"login": "other-user"}, "body": "Other comment", "id": "comment-200", "databaseId": 200},
        ]

        result = task_source._condense_comments(Path("/test"), 42, "issue-author", "allowed-creator")

        assert result == ["Condensed"]
        # Only the author's comments should be deleted, not the other user's
        assert mock_delete.call_count == 2
        mock_delete.assert_any_call(Path("/test"), 42, 100)
        mock_delete.assert_any_call(Path("/test"), 42, 101)
        # Summary should be posted
        mock_comment.assert_called_with(Path("/test"), 42, "Condensed")

    @patch("auto_slopp.workers.github_task_source.comment_on_issue")
    @patch("auto_slopp.workers.github_task_source.settings")
    def test_on_skip_adds_comment_and_does_not_remove_label(self, mock_settings, mock_comment):
        """Test that on_skip adds a skip comment but does NOT remove the required label."""
        mock_settings.github_issue_worker_required_label = "test-label"
        task_source = GitHubTaskSource()
        task = Task(id=42, title="Test", body="", comments=[], raw={"_repo_path": Path("/test")})

        task_source.on_skip(task, "LLM unavailable")

        mock_comment.assert_called_once()
        call_args = mock_comment.call_args[0]
        assert call_args[0] == Path("/test")
        assert call_args[1] == 42
        assert "Task Skipped" in call_args[2]
        assert "LLM unavailable" in call_args[2]
        assert "retried when the LLM becomes available" in call_args[2]

    @patch("auto_slopp.workers.github_task_source.comment_on_issue")
    @patch("auto_slopp.workers.github_task_source.settings")
    def test_on_skip_handles_missing_repo_path(self, mock_settings, mock_comment):
        """Test that on_skip handles missing repo_path in task gracefully."""
        mock_settings.github_issue_worker_required_label = "test-label"
        task_source = GitHubTaskSource()
        task = Task(id=42, title="Test", body="", comments=[], raw={})

        task_source.on_skip(task, "LLM unavailable")

        mock_comment.assert_not_called()
