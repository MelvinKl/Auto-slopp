"""Tests for VikunjaWorker._process_single_task."""

import tempfile
from pathlib import Path
from unittest.mock import patch

from auto_slopp.workers.vikunja_worker import VikunjaWorker


class TestVikunjaWorkerInit:
    """Tests for VikunjaWorker initialization."""

    def test_initialization_defaults(self):
        worker = VikunjaWorker()
        assert worker.agent_args == []
        assert worker.dry_run is False

    def test_initialization_custom(self):
        worker = VikunjaWorker(timeout=3600, agent_args=["--verbose"], dry_run=True)
        assert worker.timeout == 3600
        assert worker.agent_args == ["--verbose"]
        assert worker.dry_run is True


class TestVikunjaWorkerRun:
    """Tests for VikunjaWorker.run."""

    def test_run_nonexistent_repo(self):
        worker = VikunjaWorker(dry_run=True)
        result = worker.run(Path("/nonexistent/path"))
        assert result["success"] is False
        assert result["worker_name"] == "VikunjaWorker"

    def test_run_no_tasks(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)

            with (
                patch("auto_slopp.workers.vikunja_worker.checkout_branch_resilient") as mock_checkout,
                patch("auto_slopp.workers.vikunja_worker.find_or_create_project") as mock_project,
                patch("auto_slopp.workers.vikunja_worker.get_open_tasks_by_project") as mock_tasks,
            ):
                mock_checkout.return_value = True
                mock_project.return_value = {"id": 1, "title": repo_path.name}
                mock_tasks.return_value = []

                worker = VikunjaWorker(dry_run=False)
                result = worker.run(repo_path)

                assert result["success"] is True
                assert result["tasks_processed"] == 0
                assert result["task_results"] == []

    def test_run_project_not_found(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)

            with (
                patch("auto_slopp.workers.vikunja_worker.checkout_branch_resilient") as mock_checkout,
                patch("auto_slopp.workers.vikunja_worker.find_or_create_project") as mock_project,
            ):
                mock_checkout.return_value = True
                mock_project.return_value = None

                worker = VikunjaWorker(dry_run=False)
                result = worker.run(repo_path)

                assert result["success"] is False
                assert len(result["errors"]) > 0

    def test_run_tasks_sorted_by_priority(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)

            tasks = [
                {"id": 1, "title": "Low prio", "description": "", "priority": 1},
                {"id": 2, "title": "High prio", "description": "", "priority": 5},
                {"id": 3, "title": "Mid prio", "description": "", "priority": 3},
            ]

            with (
                patch("auto_slopp.workers.vikunja_worker.checkout_branch_resilient") as mock_checkout,
                patch("auto_slopp.workers.vikunja_worker.find_or_create_project") as mock_project,
                patch("auto_slopp.workers.vikunja_worker.get_open_tasks_by_project") as mock_tasks,
                patch.object(VikunjaWorker, "_process_single_task") as mock_process,
            ):
                mock_checkout.return_value = True
                mock_project.return_value = {"id": 1, "title": repo_path.name}
                mock_tasks.return_value = tasks
                mock_process.return_value = {
                    "success": True,
                    "openagent_executions": 1,
                    "tasks_completed": 1,
                }

                worker = VikunjaWorker(dry_run=False)
                worker.run(repo_path)

                processed_ids = [call.args[1]["id"] for call in mock_process.call_args_list]
                assert processed_ids == [2, 3, 1]


