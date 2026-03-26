"""Tests for TaskSource ABC and Task dataclass."""

from pathlib import Path
from typing import List
from unittest.mock import patch

from auto_slopp.workers.github_task_source import GitHubTaskSource
from auto_slopp.workers.task_source import Task, TaskSource


class ConcreteTaskSource(TaskSource):
    """Concrete implementation for testing the ABC."""

    def get_tasks(self, repo_path: Path) -> List[Task]:
        return [Task(id=1, title="Test", body="body")]

    def get_branch_name(self, task: Task) -> str:
        return f"ai/test-{task.id}"

    def get_ralph_file_prefix(self) -> str:
        return "test"

    def get_task_difficulty_name(self) -> str:
        return "test_task"

    def get_default_pr_body(self, task: Task) -> str:
        return f"PR for {task.title}"

    def on_task_start(self, task: Task, branch_name: str) -> None:
        pass

    def on_task_complete(self, task: Task, branch_name: str, pr_url: str) -> None:
        pass

    def on_task_failure(self, task: Task, error: str) -> None:
        pass

    def on_no_changes(self, task: Task) -> None:
        pass

    def on_max_iterations_reached(self, task: Task, steps_completed: int, total_steps: int, error: str) -> None:
        pass


class TestTask:
    """Tests for the Task dataclass."""

    def test_task_creation_with_all_fields(self):
        task = Task(
            id=42,
            title="Fix bug",
            body="There is a bug",
            comments=["comment1", "comment2"],
            raw={"number": 42, "extra": "data"},
        )
        assert task.id == 42
        assert task.title == "Fix bug"
        assert task.body == "There is a bug"
        assert task.comments == ["comment1", "comment2"]
        assert task.raw == {"number": 42, "extra": "data"}

    def test_task_creation_with_defaults(self):
        task = Task(id=1, title="Test", body="body")
        assert task.id == 1
        assert task.title == "Test"
        assert task.body == "body"
        assert task.comments == []
        assert task.raw == {}

    def test_task_default_lists_are_independent(self):
        task1 = Task(id=1, title="A", body="a")
        task2 = Task(id=2, title="B", body="b")
        task1.comments.append("x")
        assert task2.comments == []
        task1.raw["key"] = "val"
        assert task2.raw == {}


class TestTaskSource:
    """Tests for the TaskSource ABC."""

    def test_concrete_implementation_can_be_instantiated(self):
        source = ConcreteTaskSource()
        assert isinstance(source, TaskSource)

    def test_get_tasks_returns_list(self):
        source = ConcreteTaskSource()
        tasks = source.get_tasks(Path("/tmp"))
        assert len(tasks) == 1
        assert tasks[0].id == 1

    def test_get_branch_name(self):
        source = ConcreteTaskSource()
        task = Task(id=5, title="My Task", body="")
        assert source.get_branch_name(task) == "ai/test-5"

    def test_get_ralph_file_prefix(self):
        source = ConcreteTaskSource()
        assert source.get_ralph_file_prefix() == "test"

    def test_get_task_difficulty_name(self):
        source = ConcreteTaskSource()
        assert source.get_task_difficulty_name() == "test_task"

    def test_get_default_pr_body(self):
        source = ConcreteTaskSource()
        task = Task(id=1, title="Fix it", body="")
        assert source.get_default_pr_body(task) == "PR for Fix it"

    def test_cannot_instantiate_abc_directly(self):
        import pytest

        with pytest.raises(TypeError):
            TaskSource()  # type: ignore[abstract]

    def test_incomplete_implementation_cannot_be_instantiated(self):
        import pytest

        class IncompleteSource(TaskSource):
            def get_tasks(self, repo_path: Path) -> List[Task]:
                return []

        with pytest.raises(TypeError):
            IncompleteSource()  # type: ignore[abstract]


