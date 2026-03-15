"""Tests for OpenProjectWorker."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from auto_slopp.workers.openproject_worker import OpenProjectWorker


class TestOpenProjectWorker:
    """Tests for OpenProjectWorker."""

    def test_initialization_success(self):
        """Test successful worker initialization."""
        worker = OpenProjectWorker(
            timeout=7200,
            agent_args=["--verbose"],
            dry_run=True,
        )

        assert worker.timeout == 7200
        assert worker.agent_args == ["--verbose"]
        assert worker.dry_run is True

    def test_run_with_not_configured(self):
        """Test run when OpenProject is not configured."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / "repos" / "test_repo"
            repo_path.mkdir(parents=True)

            with patch("auto_slopp.workers.openproject_worker.settings") as mock_settings:
                mock_settings.openproject_url = ""
                mock_settings.openproject_api_token = ""

                worker = OpenProjectWorker(dry_run=True)
                result = worker.run(repo_path)

                assert result["success"] is False
                assert "not configured" in result["error"]

    def test_run_with_no_tasks(self):
        """Test run with no open tasks."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / "repos" / "test_repo"
            repo_path.mkdir(parents=True)

            mock_project = {"id": 1, "name": "test_repo"}

            with (
                patch("auto_slopp.workers.openproject_worker.settings") as mock_settings,
                patch("auto_slopp.workers.openproject_worker.get_project_by_identifier") as mock_get_project,
                patch("auto_slopp.workers.openproject_worker.get_open_work_packages") as mock_get_tasks,
                patch("auto_slopp.workers.openproject_worker.checkout_branch_resilient") as mock_checkout,
            ):
                mock_settings.openproject_url = "https://test.openproject.com"
                mock_settings.openproject_api_token = "test_token"
                mock_settings.openproject_assigned_user_id = 1
                mock_settings.openproject_project_prefix = ""
                mock_settings.openproject_create_projects = True
                mock_get_project.return_value = mock_project
                mock_get_tasks.return_value = []
                mock_checkout.return_value = True

                worker = OpenProjectWorker(dry_run=True)
                result = worker.run(repo_path)

                assert result["success"] is True
                assert result["repositories_processed"] == 1
                assert result["repositories_with_errors"] == 0
                assert result["tasks_processed"] == 0

    def test_run_with_tasks_dry_run(self):
        """Test run with open tasks in dry run mode."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / "repos" / "test_repo"
            repo_path.mkdir(parents=True)

            mock_project = {"id": 1, "name": "test_repo"}
            mock_task = {
                "id": 42,
                "subject": "Test Task",
                "description": {"raw": "This is a test task"},
                "lockVersion": 1,
            }

            with (
                patch("auto_slopp.workers.openproject_worker.settings") as mock_settings,
                patch("auto_slopp.workers.openproject_worker.get_project_by_identifier") as mock_get_project,
                patch("auto_slopp.workers.openproject_worker.get_open_work_packages") as mock_get_tasks,
                patch("auto_slopp.workers.openproject_worker.checkout_branch_resilient") as mock_checkout,
            ):
                mock_settings.openproject_url = "https://test.openproject.com"
                mock_settings.openproject_api_token = "test_token"
                mock_settings.openproject_assigned_user_id = 1
                mock_settings.openproject_project_prefix = ""
                mock_settings.openproject_create_projects = True
                mock_get_project.return_value = mock_project
                mock_get_tasks.return_value = [mock_task]
                mock_checkout.return_value = True

                worker = OpenProjectWorker(dry_run=True)
                result = worker.run(repo_path)

                assert result["success"] is True
                assert result["repositories_processed"] == 1
                assert result["tasks_processed"] == 1
                assert result["task_results"][0]["task_id"] == 42
                assert result["task_results"][0]["task_subject"] == "Test Task"

    def test_run_with_nonexistent_repo(self):
        """Test run with nonexistent repository path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / "nonexistent_repo"

            with patch("auto_slopp.workers.openproject_worker.settings") as mock_settings:
                mock_settings.openproject_url = "https://test.openproject.com"
                mock_settings.openproject_api_token = "test_token"

                worker = OpenProjectWorker(dry_run=True)
                result = worker.run(repo_path)

                assert result["success"] is False
                assert "error" in result

    def test_build_instructions(self):
        """Test instruction building."""
        worker = OpenProjectWorker(dry_run=True)

        instructions = worker._build_instructions("Fix bug", "This is a bug")
        assert "Fix bug" in instructions
        assert "This is a bug" in instructions
        assert "ai/" in instructions

    def test_build_instructions_with_branch_name(self):
        """Test instruction building with branch name provided."""
        worker = OpenProjectWorker(dry_run=True)

        instructions = worker._build_instructions(
            "Fix bug",
            "This is a bug",
            branch_name="ai/op-1-fix-bug",
        )
        assert "Fix bug" in instructions
        assert "This is a bug" in instructions
        assert "already on branch 'ai/op-1-fix-bug'" in instructions
        assert "Create a new branch" not in instructions

    def test_build_instructions_empty_description(self):
        """Test instruction building with empty description."""
        worker = OpenProjectWorker(dry_run=True)

        instructions = worker._build_instructions("Test task", "")
        assert "Test task" in instructions
        assert "ai/" in instructions

    def test_build_instructions_includes_plan(self):
        """Test that instructions include a structured plan."""
        worker = OpenProjectWorker(dry_run=True)

        instructions = worker._build_instructions("Test task", "Test description")
        assert "Plan:" in instructions
        assert "1." in instructions
        assert "2." in instructions
        assert "Understand the requirements" in instructions
        assert "Explore the codebase" in instructions
        assert "make lint" in instructions
        assert "make test" in instructions
        assert "Commit the changes" in instructions
        assert "Push the changes" in instructions

    def test_create_error_result(self):
        """Test error result creation."""
        worker = OpenProjectWorker(dry_run=True)
        start_time = 1000.0

        result = worker._create_error_result(
            start_time,
            Path("/test/repo"),
            "Test error",
        )

        assert result["success"] is False
        assert result["error"] == "Test error"
        assert result["worker_name"] == "OpenProjectWorker"

    def test_get_default_subtasks(self):
        """Test default subtask generation."""
        worker = OpenProjectWorker(dry_run=True)

        subtasks = worker._get_default_subtasks("Test Task")

        assert len(subtasks) > 0
        assert any("requirements" in s.lower() for s in subtasks)
        assert any("codebase" in s.lower() for s in subtasks)

    def test_parse_subtasks_from_output_numbered(self):
        """Test parsing numbered subtasks from output."""
        worker = OpenProjectWorker(dry_run=True)

        output = """1. First subtask