class TestProcessSingleTask:
    """Tests for VikunjaWorker._process_single_task."""

    def _make_task(self, task_id=1, title="Test Task", description="Test description", priority=0):
        return {
            "id": task_id,
            "title": title,
            "description": description,
            "priority": priority,
        }

    def test_dry_run_returns_success(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            worker = VikunjaWorker(dry_run=True)
            task = self._make_task()

            result = worker._process_single_task(repo_path, task)

            assert result["success"] is True
            assert result["openagent_executed"] is True
            assert result["task_id"] == 1
            assert result["task_title"] == "Test Task"

    def test_branch_creation_failure(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            worker = VikunjaWorker(dry_run=False)
            task = self._make_task()

            with (
                patch("auto_slopp.workers.vikunja_worker.create_and_checkout_branch") as mock_branch,
                patch("auto_slopp.workers.vikunja_worker.comment_on_task") as mock_comment,
                patch("auto_slopp.workers.vikunja_worker.update_task_status") as mock_status,
            ):
                mock_branch.return_value = False
                mock_comment.return_value = True
                mock_status.return_value = True

                result = worker._process_single_task(repo_path, task)

                assert result["success"] is False
                assert "Failed to create branch" in result["error"]
                assert result["task_commented"] is True
                assert result["task_failed"] is True
                mock_comment.assert_called_once()
                mock_status.assert_called_once_with(1, "failed")

    def test_cli_execution_failure(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            worker = VikunjaWorker(dry_run=False)
            task = self._make_task()

            with (
                patch("auto_slopp.workers.vikunja_worker.create_and_checkout_branch") as mock_branch,
                patch("auto_slopp.workers.vikunja_worker.execute_with_instructions") as mock_exec,
                patch("auto_slopp.workers.vikunja_worker.get_active_cli_command") as mock_cli,
                patch("auto_slopp.workers.vikunja_worker.comment_on_task") as mock_comment,
                patch("auto_slopp.workers.vikunja_worker.update_task_status") as mock_status,
            ):
                mock_branch.return_value = True
                mock_exec.return_value = {"success": False, "error": "Execution failed"}
                mock_cli.return_value = "slopmachine"
                mock_comment.return_value = True
                mock_status.return_value = True

                result = worker._process_single_task(repo_path, task)

                assert result["success"] is False
                assert result["openagent_executed"] is False
                assert result["task_commented"] is True
                assert result["task_failed"] is True
                mock_comment.assert_called_once()
                mock_status.assert_called_once_with(1, "failed")

    def test_no_changes_closes_task(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            worker = VikunjaWorker(dry_run=False)
            task = self._make_task()

            with (
                patch("auto_slopp.workers.vikunja_worker.create_and_checkout_branch") as mock_branch,
                patch("auto_slopp.workers.vikunja_worker.execute_with_instructions") as mock_exec,
                patch("auto_slopp.workers.vikunja_worker.get_current_branch") as mock_branch_name,
                patch("auto_slopp.workers.vikunja_worker.comment_on_task") as mock_comment,
                patch("auto_slopp.workers.vikunja_worker.update_task_status") as mock_status,
            ):
                mock_branch.return_value = True
                mock_exec.return_value = {"success": True}
                mock_branch_name.return_value = "main"
                mock_comment.return_value = True
                mock_status.return_value = True

                result = worker._process_single_task(repo_path, task)

                assert result["success"] is True
                assert result["no_changes"] is True
                assert result["task_completed"] is True
                mock_status.assert_called_once_with(1, "done")

    def test_successful_task_with_changes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            worker = VikunjaWorker(dry_run=False)
            task = self._make_task()

            with (
                patch("auto_slopp.workers.vikunja_worker.create_and_checkout_branch") as mock_branch,
                patch("auto_slopp.workers.vikunja_worker.execute_with_instructions") as mock_exec,
                patch("auto_slopp.workers.vikunja_worker.get_current_branch") as mock_branch_name,
                patch("auto_slopp.workers.vikunja_worker.push_to_remote") as mock_push,
                patch("auto_slopp.workers.vikunja_worker.update_task_status") as mock_status,
                patch("auto_slopp.workers.vikunja_worker.comment_on_task") as mock_comment,
            ):
                mock_branch.return_value = True
                mock_exec.return_value = {"success": True}
                mock_branch_name.return_value = "ai/task-1-test-task"
                mock_push.return_value = (True, "pushed")
                mock_status.return_value = True
                mock_comment.return_value = True

                result = worker._process_single_task(repo_path, task)

                assert result["success"] is True
                assert result["openagent_executed"] is True
                assert result["openagent_executions"] == 1
                mock_status.assert_called_once_with(1, "done")
                mock_comment.assert_called_once()

    def test_push_failure(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            worker = VikunjaWorker(dry_run=False)
            task = self._make_task()

            with (
                patch("auto_slopp.workers.vikunja_worker.create_and_checkout_branch") as mock_branch,
                patch("auto_slopp.workers.vikunja_worker.execute_with_instructions") as mock_exec,
                patch("auto_slopp.workers.vikunja_worker.get_current_branch") as mock_branch_name,
                patch("auto_slopp.workers.vikunja_worker.push_to_remote") as mock_push,
                patch("auto_slopp.workers.vikunja_worker.comment_on_task") as mock_comment,
                patch("auto_slopp.workers.vikunja_worker.update_task_status") as mock_status,
            ):
                mock_branch.return_value = True
                mock_exec.return_value = {"success": True}
                mock_branch_name.return_value = "ai/task-1-test-task"
                mock_push.return_value = (False, "push failed")
                mock_comment.return_value = True
                mock_status.return_value = True

                result = worker._process_single_task(repo_path, task)

                assert result["success"] is False
                assert "Failed to push branch" in result["error"]
                assert result["task_commented"] is True
                assert result["task_failed"] is True
                mock_comment.assert_called_once()
                mock_status.assert_called_once_with(1, "failed")

    def test_task_with_none_description(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            worker = VikunjaWorker(dry_run=True)
            task = {"id": 5, "title": "No desc", "description": None, "priority": 0}

            result = worker._process_single_task(repo_path, task)

            assert result["success"] is True
            assert result["task_id"] == 5

    def test_exception_handling_updates_task_status(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            worker = VikunjaWorker(dry_run=False)
            task = self._make_task()

            with (
                patch("auto_slopp.workers.vikunja_worker.create_and_checkout_branch") as mock_branch,
                patch("auto_slopp.workers.vikunja_worker.comment_on_task") as mock_comment,
                patch("auto_slopp.workers.vikunja_worker.update_task_status") as mock_status,
            ):
                mock_branch.side_effect = Exception("Unexpected error")
                mock_comment.return_value = True
                mock_status.return_value = True

                result = worker._process_single_task(repo_path, task)

                assert result["success"] is False
                assert result["error"] == "Unexpected error"
                assert result["task_commented"] is True
                assert result["task_failed"] is True
                mock_comment.assert_called_once()
                mock_status.assert_called_once_with(1, "failed")


class TestBuildInstructions:
    """Tests for VikunjaWorker._build_instructions."""

    def test_includes_title_and_description(self):
        worker = VikunjaWorker()
        instructions = worker._build_instructions("My Task", "Do something")
        assert "My Task" in instructions
        assert "Do something" in instructions

    def test_with_branch_name(self):
        worker = VikunjaWorker()
        instructions = worker._build_instructions("My Task", "desc", branch_name="ai/task-1-my-task")
        assert "already on branch 'ai/task-1-my-task'" in instructions
        assert "Create a new branch" not in instructions

    def test_without_branch_name(self):
        worker = VikunjaWorker()
        instructions = worker._build_instructions("My Task", "desc")
        assert "Create a new branch" in instructions
        assert "ai/" in instructions

    def test_empty_description(self):
        worker = VikunjaWorker()
        instructions = worker._build_instructions("My Task", "")
        assert "My Task" in instructions

    def test_includes_plan(self):
        worker = VikunjaWorker()
        instructions = worker._build_instructions("Task", "Body")
        assert "Plan:" in instructions
        assert "make test" in instructions
        assert "make lint" in instructions
