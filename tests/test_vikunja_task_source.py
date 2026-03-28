"""Tests for VikunjaTaskSource."""

from pathlib import Path
from unittest.mock import patch

from auto_slopp.workers.task_source import Task
from auto_slopp.workers.vikunja_task_source import VikunjaTaskSource


class TestVikunjaTaskSource:
    """Tests for VikunjaTaskSource."""

    @patch("auto_slopp.workers.vikunja_task_source.find_or_create_project")
    @patch("auto_slopp.workers.vikunja_task_source.settings")
    def test_get_tasks_returns_empty_on_project_creation_failure(self, mock_settings, mock_find_project):
        """Test that get_tasks returns empty list when project creation fails."""
        mock_settings.github_issue_worker_required_label = "test-tag"
        mock_find_project.return_value = None

        task_source = VikunjaTaskSource()
        tasks = task_source.get_tasks(Path("/test/repo"))

        assert tasks == []
        mock_find_project.assert_called_once_with("repo")

    @patch("auto_slopp.workers.vikunja_task_source.get_open_tasks_by_project")
    @patch("auto_slopp.workers.vikunja_task_source.find_or_create_project")
    @patch("auto_slopp.workers.vikunja_task_source.verify_blocking_closed")
    @patch("auto_slopp.workers.vikunja_task_source.settings")
    def test_get_tasks_filters_by_tag(self, mock_settings, mock_verify, mock_find_project, mock_get_tasks):
        """Test that get_tasks filters tasks by required tag."""
        mock_settings.github_issue_worker_required_label = "test-tag"
        mock_find_project.return_value = {"id": 1, "title": "Test Project"}
        mock_verify.return_value = True

        mock_tasks = [
            {
                "id": 1,
                "title": "Task 1",
                "description": "Description 1",
                "priority": 5,
                "labels": [{"title": "test-tag"}],
            },
            {
                "id": 2,
                "title": "Task 2",
                "description": "Description 2",
                "priority": 3,
                "labels": [{"title": "other-tag"}],
            },
        ]
        mock_get_tasks.return_value = mock_tasks

        task_source = VikunjaTaskSource()
        tasks = task_source.get_tasks(Path("/test/repo"))

        assert len(tasks) == 1
        assert tasks[0].id == 1

    @patch("auto_slopp.workers.vikunja_task_source.get_open_tasks_by_project")
    @patch("auto_slopp.workers.vikunja_task_source.find_or_create_project")
    @patch("auto_slopp.workers.vikunja_task_source.verify_blocking_closed")
    @patch("auto_slopp.workers.vikunja_task_source.settings")
    def test_get_tasks_filters_tag_case_insensitive(
        self, mock_settings, mock_verify, mock_find_project, mock_get_tasks
    ):
        """Test that tag filtering is case-insensitive."""
        mock_settings.github_issue_worker_required_label = "TEST-TAG"
        mock_find_project.return_value = {"id": 1, "title": "Test Project"}
        mock_verify.return_value = True

        mock_tasks = [
            {
                "id": 1,
                "title": "Task 1",
                "description": "Description 1",
                "priority": 5,
                "labels": [{"title": "test-tag"}],
            },
        ]
        mock_get_tasks.return_value = mock_tasks

        task_source = VikunjaTaskSource()
        tasks = task_source.get_tasks(Path("/test/repo"))

        assert len(tasks) == 1

    @patch("auto_slopp.workers.vikunja_task_source.get_open_tasks_by_project")
    @patch("auto_slopp.workers.vikunja_task_source.find_or_create_project")
    @patch("auto_slopp.workers.vikunja_task_source.verify_blocking_closed")
    @patch("auto_slopp.workers.vikunja_task_source.settings")
    def test_get_tasks_filters_by_dependencies(self, mock_settings, mock_verify, mock_find_project, mock_get_tasks):
        """Test that get_tasks filters tasks by open dependencies."""
        mock_settings.github_issue_worker_required_label = "test-tag"
        mock_find_project.return_value = {"id": 1, "title": "Test Project"}
        mock_verify.side_effect = [True, False, True]

        mock_tasks = [
            {
                "id": 1,
                "title": "Task 1",
                "description": "Description 1",
                "priority": 5,
                "labels": [{"title": "test-tag"}],
            },
            {
                "id": 2,
                "title": "Task 2",
                "description": "Description 2",
                "priority": 3,
                "labels": [{"title": "test-tag"}],
            },
            {
                "id": 3,
                "title": "Task 3",
                "description": "Description 3",
                "priority": 4,
                "labels": [{"title": "test-tag"}],
            },
        ]
        mock_get_tasks.return_value = mock_tasks

        task_source = VikunjaTaskSource()
        tasks = task_source.get_tasks(Path("/test/repo"))

        assert len(tasks) == 2
        assert tasks[0].id == 1
        assert tasks[1].id == 3
        assert mock_verify.call_count == 3

    @patch("auto_slopp.workers.vikunja_task_source.get_open_tasks_by_project")
    @patch("auto_slopp.workers.vikunja_task_source.find_or_create_project")
    @patch("auto_slopp.workers.vikunja_task_source.verify_blocking_closed")
    @patch("auto_slopp.workers.vikunja_task_source.settings")
    def test_get_tasks_sorts_by_priority_descending(
        self, mock_settings, mock_verify, mock_find_project, mock_get_tasks
    ):
        """Test that get_tasks sorts tasks by priority descending."""
        mock_settings.github_issue_worker_required_label = "test-tag"
        mock_find_project.return_value = {"id": 1, "title": "Test Project"}
        mock_verify.return_value = True

        mock_tasks = [
            {
                "id": 1,
                "title": "Task 1",
                "description": "Description 1",
                "priority": 3,
                "labels": [{"title": "test-tag"}],
            },
            {
                "id": 2,
                "title": "Task 2",
                "description": "Description 2",
                "priority": 5,
                "labels": [{"title": "test-tag"}],
            },
            {
                "id": 3,
                "title": "Task 3",
                "description": "Description 3",
                "priority": 4,
                "labels": [{"title": "test-tag"}],
            },
        ]
        mock_get_tasks.return_value = mock_tasks

        task_source = VikunjaTaskSource()
        tasks = task_source.get_tasks(Path("/test/repo"))

        assert len(tasks) == 3
        assert tasks[0].id == 2
        assert tasks[1].id == 3
        assert tasks[2].id == 1

    @patch("auto_slopp.workers.vikunja_task_source.get_open_tasks_by_project")
    @patch("auto_slopp.workers.vikunja_task_source.find_or_create_project")
    @patch("auto_slopp.workers.vikunja_task_source.verify_blocking_closed")
    @patch("auto_slopp.workers.vikunja_task_source.settings")
    def test_get_tasks_constructs_task_objects(self, mock_settings, mock_verify, mock_find_project, mock_get_tasks):
        """Test that get_tasks constructs Task dataclass objects correctly."""
        mock_settings.github_issue_worker_required_label = "test-tag"
        mock_find_project.return_value = {"id": 1, "title": "Test Project"}
        mock_verify.return_value = True

        mock_tasks = [
            {
                "id": 1,
                "title": "Test Task",
                "description": "Test Description",
                "priority": 5,
                "labels": [{"title": "test-tag"}],
            }
        ]
        mock_get_tasks.return_value = mock_tasks

        task_source = VikunjaTaskSource()
        tasks = task_source.get_tasks(Path("/test/repo"))

        assert len(tasks) == 1
        task = tasks[0]
        assert task.id == 1
        assert task.title == "Test Task"
        assert task.body == "Test Description"
        assert task.comments == []
        assert task.raw is not None
        assert task.raw.get("_repo_path") == Path("/test/repo")

    @patch("auto_slopp.workers.vikunja_task_source.get_open_tasks_by_project")
    @patch("auto_slopp.workers.vikunja_task_source.find_or_create_project")
    @patch("auto_slopp.workers.vikunja_task_source.settings")
    def test_get_tasks_returns_empty_on_no_tasks(self, mock_settings, mock_find_project, mock_get_tasks):
        """Test that get_tasks returns empty list when no tasks found."""
        mock_settings.github_issue_worker_required_label = "test-tag"
        mock_find_project.return_value = {"id": 1, "title": "Test Project"}
        mock_get_tasks.return_value = []

        task_source = VikunjaTaskSource()
        tasks = task_source.get_tasks(Path("/test/repo"))

        assert tasks == []

    def test_get_branch_name(self):
        """Test that get_branch_name returns correct format."""
        task_source = VikunjaTaskSource()
        task = Task(id=42, title="Test Task Title", body="", comments=[], raw={})

        branch_name = task_source.get_branch_name(task)

        assert branch_name == "ai/task-42-test-task-title"

    def test_get_ralph_file_prefix(self):
        """Test that get_ralph_file_prefix returns 'vikunja'."""
        task_source = VikunjaTaskSource()

        assert task_source.get_ralph_file_prefix() == "vikunja"

    def test_get_default_pr_body(self):
        """Test that get_default_pr_body returns correct format."""
        task_source = VikunjaTaskSource()
        task = Task(id=42, title="Test Task", body="Test Body", comments=[], raw={})

        pr_body = task_source.get_default_pr_body(task)

        assert "Vikunja Task #42: Test Task" in pr_body
        assert "Test Body" in pr_body

    @patch("auto_slopp.workers.vikunja_task_source.update_task_status")
    @patch("auto_slopp.workers.vikunja_task_source.analyze_task")
    @patch("auto_slopp.workers.vikunja_task_source.comment_on_task")
    def test_on_task_start_updates_status_and_comments(self, mock_comment, mock_analyze, mock_update):
        """Test that on_task_start updates status and adds comment."""
        mock_analyze.return_value = [{"id": 1}]
        task_source = VikunjaTaskSource()
        task = Task(id=42, title="Test", body="", comments=[], raw={})

        task_source.on_task_start(task, "ai/task-42-test")

        mock_update.assert_called_once_with(42, "in_progress")
        mock_analyze.assert_called_once_with(42)
        mock_comment.assert_called_once()
        comment_args = mock_comment.call_args[0]
        assert comment_args[0] == 42
        assert "ai/task-42-test" in comment_args[1]

    @patch("auto_slopp.workers.vikunja_task_source.update_task_status")
    @patch("auto_slopp.workers.vikunja_task_source.comment_on_task")
    def test_on_task_complete_updates_status_and_comments(self, mock_comment, mock_update):
        """Test that on_task_complete updates status and adds comment."""
        task_source = VikunjaTaskSource()
        task = Task(id=42, title="Test", body="", comments=[], raw={})

        task_source.on_task_complete(task, "ai/task-42-test", "https://github.com/test/pr/1")

        mock_update.assert_called_once_with(42, "done")
        mock_comment.assert_called_once()
        comment_args = mock_comment.call_args[0]
        assert comment_args[0] == 42
        assert "ai/task-42-test" in comment_args[1]
        assert "https://github.com/test/pr/1" in comment_args[1]

    @patch("auto_slopp.workers.vikunja_task_source.update_task_status")
    @patch("auto_slopp.workers.vikunja_task_source.comment_on_task")
    def test_on_task_failure_updates_status_and_comments(self, mock_comment, mock_update):
        """Test that on_task_failure updates status and adds comment."""
        task_source = VikunjaTaskSource()
        task = Task(id=42, title="Test", body="", comments=[], raw={})

        task_source.on_task_failure(task, "Test error")

        mock_comment.assert_called_once()
        mock_update.assert_called_once_with(42, "failed")
        comment_args = mock_comment.call_args[0]
        assert comment_args[0] == 42
        assert "Test error" in comment_args[1]

    @patch("auto_slopp.workers.vikunja_task_source.update_task_status")
    @patch("auto_slopp.workers.vikunja_task_source.comment_on_task")
    def test_on_no_changes_updates_status_and_comments(self, mock_comment, mock_update):
        """Test that on_no_changes updates status and adds comment."""
        task_source = VikunjaTaskSource()
        task = Task(id=42, title="Test", body="", comments=[], raw={})

        task_source.on_no_changes(task)

        mock_update.assert_called_once_with(42, "done")
        mock_comment.assert_called_once()
        comment_args = mock_comment.call_args[0]
        assert comment_args[0] == 42
        assert "No Changes Required" in comment_args[1]

    @patch("auto_slopp.workers.vikunja_task_source.update_task_status")
    @patch("auto_slopp.workers.vikunja_task_source.comment_on_task")
    def test_on_max_iterations_reached_updates_status_and_comments(self, mock_comment, mock_update):
        """Test that on_max_iterations_reached updates status and adds comment."""
        task_source = VikunjaTaskSource()
        task = Task(id=42, title="Test", body="", comments=[], raw={})

        task_source.on_max_iterations_reached(task, 8, 15, "Max iterations reached")

        mock_update.assert_called_once_with(42, "failed")
        mock_comment.assert_called_once()
        comment_args = mock_comment.call_args[0]
        assert comment_args[0] == 42
        assert "8/15" in comment_args[1]
        assert "Max iterations reached" in comment_args[1]