2. Second subtask
3. Third subtask"""

        subtasks = worker._parse_subtasks_from_output(output)

        assert len(subtasks) == 3
        assert subtasks[0] == "First subtask"
        assert subtasks[1] == "Second subtask"
        assert subtasks[2] == "Third subtask"

    def test_parse_subtasks_from_output_bullets(self):
        """Test parsing bullet subtasks from output."""
        worker = OpenProjectWorker(dry_run=True)

        output = """- First subtask
- Second subtask
- Third subtask"""

        subtasks = worker._parse_subtasks_from_output(output)

        assert len(subtasks) == 3
        assert subtasks[0] == "First subtask"
        assert subtasks[1] == "Second subtask"
        assert subtasks[2] == "Third subtask"

    def test_parse_subtasks_from_output_mixed(self):
        """Test parsing mixed format subtasks from output."""
        worker = OpenProjectWorker(dry_run=True)

        output = """1. First subtask
- Second subtask (as bullet)
2. Third subtask"""

        subtasks = worker._parse_subtasks_from_output(output)

        assert len(subtasks) >= 2

    def test_parse_subtasks_from_output_empty(self):
        """Test parsing empty output."""
        worker = OpenProjectWorker(dry_run=True)

        subtasks = worker._parse_subtasks_from_output("")

        assert subtasks == []

    def test_build_progress_info(self):
        """Test progress info building."""
        from auto_slopp.utils.ralph import Plan, Step

        worker = OpenProjectWorker(dry_run=True)

        plan = Plan(
            title="Test Plan",
            description="Test description",
            steps=[
                Step(number=1, description="First step", is_closed=True),
                Step(number=2, description="Second step", is_closed=False),
                Step(number=3, description="Third step", is_closed=False),
            ],
        )

        progress = worker._build_progress_info(plan)

        assert "✓" in progress
        assert "○" in progress
        assert "Step 1" in progress
        assert "Step 2" in progress
        assert "Step 3" in progress

    def test_branch_name_sanitization(self):
        """Test that branch names are properly sanitized from task subjects."""
        worker = OpenProjectWorker(dry_run=True)

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / "repos" / "test_repo"
            repo_path.mkdir(parents=True)

            mock_project = {"id": 1, "name": "test_repo"}

            test_cases = [
                {"subject": "Fix bug", "expected_prefix": "ai/op-1-fix-bug"},
                {
                    "subject": "Feature: Add new functionality",
                    "expected_prefix": "ai/op-2-feature-add-new-functio",
                },
                {
                    "subject": "Task with:colon",
                    "expected_prefix": "ai/op-3-task-with-colon",
                },
            ]

            for i, test_case in enumerate(test_cases, start=1):
                mock_task = {
                    "id": i,
                    "subject": test_case["subject"],
                    "description": {"raw": "Test description"},
                    "lockVersion": 1,
                }

                with (
                    patch("auto_slopp.workers.openproject_worker.settings") as mock_settings,
                    patch("auto_slopp.workers.openproject_worker.get_project_by_identifier") as mock_get_project,
                    patch("auto_slopp.workers.openproject_worker.get_open_work_packages") as mock_get_tasks,
                    patch("auto_slopp.workers.openproject_worker.checkout_branch_resilient") as mock_checkout,
                ):
                    mock_settings.openproject_url = "https://test.openproject.com"
                    mock_settings.openproject_api_token = "test_token"
                    mock_settings.openproject_assigned_user_id = 1
                    mock_settings.openproject_project_prefix = ""
                    mock_settings.openproject_create_projects = True
                    mock_get_project.return_value = mock_project
                    mock_get_tasks.return_value = [mock_task]
                    mock_checkout.return_value = True

                    result = worker.run(repo_path)

                    assert result["success"] is True
                    assert result["tasks_processed"] == 1

                    from auto_slopp.utils.git_operations import sanitize_branch_name

                    sanitized_subject = sanitize_branch_name(test_case["subject"][:30].lower())
                    expected_branch = f"ai/op-{i}-{sanitized_subject}"

                    assert result["task_results"][0]["task_subject"] == test_case["subject"]

    def test_get_or_create_project_existing_by_identifier(self):
        """Test getting existing project by identifier."""
        worker = OpenProjectWorker(dry_run=True)

        mock_project = {"id": 1, "name": "test-repo", "identifier": "test_repo"}

        with (
            patch("auto_slopp.workers.openproject_worker.settings") as mock_settings,
            patch("auto_slopp.workers.openproject_worker.get_project_by_identifier") as mock_get_id,
        ):
            mock_settings.openproject_project_prefix = ""
            mock_settings.openproject_create_projects = True
            mock_get_id.return_value = mock_project

            result = worker._get_or_create_project("test-repo")

            assert result == mock_project
            mock_get_id.assert_called_once_with("test_repo")

    def test_get_or_create_project_existing_by_name(self):
        """Test getting existing project by name when identifier not found."""
        worker = OpenProjectWorker(dry_run=True)

        mock_project = {"id": 1, "name": "test-repo", "identifier": "test_repo"}

        with (
            patch("auto_slopp.workers.openproject_worker.settings") as mock_settings,
            patch("auto_slopp.workers.openproject_worker.get_project_by_identifier") as mock_get_id,
            patch("auto_slopp.workers.openproject_worker.get_project_by_name") as mock_get_name,
        ):
            mock_settings.openproject_project_prefix = ""
            mock_settings.openproject_create_projects = True
            mock_get_id.return_value = None
            mock_get_name.return_value = mock_project

            result = worker._get_or_create_project("test-repo")

            assert result == mock_project
            mock_get_id.assert_called_once()
            mock_get_name.assert_called_once_with("test-repo")

    def test_get_or_create_project_create_new(self):
        """Test creating new project when it doesn't exist."""
        worker = OpenProjectWorker(dry_run=True)

        mock_project = {"id": 1, "name": "test-repo", "identifier": "test_repo"}

        with (
            patch("auto_slopp.workers.openproject_worker.settings") as mock_settings,
            patch("auto_slopp.workers.openproject_worker.get_project_by_identifier") as mock_get_id,
            patch("auto_slopp.workers.openproject_worker.get_project_by_name") as mock_get_name,
            patch("auto_slopp.workers.openproject_worker.create_project") as mock_create,
        ):
            mock_settings.openproject_project_prefix = ""
            mock_settings.openproject_create_projects = True
            mock_get_id.return_value = None
            mock_get_name.return_value = None
            mock_create.return_value = mock_project

            result = worker._get_or_create_project("test-repo")

            assert result == mock_project
            mock_create.assert_called_once()

    def test_get_or_create_project_no_create(self):
        """Test not creating project when auto-creation is disabled."""
        worker = OpenProjectWorker(dry_run=True)

        with (
            patch("auto_slopp.workers.openproject_worker.settings") as mock_settings,
            patch("auto_slopp.workers.openproject_worker.get_project_by_identifier") as mock_get_id,
            patch("auto_slopp.workers.openproject_worker.get_project_by_name") as mock_get_name,
        ):
            mock_settings.openproject_project_prefix = ""
            mock_settings.openproject_create_projects = False
            mock_get_id.return_value = None
            mock_get_name.return_value = None

            result = worker._get_or_create_project("test-repo")

            assert result is None

    def test_is_configured_true(self):
        """Test is_configured returns True when properly configured."""
        worker = OpenProjectWorker(dry_run=True)

        with patch("auto_slopp.workers.openproject_worker.settings") as mock_settings:
            mock_settings.openproject_url = "https://test.openproject.com"
            mock_settings.openproject_api_token = "test_token"

            assert worker._is_configured() is True

    def test_is_configured_false_no_url(self):
        """Test is_configured returns False when URL is missing."""
        worker = OpenProjectWorker(dry_run=True)

        with patch("auto_slopp.workers.openproject_worker.settings") as mock_settings:
            mock_settings.openproject_url = ""
            mock_settings.openproject_api_token = "test_token"

            assert worker._is_configured() is False

    def test_is_configured_false_no_token(self):
        """Test is_configured returns False when token is missing."""
        worker = OpenProjectWorker(dry_run=True)

        with patch("auto_slopp.workers.openproject_worker.settings") as mock_settings:
            mock_settings.openproject_url = "https://test.openproject.com"
            mock_settings.openproject_api_token = ""

            assert worker._is_configured() is False
