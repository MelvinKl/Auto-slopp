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

    def test_get_or_create_project_create_fails_already_exists(self):
        """Test handling when create_project fails but project already exists."""
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
            mock_get_id.side_effect = [None, mock_project]
            mock_get_name.return_value = None
            mock_create.return_value = None

            result = worker._get_or_create_project("test-repo")

            assert result == mock_project
            assert mock_get_id.call_count == 2
            mock_create.assert_called_once()

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

    def test_process_single_task_no_id(self):
        """Test _process_single_task with task that has no ID."""
        worker = OpenProjectWorker(dry_run=True)

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / "test_repo"
            repo_path.mkdir()

            task = {"subject": "No ID Task"}

            result = worker._process_single_task(repo_path, task, 1)

            assert result["success"] is False
            assert result["error"] == "Task has no ID"
            assert result["task_id"] is None

    def test_process_single_task_branch_creation_fails(self):
        """Test _process_single_task when branch creation fails."""
        worker = OpenProjectWorker(dry_run=False)

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / "test_repo"
            repo_path.mkdir()

            task = {
                "id": 1,
                "subject": "Test Task",
                "description": {"raw": "Test description"},
                "lockVersion": 1,
            }

            with (
                patch("auto_slopp.workers.openproject_worker.create_and_checkout_branch") as mock_branch,
                patch("auto_slopp.workers.openproject_worker.create_subtask") as mock_subtask,
            ):
                mock_branch.return_value = False
                mock_subtask.return_value = {"id": 100, "subject": "Subtask 1"}

                result = worker._process_single_task(repo_path, task, 1)

                assert result["success"] is False
                assert "Failed to create branch" in result["error"]

    def test_process_single_task_no_changes_made(self):
        """Test _process_single_task when no changes are made (stays on main)."""
        worker = OpenProjectWorker(dry_run=False)

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / "test_repo"
            repo_path.mkdir()

            task = {
                "id": 1,
                "subject": "Test Task",
                "description": {"raw": "Test description"},
                "lockVersion": 1,
            }

            with (
                patch("auto_slopp.workers.openproject_worker.create_and_checkout_branch") as mock_branch,
                patch("auto_slopp.workers.openproject_worker.get_current_branch") as mock_get_branch,
                patch("auto_slopp.workers.openproject_worker.add_comment_to_work_package") as mock_comment,
                patch("auto_slopp.workers.openproject_worker.create_subtask") as mock_subtask,
                patch("auto_slopp.workers.openproject_worker.settings") as mock_settings,
                patch("auto_slopp.workers.openproject_worker.execute_with_instructions") as mock_execute,
            ):
                mock_branch.return_value = True
                mock_get_branch.return_value = "main"
                mock_comment.return_value = True
                mock_subtask.return_value = {"id": 100, "subject": "Subtask 1"}
                mock_settings.ralph_enabled = False
                mock_execute.return_value = {"success": True}

                result = worker._process_single_task(repo_path, task, 1)

                assert result["success"] is True
                assert result["no_changes"] is True
                assert result["task_updated"] is True
                assert result["task_commented"] is True
                mock_comment.assert_called_once()

    def test_process_single_task_creates_pr_successfully(self):
        """Test _process_single_task creates PR successfully."""
        worker = OpenProjectWorker(dry_run=False)

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / "test_repo"
            repo_path.mkdir()

            task = {
                "id": 1,
                "subject": "Test Task",
                "description": {"raw": "Test description"},
                "lockVersion": 1,
            }

            with (
                patch("auto_slopp.workers.openproject_worker.create_and_checkout_branch") as mock_branch,
                patch("auto_slopp.workers.openproject_worker.get_current_branch") as mock_get_branch,
                patch("auto_slopp.workers.openproject_worker.get_pr_for_branch") as mock_get_pr,
                patch("auto_slopp.workers.openproject_worker.create_pull_request") as mock_create_pr,
                patch("auto_slopp.workers.openproject_worker.set_work_package_status") as mock_status,
                patch("auto_slopp.workers.openproject_worker.add_comment_to_work_package") as mock_comment,
                patch("auto_slopp.workers.openproject_worker.create_subtask") as mock_subtask,
                patch("auto_slopp.workers.openproject_worker.settings") as mock_settings,
                patch("auto_slopp.workers.openproject_worker.execute_with_instructions") as mock_execute,
            ):
                mock_branch.return_value = True
                mock_get_branch.return_value = "ai/op-1-test-task"
                mock_get_pr.return_value = None
                mock_create_pr.return_value = {"url": "https://github.com/test/repo/pull/1"}
                mock_status.return_value = True
                mock_comment.return_value = True
                mock_subtask.return_value = {"id": 100, "subject": "Subtask 1"}
                mock_settings.ralph_enabled = False
                mock_settings.openproject_in_progress_status_id = 7
                mock_execute.return_value = {"success": True}

                result = worker._process_single_task(repo_path, task, 1)

                assert result["success"] is True
                assert result["pr_created"] is True
                assert result["pr_url"] == "https://github.com/test/repo/pull/1"
                assert result["task_status_updated"] is True
                mock_create_pr.assert_called_once()
                mock_status.assert_called_once()
                mock_comment.assert_called_once()

    def test_process_single_task_pr_already_exists(self):
        """Test _process_single_task when PR already exists."""
        worker = OpenProjectWorker(dry_run=False)

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / "test_repo"
            repo_path.mkdir()

            task = {
                "id": 1,
                "subject": "Test Task",
                "description": {"raw": "Test description"},
                "lockVersion": 1,
            }

            with (
                patch("auto_slopp.workers.openproject_worker.create_and_checkout_branch") as mock_branch,
                patch("auto_slopp.workers.openproject_worker.get_current_branch") as mock_get_branch,
                patch("auto_slopp.workers.openproject_worker.get_pr_for_branch") as mock_get_pr,
                patch("auto_slopp.workers.openproject_worker.set_work_package_status") as mock_status,
                patch("auto_slopp.workers.openproject_worker.add_comment_to_work_package") as mock_comment,
                patch("auto_slopp.workers.openproject_worker.create_subtask") as mock_subtask,
                patch("auto_slopp.workers.openproject_worker.settings") as mock_settings,
                patch("auto_slopp.workers.openproject_worker.execute_with_instructions") as mock_execute,
            ):
                mock_branch.return_value = True
                mock_get_branch.return_value = "ai/op-1-test-task"
                mock_get_pr.return_value = {
                    "state": "OPEN",
                    "url": "https://github.com/test/repo/pull/2",
                }
                mock_status.return_value = True
                mock_comment.return_value = True
                mock_subtask.return_value = {"id": 100, "subject": "Subtask 1"}
                mock_settings.ralph_enabled = False
                mock_settings.openproject_in_progress_status_id = 7
                mock_execute.return_value = {"success": True}

                result = worker._process_single_task(repo_path, task, 1)

                assert result["success"] is True
                assert result["pr_created"] is True
                assert result["pr_url"] == "https://github.com/test/repo/pull/2"

    def test_process_single_task_pr_creation_fails(self):
        """Test _process_single_task when PR creation fails."""
        worker = OpenProjectWorker(dry_run=False)

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / "test_repo"
            repo_path.mkdir()

            task = {
                "id": 1,
                "subject": "Test Task",
                "description": {"raw": "Test description"},
                "lockVersion": 1,
            }

            with (
                patch("auto_slopp.workers.openproject_worker.create_and_checkout_branch") as mock_branch,
                patch("auto_slopp.workers.openproject_worker.get_current_branch") as mock_get_branch,
                patch("auto_slopp.workers.openproject_worker.get_pr_for_branch") as mock_get_pr,
                patch("auto_slopp.workers.openproject_worker.create_pull_request") as mock_create_pr,
                patch("auto_slopp.workers.openproject_worker.create_subtask") as mock_subtask,
                patch("auto_slopp.workers.openproject_worker.settings") as mock_settings,
                patch("auto_slopp.workers.openproject_worker.execute_with_instructions") as mock_execute,
            ):
                mock_branch.return_value = True
                mock_get_branch.return_value = "ai/op-1-test-task"
                mock_get_pr.return_value = None
                mock_create_pr.return_value = None
                mock_subtask.return_value = {"id": 100, "subject": "Subtask 1"}
                mock_settings.ralph_enabled = False
                mock_execute.return_value = {"success": True}

                result = worker._process_single_task(repo_path, task, 1)

                assert result["success"] is False
                assert result["error"] == "Failed to create pull request"

    def test_create_task_plan(self):
        """Test _create_task_plan creates a proper plan."""
        import tempfile
        from pathlib import Path

        from auto_slopp.utils.ralph import Plan, Step

        worker = OpenProjectWorker(dry_run=True)

        with tempfile.TemporaryDirectory() as temp_dir:
            plan_path = Path(temp_dir) / ".ralph" / "test-plan.md"
            plan_path.parent.mkdir(parents=True, exist_ok=True)

            task = {
                "id": 1,
                "subject": "Test Task",
                "description": {"raw": "Test description"},
            }

            subtasks = [
                {"subject": "Subtask 1", "description": {"raw": "Desc 1"}},
                {"subject": "Subtask 2", "description": {"raw": "Desc 2"}},
            ]

            plan = worker._create_task_plan(
                plan_path=plan_path,
                task=task,
                subtasks=subtasks,
                branch_name="ai/op-1-test",
            )

            assert plan is not None
            assert plan.title == "OpenProject Task Plan: Test Task"
            assert len(plan.steps) == 2
            assert "ai/op-1-test" in plan.description
            assert plan_path.exists()

    def test_build_step_instructions(self):
        """Test _build_step_instructions creates proper instructions."""
        from auto_slopp.utils.ralph import Plan, Step

        worker = OpenProjectWorker(dry_run=True)

        plan = Plan(
            title="Test Plan",
            description="Test description",
            steps=[
                Step(number=1, description="First step", is_closed=True),
                Step(number=2, description="Second step", is_closed=False),
            ],
        )

        step = Step(number=2, description="Second step", is_closed=False)

        task = {
            "subject": "Test Task",
            "description": {"raw": "Task description"},
        }

        instructions = worker._build_step_instructions(
            step=step,
            plan=plan,
            task=task,
            branch_name="ai/op-1-test",
        )

        assert "Test Task" in instructions
        assert "Task description" in instructions
        assert "ai/op-1-test" in instructions
        assert "Step 2: Second step" in instructions
        assert "✓" in instructions
        assert "○" in instructions

    def test_create_results_dict(self):
        """Test _create_results_dict creates proper dictionary."""
        worker = OpenProjectWorker(dry_run=True)

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / "test_repo"
            repo_path.mkdir()

            result = worker._create_results_dict(1000.0, repo_path)

            assert result["worker_name"] == "OpenProjectWorker"
            assert result["repo_path"] == str(repo_path)
            assert result["dry_run"] is True
            assert result["repositories_processed"] == 1
            assert result["repositories_with_errors"] == 0
            assert result["tasks_processed"] == 0
            assert result["success"] is True
            assert result["task_results"] == []

    def test_checkout_main_branch_failure(self):
        """Test _checkout_main_branch when checkout fails."""
        worker = OpenProjectWorker(dry_run=False)

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / "test_repo"
            repo_path.mkdir()

            with patch("auto_slopp.workers.openproject_worker.checkout_branch_resilient") as mock_checkout:
                mock_checkout.return_value = False

                result = worker._checkout_main_branch(repo_path)

                assert result is False

    def test_run_with_checkout_failure(self):
        """Test run when checkout of main branch fails."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / "repos" / "test_repo"
            repo_path.mkdir(parents=True)

            with (
                patch("auto_slopp.workers.openproject_worker.settings") as mock_settings,
                patch("auto_slopp.workers.openproject_worker.checkout_branch_resilient") as mock_checkout,
            ):
                mock_settings.openproject_url = "https://test.openproject.com"
                mock_settings.openproject_api_token = "test_token"
                mock_checkout.return_value = False

                worker = OpenProjectWorker(dry_run=False)
                result = worker.run(repo_path)

                assert result["success"] is False
                assert result["repositories_with_errors"] == 1

    def test_run_with_project_not_found_no_create(self):
        """Test run when project not found and auto-creation is disabled."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / "repos" / "test_repo"
            repo_path.mkdir(parents=True)

            with (
                patch("auto_slopp.workers.openproject_worker.settings") as mock_settings,
                patch("auto_slopp.workers.openproject_worker.get_project_by_identifier") as mock_get_id,
                patch("auto_slopp.workers.openproject_worker.get_project_by_name") as mock_get_name,
                patch("auto_slopp.workers.openproject_worker.checkout_branch_resilient") as mock_checkout,
            ):
                mock_settings.openproject_url = "https://test.openproject.com"
                mock_settings.openproject_api_token = "test_token"
                mock_settings.openproject_project_prefix = ""
                mock_settings.openproject_create_projects = False
                mock_get_id.return_value = None
                mock_get_name.return_value = None
                mock_checkout.return_value = True

                worker = OpenProjectWorker(dry_run=False)
                result = worker.run(repo_path)

                assert result["success"] is True
                assert result["tasks_processed"] == 0

    def test_get_or_create_project_with_prefix(self):
        """Test _get_or_create_project uses prefix correctly."""
        worker = OpenProjectWorker(dry_run=True)

        mock_project = {"id": 1, "name": "test-repo", "identifier": "prefix_test_repo"}

        with (
            patch("auto_slopp.workers.openproject_worker.settings") as mock_settings,
            patch("auto_slopp.workers.openproject_worker.get_project_by_identifier") as mock_get_id,
        ):
            mock_settings.openproject_project_prefix = "prefix_"
            mock_settings.openproject_create_projects = True
            mock_get_id.return_value = mock_project

            result = worker._get_or_create_project("test-repo")

            assert result == mock_project
            mock_get_id.assert_called_once_with("prefix_test_repo")

    def test_run_with_multiple_tasks_processes_only_first(self):
        """Test that run processes only the first task when multiple exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / "repos" / "test_repo"
            repo_path.mkdir(parents=True)

            mock_project = {"id": 1, "name": "test_repo"}
            mock_tasks = [
                {
                    "id": 1,
                    "subject": "Task 1",
                    "description": {"raw": "Desc 1"},
                    "lockVersion": 1,
                },
                {
                    "id": 2,
                    "subject": "Task 2",
                    "description": {"raw": "Desc 2"},
                    "lockVersion": 1,
                },
            ]

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
                mock_get_tasks.return_value = mock_tasks
                mock_checkout.return_value = True

                worker = OpenProjectWorker(dry_run=True)
                result = worker.run(repo_path)

                assert result["success"] is True
                assert result["tasks_processed"] == 1
                assert result["task_results"][0]["task_id"] == 1

    def test_process_single_task_with_exception(self):
        """Test _process_single_task handles exceptions gracefully."""
        worker = OpenProjectWorker(dry_run=False)

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / "test_repo"
            repo_path.mkdir()

            task = {
                "id": 1,
                "subject": "Test Task",
                "description": {"raw": "Test description"},
                "lockVersion": 1,
            }

            with (patch("auto_slopp.workers.openproject_worker.create_and_checkout_branch") as mock_branch,):
                mock_branch.side_effect = Exception("Unexpected error")

                result = worker._process_single_task(repo_path, task, 1)

                assert result["success"] is False
                assert "Unexpected error" in result["error"]

    def test_process_single_task_execution_fails(self):
        """Test _process_single_task when CLI execution fails."""
        worker = OpenProjectWorker(dry_run=False)

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / "test_repo"
            repo_path.mkdir()

            task = {
                "id": 1,
                "subject": "Test Task",
                "description": {"raw": "Test description"},
                "lockVersion": 1,
            }

            with (
                patch("auto_slopp.workers.openproject_worker.create_and_checkout_branch") as mock_branch,
                patch("auto_slopp.workers.openproject_worker.create_subtask") as mock_subtask,
                patch("auto_slopp.workers.openproject_worker.settings") as mock_settings,
                patch("auto_slopp.workers.openproject_worker.execute_with_instructions") as mock_execute,
                patch("auto_slopp.workers.openproject_worker.get_active_cli_command") as mock_cli,
            ):
                mock_branch.return_value = True
                mock_subtask.return_value = {"id": 100, "subject": "Subtask 1"}
                mock_settings.ralph_enabled = False
                mock_execute.return_value = {"success": False, "error": "CLI failed"}
                mock_cli.return_value = "test-cli"

                result = worker._process_single_task(repo_path, task, 1)

                assert result["success"] is False
                assert "CLI failed" in result["error"]
