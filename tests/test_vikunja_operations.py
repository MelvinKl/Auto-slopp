"""Tests for Vikunja operations utilities."""

from unittest.mock import MagicMock, patch

import pytest

from auto_slopp.utils.vikunja_operations import (
    VikunjaOperationError,
    check_task_dependencies,
    comment_on_task,
    create_project,
    create_subtask,
    find_project,
    get_open_tasks_by_project,
    get_task_by_identifier,
    get_task_details,
    get_tasks,
    update_task_status,
    verify_blocking_closed,
)


class TestRunVikunjaCommand:
    """Tests for _run_vikunja_command internal function."""

    def test_success(self):
        """Test successful command execution."""
        from auto_slopp.utils.vikunja_operations import _run_vikunja_command

        with patch("auto_slopp.utils.vikunja_operations.subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = '{"success": true}'
            mock_result.stderr = ""
            mock_run.return_value = mock_result

            result = _run_vikunja_command("-list-tasks")

            assert result.returncode == 0
            assert result.stdout == '{"success": true}'
            mock_run.assert_called_once()

    def test_timeout(self):
        """Test command timeout handling."""
        from auto_slopp.utils.vikunja_operations import _run_vikunja_command

        with patch("auto_slopp.utils.vikunja_operations.subprocess.run") as mock_run:
            from subprocess import TimeoutExpired

            mock_run.side_effect = TimeoutExpired("vikunja-cli-helper", 30)

            with pytest.raises(VikunjaOperationError):
                _run_vikunja_command("-list-tasks")

    def test_command_failure(self):
        """Test command failure handling."""
        from auto_slopp.utils.vikunja_operations import _run_vikunja_command

        with patch("auto_slopp.utils.vikunja_operations.subprocess.run") as mock_run:
            from subprocess import CalledProcessError

            mock_run.side_effect = CalledProcessError(1, "vikunja-cli-helper", stderr="Error occurred")

            with pytest.raises(VikunjaOperationError):
                _run_vikunja_command("-list-tasks")


class TestFindProject:
    """Tests for find_project function."""

    def test_found(self):
        """Test successful project finding."""
        with patch("auto_slopp.utils.vikunja_operations._run_vikunja_command") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = '{"data": {"id": 1, "title": "test-project", "identifier": "test-project"}}'
            mock_run.return_value = mock_result

            result = find_project("test-project")

            assert result is not None
            assert result["id"] == 1
            assert result["title"] == "test-project"

    def test_not_found(self):
        """Test project not found."""
        with patch("auto_slopp.utils.vikunja_operations._run_vikunja_command") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 1
            mock_result.stdout = ""
            mock_result.stderr = "project not found: test-project"
            mock_run.return_value = mock_result

            result = find_project("test-project")

            assert result is None

    def test_invalid_json(self):
        """Test handling invalid JSON response."""
        with patch("auto_slopp.utils.vikunja_operations._run_vikunja_command") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "invalid json"
            mock_run.return_value = mock_result

            result = find_project("test-project")

            assert result is None


class TestCreateProject:
    """Tests for create_project function."""

    def test_success(self):
        """Test successful project creation."""
        with patch("auto_slopp.utils.vikunja_operations._run_vikunja_command") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = '{"data": {"id": 2, "title": "new-project", "identifier": "new-project"}}'
            mock_run.return_value = mock_result

            result = create_project("new-project")

            assert result is not None
            assert result["id"] == 2
            assert result["title"] == "new-project"

    def test_with_custom_identifier(self):
        """Test project creation with custom identifier."""
        with patch("auto_slopp.utils.vikunja_operations._run_vikunja_command") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = '{"data": {"id": 3, "title": "my project", "identifier": "my-custom-id"}}'
            mock_run.return_value = mock_result

            result = create_project("my project", "my-custom-id")

            assert result is not None
            assert result["identifier"] == "my-custom-id"

    def test_failure(self):
        """Test project creation failure."""
        with patch("auto_slopp.utils.vikunja_operations._run_vikunja_command") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 1
            mock_result.stdout = ""
            mock_result.stderr = "failed to create project"
            mock_run.return_value = mock_result

            result = create_project("test-project")

            assert result is None


class TestGetTasks:
    """Tests for get_tasks function."""

    def test_success(self):
        """Test successful task listing."""
        with patch("auto_slopp.utils.vikunja_operations._run_vikunja_command") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = (
                '{"data": [{"id": 1, "title": "Task 1", "done": false}, {"id": 2, "title": "Task 2", "done": false}]}'
            )
            mock_run.return_value = mock_result

            result = get_tasks()

            assert len(result) == 2
            assert result[0]["id"] == 1
            assert result[1]["title"] == "Task 2"

    def test_with_filters(self):
        """Test task listing with filters."""
        with patch("auto_slopp.utils.vikunja_operations._run_vikunja_command") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = '{"data": [{"id": 1, "done": false}]}'
            mock_run.return_value = mock_result

            result = get_tasks(task_filter="done=false", sort_by="id", order_by="asc")

            assert len(result) == 1
            mock_run.assert_called_once()

    def test_with_list_of_filters(self):
        """Test task listing with a list of filter strings."""
        with patch("auto_slopp.utils.vikunja_operations._run_vikunja_command") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = '{"data": [{"id": 1, "done": false}]}'
            mock_run.return_value = mock_result

            result = get_tasks(task_filter=["project_id=5", "done=false"])

            assert len(result) == 1
            call_args = mock_run.call_args[0]
            assert "-task-filter" in call_args
            # Both filters should appear as separate -task-filter arguments
            filter_indices = [i for i, a in enumerate(call_args) if a == "-task-filter"]
            assert len(filter_indices) == 2
            assert call_args[filter_indices[0] + 1] == "project_id=5"
            assert call_args[filter_indices[1] + 1] == "done=false"

    def test_empty_list(self):
        """Test empty task list."""
        with patch("auto_slopp.utils.vikunja_operations._run_vikunja_command") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = '{"data": []}'
            mock_run.return_value = mock_result

            result = get_tasks()

            assert result == []


class TestGetTaskDetails:
    """Tests for get_task_details function."""

    def test_found(self):
        """Test getting task details."""
        with patch("auto_slopp.utils.vikunja_operations.get_tasks") as mock_get_tasks:
            mock_get_tasks.return_value = [{"id": 1, "title": "Test Task", "description": "Test description"}]

            result = get_task_details(1)

            assert result is not None
            assert result["id"] == 1
            assert result["title"] == "Test Task"

    def test_not_found(self):
        """Test task not found."""
        with patch("auto_slopp.utils.vikunja_operations.get_tasks") as mock_get_tasks:
            mock_get_tasks.return_value = []

            result = get_task_details(999)

            assert result is None


class TestUpdateTaskStatus:
    """Tests for update_task_status function."""

    def test_success(self):
        """Test successful status update."""
        with patch("auto_slopp.utils.vikunja_operations._run_vikunja_command") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result

            result = update_task_status(1, "done")

            assert result is True

    def test_failure(self):
        """Test status update failure."""
        with patch("auto_slopp.utils.vikunja_operations._run_vikunja_command") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 1
            mock_run.return_value = mock_result

            result = update_task_status(1, "done")

            assert result is False


class TestCommentOnTask:
    """Tests for comment_on_task function."""

    def test_success(self):
        """Test successful comment addition."""
        with patch("auto_slopp.utils.vikunja_operations._run_vikunja_command") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result

            result = comment_on_task(1, "Test comment")

            assert result is True

    def test_failure(self):
        """Test comment addition failure."""
        with patch("auto_slopp.utils.vikunja_operations._run_vikunja_command") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 1
            mock_run.return_value = mock_result

            result = comment_on_task(1, "Test comment")

            assert result is False


class TestCreateSubtask:
    """Tests for create_subtask function."""

    def test_success(self):
        """Test successful subtask creation."""
        with patch("auto_slopp.utils.vikunja_operations._run_vikunja_command") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = '{"data": {"id": 2, "title": "Subtask 1", "description": "Subtask description"}}'
            mock_run.return_value = mock_result

            result = create_subtask(1, "Subtask 1", "Subtask description")

            assert result is not None
            assert result["id"] == 2
            assert result["title"] == "Subtask 1"

    def test_without_description(self):
        """Test subtask creation without description."""
        with patch("auto_slopp.utils.vikunja_operations._run_vikunja_command") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = '{"data": {"id": 2, "title": "Subtask 2"}}'
            mock_run.return_value = mock_result

            result = create_subtask(1, "Subtask 2")

            assert result is not None
            assert result["title"] == "Subtask 2"

    def test_failure(self):
        """Test subtask creation failure."""
        with patch("auto_slopp.utils.vikunja_operations._run_vikunja_command") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 1
            mock_result.stdout = ""
            mock_result.stderr = "failed to create subtask"
            mock_run.return_value = mock_result

            result = create_subtask(1, "Subtask")

            assert result is None


class TestCheckTaskDependencies:
    """Tests for check_task_dependencies function."""

    def test_success(self):
        """Test successful dependency check."""
        with patch("auto_slopp.utils.vikunja_operations._run_vikunja_command") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = '{"data": [{"id": 3, "title": "Blocking Task", "done": false}]}'
            mock_run.return_value = mock_result

            result = check_task_dependencies(1)

            assert len(result) == 1
            assert result[0]["id"] == 3

    def test_no_dependencies(self):
        """Test task with no dependencies."""
        with patch("auto_slopp.utils.vikunja_operations._run_vikunja_command") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = '{"data": []}'
            mock_run.return_value = mock_result

            result = check_task_dependencies(1)

            assert result == []


class TestVerifyBlockingClosed:
    """Tests for verify_blocking_closed function."""

    def test_all_closed(self):
        """Test when all blocking tasks are closed."""
        with patch("auto_slopp.utils.vikunja_operations._run_vikunja_command") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = '{"all_blocking_closed": true}'
            mock_run.return_value = mock_result

            result = verify_blocking_closed(1)

            assert result is True

    def test_not_all_closed(self):
        """Test when not all blocking tasks are closed."""
        with patch("auto_slopp.utils.vikunja_operations._run_vikunja_command") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = '{"all_blocking_closed": false}'
            mock_run.return_value = mock_result

            result = verify_blocking_closed(1)

            assert result is False

    def test_error_response(self):
        """Test error response."""
        with patch("auto_slopp.utils.vikunja_operations._run_vikunja_command") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = '{"error": "some error"}'
            mock_run.return_value = mock_result

            result = verify_blocking_closed(1)

            assert result is False


class TestGetOpenTasksByProject:
    """Tests for get_open_tasks_by_project function."""

    def test_success(self):
        """Test getting open tasks for a project."""
        with patch("auto_slopp.utils.vikunja_operations.get_tasks") as mock_get_tasks:
            mock_get_tasks.return_value = [
                {"id": 1, "project_id": 5, "done": False},
                {"id": 2, "project_id": 5, "done": False},
            ]

            result = get_open_tasks_by_project(5)

            assert len(result) == 2
            mock_get_tasks.assert_called_once_with(task_filter=["project_id=5", "done=false"])


class TestGetTaskByIdentifier:
    """Tests for get_task_by_identifier function."""

    def test_found(self):
        """Test finding task by identifier."""
        with patch("auto_slopp.utils.vikunja_operations.get_tasks") as mock_get_tasks:
            mock_get_tasks.return_value = [
                {"id": 1, "title": "Task 1", "identifier": "T5-1"},
                {"id": 2, "title": "Task 2", "identifier": "T5-2"},
            ]

            result = get_task_by_identifier("T5-2")

            assert result is not None
            assert result["id"] == 2
            assert result["title"] == "Task 2"

    def test_not_found(self):
        """Test task identifier not found."""
        with patch("auto_slopp.utils.vikunja_operations.get_tasks") as mock_get_tasks:
            mock_get_tasks.return_value = [{"id": 1, "identifier": "T5-1"}]

            result = get_task_by_identifier("T5-999")

            assert result is None