class TestGitHubTaskSource:
    """Tests for the GitHubTaskSource implementation."""

    def test_github_task_source_initialization(self):
        """Test that GitHubTaskSource can be instantiated."""
        source = GitHubTaskSource()
        assert isinstance(source, TaskSource)

    @patch("auto_slopp.workers.github_task_source.get_open_issues")
    @patch("auto_slopp.workers.github_task_source.get_issue_comments")
    def test_get_tasks_returns_empty_list_when_no_issues(self, mock_comments, mock_issues):
        """Test that get_tasks returns empty list when no issues found."""
        mock_issues.return_value = []
        source = GitHubTaskSource()
        tasks = source.get_tasks(Path("/tmp"))
        assert len(tasks) == 0
        mock_issues.assert_called_once()

    @patch("auto_slopp.workers.github_task_source.get_open_issues")
    @patch("auto_slopp.workers.github_task_source.get_issue_comments")
    @patch("auto_slopp.workers.github_task_source.settings")
    def test_get_tasks_filters_renovate_issues(self, mock_settings, mock_comments, mock_issues):
        """Test that get_tasks filters out Renovate bot issues."""
        mock_settings.github_issue_worker_required_label = "ai"
        mock_settings.github_issue_worker_allowed_creator = "user1"
        mock_issues.return_value = [
            {
                "number": 1,
                "title": "Regular Issue",
                "body": "Body",
                "author": {"login": "user1"},
                "labels": [{"name": "ai"}],
            },
            {
                "number": 2,
                "title": "Renovate Issue",
                "body": "Body",
                "author": {"login": "renovate[bot]"},
                "labels": [],
            },
        ]
        mock_comments.return_value = []
        source = GitHubTaskSource()
        tasks = source.get_tasks(Path("/tmp"))
        assert len(tasks) == 1
        assert tasks[0].id == 1

    @patch("auto_slopp.workers.github_task_source.get_open_issues")
    @patch("auto_slopp.workers.github_task_source.get_issue_comments")
    @patch("auto_slopp.workers.github_task_source.settings")
    def test_get_tasks_filters_by_label_and_creator(self, mock_settings, mock_comments, mock_issues):
        """Test that get_tasks filters by required label and allowed creator."""
        mock_settings.github_issue_worker_required_label = "ai"
        mock_settings.github_issue_worker_allowed_creator = "testuser"

        mock_issues.return_value = [
            {
                "number": 1,
                "title": "Valid Issue",
                "body": "Body",
                "author": {"login": "testuser"},
                "labels": [{"name": "ai"}],
            },
            {
                "number": 2,
                "title": "Invalid Issue",
                "body": "Body",
                "author": {"login": "otheruser"},
                "labels": [{"name": "ai"}],
            },
        ]
        mock_comments.return_value = []
        source = GitHubTaskSource()
        tasks = source.get_tasks(Path("/tmp"))
        assert len(tasks) == 1
        assert tasks[0].id == 1

    @patch("auto_slopp.workers.github_task_source.get_open_issues")
    @patch("auto_slopp.workers.github_task_source.get_issue_comments")
    @patch("auto_slopp.workers.github_task_source.settings")
    def test_get_tasks_returns_correct_task_objects(self, mock_settings, mock_comments, mock_issues):
        """Test that get_tasks returns properly structured Task objects."""
        mock_settings.github_issue_worker_required_label = "ai"
        mock_settings.github_issue_worker_allowed_creator = "testuser"
        mock_issues.return_value = [
            {
                "number": 42,
                "title": "Test Issue",
                "body": "Test Body",
                "author": {"login": "testuser"},
                "labels": [{"name": "ai"}],
            },
        ]
        mock_comments.return_value = [
            {"author": "testuser", "body": "Comment 1"},
            {"author": "otheruser", "body": "Comment 2"},
        ]
        source = GitHubTaskSource()
        tasks = source.get_tasks(Path("/tmp"))
        assert len(tasks) == 1
        assert tasks[0].id == 42
        assert tasks[0].title == "Test Issue"
        assert tasks[0].body == "Test Body"
        assert tasks[0].comments == ["Comment 1"]
        assert tasks[0].raw["number"] == 42

    def test_get_branch_name_generates_correct_format(self):
        """Test that get_branch_name generates correct branch name."""
        source = GitHubTaskSource()
        task = Task(id=42, title="Fix a Bug in the Code", body="")
        branch_name = source.get_branch_name(task)
        assert branch_name == "ai/issue-42-fix-a-bug-in-the-code"

    def test_get_ralph_file_prefix(self):
        """Test that get_ralph_file_prefix returns 'github'."""
        source = GitHubTaskSource()
        assert source.get_ralph_file_prefix() == "github"

    def test_get_task_difficulty_name(self):
        """Test that get_task_difficulty_name returns 'github_issue'."""
        source = GitHubTaskSource()
        assert source.get_task_difficulty_name() == "github_issue"

    def test_get_default_pr_body(self):
        """Test that get_default_pr_body generates correct PR body."""
        source = GitHubTaskSource()
        task = Task(id=42, title="Fix Bug", body="This is the issue body")
        pr_body = source.get_default_pr_body(task)
        assert pr_body == "Closes #42\n\nThis is the issue body"

    @patch("auto_slopp.workers.github_task_source.close_issue")
    @patch("auto_slopp.workers.github_task_source.comment_on_issue")
    def test_on_task_complete_closes_issue_and_adds_comment(self, mock_comment, mock_close):
        """Test that on_task_complete closes issue and adds PR comment."""
        mock_close.return_value = True
        mock_comment.return_value = True
        source = GitHubTaskSource()
        task = Task(id=42, title="Test", body="", raw={"_repo_path": "/tmp"})
        source.on_task_complete(task, "ai/issue-42", "https://github.com/test/pr/1")
        mock_close.assert_called_once_with("/tmp", 42)
        mock_comment.assert_called_once_with("/tmp", 42, "Completed by PR: https://github.com/test/pr/1")

    @patch("auto_slopp.workers.github_task_source.close_issue")
    @patch("auto_slopp.workers.github_task_source.comment_on_issue")
    def test_on_no_changes_closes_issue_with_comment(self, mock_comment, mock_close):
        """Test that on_no_changes closes issue with no-changes comment."""
        source = GitHubTaskSource()
        task = Task(id=42, title="Test", body="", raw={"_repo_path": "/tmp"})
        source.on_no_changes(task)
        mock_comment.assert_called_once()
        mock_close.assert_called_once_with("/tmp", 42)

    @patch("auto_slopp.workers.github_task_source.remove_label_from_issue")
    @patch("auto_slopp.workers.github_task_source.comment_on_issue")
    @patch("auto_slopp.workers.github_task_source.settings")
    def test_on_max_iterations_reached_removes_label_and_comments(self, mock_settings, mock_comment, mock_remove_label):
        """Test that on_max_iterations_reached removes label and adds failure comment."""
        mock_settings.github_issue_worker_required_label = "ai"
        mock_remove_label.return_value = True
        source = GitHubTaskSource()
        task = Task(id=42, title="Test", body="", raw={"_repo_path": "/tmp"})
        source.on_max_iterations_reached(task, steps_completed=5, total_steps=10, error="Timeout")
        mock_comment.assert_called_once()
        mock_remove_label.assert_called_once_with("/tmp", 42, "ai")
