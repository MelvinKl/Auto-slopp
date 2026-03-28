"""Tests for unified IssueWorker."""

import tempfile
from pathlib import Path
from unittest.mock import patch

from auto_slopp.workers.github_task_source import GitHubTaskSource
from auto_slopp.workers.issue_worker import IssueWorker
from auto_slopp.workers.task_source import Task, TaskSource
from auto_slopp.workers.vikunja_task_source import VikunjaTaskSource


class MockTaskSource(TaskSource):
    """Mock TaskSource for testing."""

    def __init__(self, tasks=None):
        self.tasks = tasks or []
        self.on_task_start_called = False
        self.on_task_complete_called = False
        self.on_task_failure_called = False
        self.on_no_changes_called = False
        self.on_max_iterations_called = False

    def get_tasks(self, repo_path: Path) -> list[Task]:
        return self.tasks

    def get_branch_name(self, task: Task) -> str:
        return f"ai/task-{task.id}"

    def get_ralph_file_prefix(self) -> str:
        return "test"

    def get_pr_title(self, task: Task) -> str:
        return f"Task #{task.id}: {task.title}"

    def get_default_pr_body(self, task: Task) -> str:
        return f"PR for {task.title}"

    def on_task_start(self, task: Task, branch_name: str) -> None:
        self.on_task_start_called = True

    def on_task_complete(self, task: Task, branch_name: str, pr_url: str) -> None:
        self.on_task_complete_called = True

    def on_task_failure(self, task: Task, error: str) -> None:
        self.on_task_failure_called = True

    def on_no_changes(self, task: Task) -> None:
        self.on_no_changes_called = True

    def on_max_iterations_reached(self, task: Task, steps_completed: int, total_steps: int, error: str) -> None:
        self.on_max_iterations_called = True


class TestIssueWorker:
    """Tests for the unified IssueWorker."""

    def test_initialization_with_task_source(self):
        """Test that IssueWorker can be initialized with a TaskSource."""
        task_source = MockTaskSource()
        worker = IssueWorker(task_source=task_source)
        assert worker.task_source == task_source

    def test_initialization_with_timeout(self):
        """Test that timeout is properly set."""
        task_source = MockTaskSource()
        worker = IssueWorker(task_source=task_source, timeout=3600)
        assert worker.timeout == 3600

    def test_initialization_with_agent_args(self):
        """Test that agent_args are properly set."""
        task_source = MockTaskSource()
        worker = IssueWorker(task_source=task_source, agent_args=["--verbose"])
        assert worker.agent_args == ["--verbose"]

    def test_initialization_with_dry_run(self):
        """Test that dry_run is properly set."""
        task_source = MockTaskSource()
        worker = IssueWorker(task_source=task_source, dry_run=True)
        assert worker.dry_run is True

    @patch("auto_slopp.workers.issue_worker.settings")
    def test_ralph_executor_initialization(self, mock_settings):
        """Test that RalphExecutor is initialized with correct parameters."""
        mock_settings.github_issue_step_max_iterations = 10
        task_source = MockTaskSource()
        worker = IssueWorker(task_source=task_source)
        assert worker.ralph_executor is not None
        assert worker.ralph_executor.file_prefix == "test"

    def test_run_with_nonexistent_path(self):
        """Test that run handles non-existent repository path."""
        task_source = MockTaskSource()
        worker = IssueWorker(task_source=task_source)
        result = worker.run(Path("/nonexistent/path"))
        assert result["success"] is False
        assert "does not exist" in result["error"]

    def test_run_with_no_tasks(self):
        """Test that run handles case with no tasks."""
        with tempfile.TemporaryDirectory() as temp_dir:
            task_source = MockTaskSource(tasks=[])
            worker = IssueWorker(task_source=task_source, dry_run=True)
            result = worker.run(Path(temp_dir))
            assert result["success"] is True
            assert result["tasks_processed"] == 0

    @patch("auto_slopp.workers.issue_worker.checkout_branch_resilient")
    @patch("auto_slopp.workers.issue_worker.create_and_checkout_branch")
    @patch("auto_slopp.workers.issue_worker.has_changes")
    @patch("auto_slopp.workers.issue_worker.get_current_branch")
    @patch("auto_slopp.workers.issue_worker.settings")
    @patch("auto_slopp.workers.issue_worker.get_active_cli_command")
    def test_run_dry_run(
        self,
        mock_cli,
        mock_settings,
        mock_current_branch,
        mock_has_changes,
        mock_create,
        mock_checkout,
    ):
        """Test that dry_run mode skips actual execution."""
        mock_cli.return_value = "opencode"
        mock_settings.ralph_enabled = False
        task_source = MockTaskSource(tasks=[Task(id=1, title="Test", body="")])
        worker = IssueWorker(task_source=task_source, dry_run=True)
        result = worker.run(Path("/tmp"))
        assert result["success"] is True
        assert result["tasks_processed"] == 1
        assert result["openagent_executions"] == 0
        mock_create.assert_not_called()

    @patch("auto_slopp.workers.issue_worker.checkout_branch_resilient")
    @patch("auto_slopp.workers.issue_worker.create_and_checkout_branch")
    @patch("auto_slopp.workers.issue_worker.has_changes")
    @patch("auto_slopp.workers.issue_worker.get_current_branch")
    @patch("auto_slopp.workers.issue_worker.settings")
    @patch("auto_slopp.workers.issue_worker.push_to_remote")
    @patch("auto_slopp.workers.issue_worker.create_pull_request")
    @patch("auto_slopp.workers.issue_worker.get_pr_for_branch")
    @patch("auto_slopp.workers.issue_worker.execute_with_instructions")
    @patch("auto_slopp.workers.issue_worker.get_active_cli_command")
    def test_run_with_no_changes(
        self,
        mock_cli,
        mock_execute,
        mock_get_pr,
        mock_create_pr,
        mock_push,
        mock_settings,
        mock_current_branch,
        mock_has_changes,
        mock_create_branch,
        mock_checkout,
    ):
        """Test that run handles case with no changes."""
        mock_cli.return_value = "opencode"
        mock_settings.ralph_enabled = False
        mock_checkout.return_value = True
        mock_create_branch.return_value = True
        mock_execute.return_value = {"success": True}
        mock_has_changes.return_value = False
        mock_current_branch.return_value = "main"
        task_source = MockTaskSource(tasks=[Task(id=1, title="Test", body="")])
        worker = IssueWorker(task_source=task_source, dry_run=False)
        result = worker.run(Path("/tmp"))
        assert result["success"] is True
        assert result["tasks_processed"] == 1
        assert result["task_results"][0]["no_changes"] is True
        assert task_source.on_no_changes_called is True
        mock_push.assert_not_called()

    @patch("auto_slopp.workers.issue_worker.checkout_branch_resilient")
    @patch("auto_slopp.workers.issue_worker.create_and_checkout_branch")
    @patch("auto_slopp.workers.issue_worker.has_changes")
    @patch("auto_slopp.workers.issue_worker.get_current_branch")
    @patch("auto_slopp.workers.issue_worker.settings")
    @patch("auto_slopp.workers.issue_worker.push_to_remote")
    @patch("auto_slopp.workers.issue_worker.create_pull_request")
    @patch("auto_slopp.workers.issue_worker.get_pr_for_branch")
    @patch("auto_slopp.workers.issue_worker.execute_with_instructions")
    @patch("auto_slopp.workers.issue_worker.get_active_cli_command")
    def test_run_with_successful_execution(
        self,
        mock_cli,
        mock_execute,
        mock_get_pr,
        mock_create_pr,
        mock_push,
        mock_settings,
        mock_current_branch,
        mock_has_changes,
        mock_create_branch,
        mock_checkout,
    ):
        """Test that run handles successful execution with PR creation."""
        mock_cli.return_value = "opencode"
        mock_settings.ralph_enabled = False
        mock_checkout.return_value = True
        mock_create_branch.return_value = True
        mock_execute.return_value = {"success": True}
        mock_has_changes.return_value = True
        mock_current_branch.return_value = "ai/task-1"
        mock_push.return_value = (True, "")
        mock_get_pr.return_value = None
        mock_create_pr.return_value = {"url": "https://github.com/test/pr/1"}
        task_source = MockTaskSource(tasks=[Task(id=1, title="Test", body="")])
        worker = IssueWorker(task_source=task_source, dry_run=False)
        result = worker.run(Path("/tmp"))
        assert result["success"] is True
        assert result["tasks_processed"] == 1
        assert result["prs_created"] == 1
        assert result["tasks_completed"] == 1
        assert task_source.on_task_complete_called is True
        mock_create_pr.assert_called_once()

    @patch("auto_slopp.workers.issue_worker.checkout_branch_resilient")
    @patch("auto_slopp.workers.issue_worker.settings")
    def test_run_with_checkout_failure(self, mock_settings, mock_checkout):
        """Test that run handles main branch checkout failure."""
        mock_settings.ralph_enabled = False
        mock_checkout.return_value = False
        task_source = MockTaskSource(tasks=[Task(id=1, title="Test", body="")])
        worker = IssueWorker(task_source=task_source, dry_run=False)
        result = worker.run(Path("/tmp"))
        assert result["success"] is False
        assert result["repositories_with_errors"] == 1

    @patch("auto_slopp.workers.issue_worker.checkout_branch_resilient")
    @patch("auto_slopp.workers.issue_worker.settings")
    def test_run_with_existing_pr(self, mock_settings, mock_checkout):
        """Test that run handles existing PR."""
        mock_settings.ralph_enabled = False
        mock_checkout.return_value = True
        task_source = MockTaskSource(tasks=[Task(id=1, title="Test", body="")])
        worker = IssueWorker(task_source=task_source, dry_run=True)
        result = worker.run(Path("/tmp"))
        assert result["success"] is True

    def test_build_instructions_with_branch_name(self):
        """Test that _build_instructions includes branch name when provided."""
        task_source = MockTaskSource()
        worker = IssueWorker(task_source=task_source)
        instructions = worker._build_instructions(
            task_title="Fix Bug",
            task_body="Description",
            comments=["Comment 1"],
            branch_name="ai/task-1",
        )
        assert "Fix Bug" in instructions
        assert "Description" in instructions
        assert "Comment 1" in instructions
        assert "You are already on branch 'ai/task-1'" in instructions

    def test_build_instructions_without_branch_name(self):
        """Test that _build_instructions works without branch name."""
        task_source = MockTaskSource()
        worker = IssueWorker(task_source=task_source)
        instructions = worker._build_instructions(
            task_title="Fix Bug",
            task_body="Description",
            comments=[],
        )
        assert "Fix Bug" in instructions
        assert "Description" in instructions
        assert "Create a new branch that starts with ai/" in instructions

    @patch("auto_slopp.workers.issue_worker.checkout_branch_resilient")
    @patch("auto_slopp.workers.issue_worker.create_and_checkout_branch")
    @patch("auto_slopp.workers.issue_worker.has_changes")
    @patch("auto_slopp.workers.issue_worker.get_current_branch")
    @patch("auto_slopp.workers.issue_worker.settings")
    @patch("auto_slopp.workers.issue_worker.push_to_remote")
    @patch("auto_slopp.workers.issue_worker.create_pull_request")
    @patch("auto_slopp.workers.issue_worker.get_pr_for_branch")
    @patch("auto_slopp.workers.issue_worker.execute_with_instructions")
    @patch("auto_slopp.workers.issue_worker.get_active_cli_command")
    def test_multiple_tasks_processing(
        self,
        mock_cli,
        mock_execute,
        mock_get_pr,
        mock_create_pr,
        mock_push,
        mock_settings,
        mock_current_branch,
        mock_has_changes,
        mock_create_branch,
        mock_checkout,
    ):
        """Test that run processes multiple tasks correctly."""
        mock_cli.return_value = "opencode"
        mock_settings.ralph_enabled = False
        mock_checkout.return_value = True
        mock_create_branch.return_value = True
        mock_execute.return_value = {"success": True}
        mock_has_changes.return_value = True
        # Return task branch instead of main so PR can be created
        mock_current_branch.return_value = "ai/task-1"
        mock_push.return_value = (True, "")
        mock_get_pr.return_value = None
        mock_create_pr.return_value = {"url": "https://github.com/test/pr/1"}
        task_source = MockTaskSource(
            tasks=[
                Task(id=1, title="Task 1", body=""),
                Task(id=2, title="Task 2", body=""),
            ]
        )
        worker = IssueWorker(task_source=task_source, dry_run=False)
        result = worker.run(Path("/tmp"))
        assert result["success"] is True
        assert result["tasks_processed"] == 2
        assert result["prs_created"] == 2

    @patch("auto_slopp.workers.issue_worker.checkout_branch_resilient")
    @patch("auto_slopp.workers.issue_worker.create_and_checkout_branch")
    @patch("auto_slopp.workers.issue_worker.settings")
    @patch("auto_slopp.workers.issue_worker.execute_with_instructions")
    @patch("auto_slopp.workers.issue_worker.get_active_cli_command")
    def test_task_execution_failure(self, mock_cli, mock_execute, mock_settings, mock_create_branch, mock_checkout):
        """Test that run handles task execution failure and calls on_task_failure."""
        mock_cli.return_value = "opencode"
        mock_settings.ralph_enabled = False
        mock_checkout.return_value = True
        mock_create_branch.return_value = True
        mock_execute.return_value = {"success": False, "error": "Execution failed"}
        task_source = MockTaskSource(tasks=[Task(id=1, title="Test", body="")])
        worker = IssueWorker(task_source=task_source, dry_run=False)
        result = worker.run(Path("/tmp"))
        assert result["success"] is True
        assert result["tasks_processed"] == 0
        assert len(result["task_results"]) == 1
        assert result["task_results"][0]["success"] is False
        assert task_source.on_task_failure_called is True

    @patch("auto_slopp.workers.issue_worker.checkout_branch_resilient")
    @patch("auto_slopp.workers.issue_worker.create_and_checkout_branch")
    @patch("auto_slopp.workers.issue_worker.settings")
    def test_ralph_executor_max_iterations_reached(self, mock_settings, mock_create_branch, mock_checkout):
        """Test that on_max_iterations_reached is called when Ralph reaches max iterations."""
        mock_settings.ralph_enabled = True
        mock_settings.github_issue_step_max_iterations = 10
        mock_checkout.return_value = True
        mock_create_branch.return_value = True
        task_source = MockTaskSource(tasks=[Task(id=1, title="Test", body="")])
        worker = IssueWorker(task_source=task_source, dry_run=False)
        # Mock the RalphExecutor.execute method to simulate max iterations reached
        worker.ralph_executor.execute = lambda *args, **kwargs: {
            "success": False,
            "loops_executed": 10,
            "steps_completed": 8,
            "total_steps": 15,
            "max_loops_reached": True,
            "error": "Max iterations reached",
        }
        result = worker.run(Path("/tmp"))
        assert result["success"] is True
        assert result["tasks_processed"] == 0
        assert len(result["task_results"]) == 1
        assert result["task_results"][0]["success"] is False
        assert result["task_results"][0]["ralph_loops_executed"] == 10
        assert task_source.on_max_iterations_called is True

    @patch("auto_slopp.workers.issue_worker.checkout_branch_resilient")
    @patch("auto_slopp.workers.issue_worker.create_and_checkout_branch")
    @patch("auto_slopp.workers.issue_worker.settings")
    def test_branch_creation_failure(self, mock_settings, mock_create_branch, mock_checkout):
        """Test that run handles branch creation failure and calls on_task_failure."""
        mock_settings.ralph_enabled = False
        mock_checkout.return_value = True
        mock_create_branch.return_value = False
        task_source = MockTaskSource(tasks=[Task(id=1, title="Test", body="")])
        worker = IssueWorker(task_source=task_source, dry_run=False)
        result = worker.run(Path("/tmp"))
        assert result["success"] is True
        assert result["tasks_processed"] == 0
        assert len(result["task_results"]) == 1
        assert "Failed to create branch" in result["task_results"][0]["error"]
        assert "task #1" in result["task_results"][0]["error"]
        assert task_source.on_task_failure_called is True

    @patch("auto_slopp.workers.issue_worker.settings")
    def test_create_results_dict(self, mock_settings):
        """Test that _create_results_dict creates proper result structure."""
        task_source = MockTaskSource()
        worker = IssueWorker(task_source=task_source)
        result = worker._create_results_dict(123.45, Path("/test/path"))
        assert result["worker_name"] == "IssueWorker"
        assert result["timestamp"] == 123.45
        assert result["repo_path"] == "/test/path"
        assert result["repositories_processed"] == 1
        assert result["tasks_processed"] == 0
        assert result["success"] is True

    @patch("auto_slopp.workers.issue_worker.settings")
    def test_create_error_result(self, mock_settings):
        """Test that _create_error_result creates proper error structure."""
        task_source = MockTaskSource()
        worker = IssueWorker(task_source=task_source)
        result = worker._create_error_result(123.45, Path("/test/path"), "Test error")
        assert result["success"] is False
        assert result["error"] == "Test error"
        assert result["repositories_with_errors"] == 1
        assert result["repositories_processed"] == 0

    @patch("auto_slopp.workers.issue_worker.checkout_branch_resilient")
    @patch("auto_slopp.workers.issue_worker.create_and_checkout_branch")
    @patch("auto_slopp.workers.issue_worker.get_current_branch")
    @patch("auto_slopp.workers.issue_worker.settings")
    @patch("auto_slopp.workers.issue_worker.push_to_remote")
    @patch("auto_slopp.workers.issue_worker.get_active_cli_command")
    def test_push_failure_calls_on_task_failure(
        self,
        mock_cli,
        mock_push,
        mock_settings,
        mock_current_branch,
        mock_create_branch,
        mock_checkout,
    ):
        """Test that push failure calls on_task_failure."""
        mock_cli.return_value = "opencode"
        mock_settings.ralph_enabled = True
        mock_settings.github_issue_step_max_iterations = 10
        mock_checkout.return_value = True
        mock_create_branch.return_value = True
        mock_current_branch.return_value = "ai/task-1"
        mock_push.return_value = (False, "Push rejected")
        task_source = MockTaskSource(tasks=[Task(id=1, title="Test", body="")])
        worker = IssueWorker(task_source=task_source, dry_run=False)
        worker.ralph_executor.execute = lambda *args, **kwargs: {
            "success": True,
            "loops_executed": 1,
            "steps_completed": 3,
            "total_steps": 3,
        }
        result = worker.run(Path("/tmp"))
        assert result["tasks_processed"] == 0
        assert "Failed to push" in result["task_results"][0]["error"]
        assert "task #1" in result["task_results"][0]["error"]
        assert task_source.on_task_failure_called is True

    @patch("auto_slopp.workers.issue_worker.checkout_branch_resilient")
    @patch("auto_slopp.workers.issue_worker.create_and_checkout_branch")
    @patch("auto_slopp.workers.issue_worker.settings")
    def test_exception_calls_on_task_failure(self, mock_settings, mock_create_branch, mock_checkout):
        """Test that unexpected exceptions call on_task_failure."""
        mock_settings.ralph_enabled = False
        mock_checkout.return_value = True
        mock_create_branch.side_effect = Exception("Unexpected error")
        task_source = MockTaskSource(tasks=[Task(id=1, title="Test", body="")])
        worker = IssueWorker(task_source=task_source, dry_run=False)
        result = worker.run(Path("/tmp"))
        assert result["tasks_processed"] == 0
        assert result["task_results"][0]["error"] == "Unexpected error"
        assert task_source.on_task_failure_called is True

    @patch("auto_slopp.workers.issue_worker.checkout_branch_resilient")
    @patch("auto_slopp.workers.issue_worker.create_and_checkout_branch")
    @patch("auto_slopp.workers.issue_worker.get_current_branch")
    @patch("auto_slopp.workers.issue_worker.settings")
    @patch("auto_slopp.workers.issue_worker.push_to_remote")
    @patch("auto_slopp.workers.issue_worker.create_pull_request")
    @patch("auto_slopp.workers.issue_worker.get_pr_for_branch")
    @patch("auto_slopp.workers.issue_worker.execute_with_instructions")
    @patch("auto_slopp.workers.issue_worker.get_active_cli_command")
    def test_pr_creation_failure_calls_on_task_failure(
        self,
        mock_cli,
        mock_execute,
        mock_get_pr,
        mock_create_pr,
        mock_push,
        mock_settings,
        mock_current_branch,
        mock_create_branch,
        mock_checkout,
    ):
        """Test that PR creation failure calls on_task_failure."""
        mock_cli.return_value = "opencode"
        mock_settings.ralph_enabled = False
        mock_checkout.return_value = True
        mock_create_branch.return_value = True
        mock_execute.return_value = {"success": True}
        mock_current_branch.return_value = "ai/task-1"
        mock_push.return_value = (True, "")
        mock_get_pr.return_value = None
        mock_create_pr.return_value = None
        task_source = MockTaskSource(tasks=[Task(id=1, title="Test", body="")])
        worker = IssueWorker(task_source=task_source, dry_run=False)
        result = worker.run(Path("/tmp"))
        assert result["tasks_processed"] == 0
        assert result["task_results"][0]["success"] is False
        assert task_source.on_task_failure_called is True
        assert task_source.on_task_complete_called is False

    @patch("auto_slopp.workers.issue_worker.checkout_branch_resilient")
    @patch("auto_slopp.workers.issue_worker.create_and_checkout_branch")
    @patch("auto_slopp.workers.issue_worker.get_current_branch")
    @patch("auto_slopp.workers.issue_worker.settings")
    @patch("auto_slopp.workers.issue_worker.push_to_remote")
    @patch("auto_slopp.workers.issue_worker.create_pull_request")
    @patch("auto_slopp.workers.issue_worker.get_pr_for_branch")
    @patch("auto_slopp.workers.issue_worker.execute_with_instructions")
    @patch("auto_slopp.workers.issue_worker.get_active_cli_command")
    def test_empty_pr_url_calls_on_task_failure(
        self,
        mock_cli,
        mock_execute,
        mock_get_pr,
        mock_create_pr,
        mock_push,
        mock_settings,
        mock_current_branch,
        mock_create_branch,
        mock_checkout,
    ):
        """Test that empty PR URL prevents marking task as complete."""
        mock_cli.return_value = "opencode"
        mock_settings.ralph_enabled = False
        mock_checkout.return_value = True
        mock_create_branch.return_value = True
        mock_execute.return_value = {"success": True}
        mock_current_branch.return_value = "ai/task-1"
        mock_push.return_value = (True, "")
        mock_get_pr.return_value = {"state": "OPEN", "url": ""}
        task_source = MockTaskSource(tasks=[Task(id=1, title="Test", body="")])
        worker = IssueWorker(task_source=task_source, dry_run=False)
        result = worker.run(Path("/tmp"))
        assert result["task_results"][0]["success"] is False
        assert "no PR URL available" in result["task_results"][0]["error"]
        assert "Task #1" in result["task_results"][0]["error"]
        assert task_source.on_task_failure_called is True
        assert task_source.on_task_complete_called is False

    @patch("auto_slopp.workers.issue_worker.checkout_branch_resilient")
    @patch("auto_slopp.workers.issue_worker.create_and_checkout_branch")
    @patch("auto_slopp.workers.issue_worker.get_current_branch")
    @patch("auto_slopp.workers.issue_worker.settings")
    @patch("auto_slopp.workers.issue_worker.push_to_remote")
    @patch("auto_slopp.workers.issue_worker.create_pull_request")
    @patch("auto_slopp.workers.issue_worker.get_pr_for_branch")
    @patch("auto_slopp.workers.issue_worker.execute_with_instructions")
    @patch("auto_slopp.workers.issue_worker.get_active_cli_command")
    def test_existing_open_pr_reused(
        self,
        mock_cli,
        mock_execute,
        mock_get_pr,
        mock_create_pr,
        mock_push,
        mock_settings,
        mock_current_branch,
        mock_create_branch,
        mock_checkout,
    ):
        """Test that an existing open PR is reused instead of creating a new one."""
        mock_cli.return_value = "opencode"
        mock_settings.ralph_enabled = False
        mock_checkout.return_value = True
        mock_create_branch.return_value = True
        mock_execute.return_value = {"success": True}
        mock_current_branch.return_value = "ai/task-1"
        mock_push.return_value = (True, "")
        mock_get_pr.return_value = {
            "state": "OPEN",
            "url": "https://github.com/test/pr/99",
        }
        task_source = MockTaskSource(tasks=[Task(id=1, title="Test", body="")])
        worker = IssueWorker(task_source=task_source, dry_run=False)
        result = worker.run(Path("/tmp"))
        assert result["task_results"][0]["success"] is True
        assert result["task_results"][0]["pr_url"] == "https://github.com/test/pr/99"
        assert result["prs_created"] == 1
        assert task_source.on_task_complete_called is True
        mock_create_pr.assert_not_called()

    @patch("auto_slopp.workers.issue_worker.checkout_branch_resilient")
    @patch("auto_slopp.workers.issue_worker.create_and_checkout_branch")
    @patch("auto_slopp.workers.issue_worker.get_current_branch")
    @patch("auto_slopp.workers.issue_worker.settings")
    @patch("auto_slopp.workers.issue_worker.push_to_remote")
    @patch("auto_slopp.workers.issue_worker.create_pull_request")
    @patch("auto_slopp.workers.issue_worker.get_pr_for_branch")
    @patch("auto_slopp.workers.issue_worker.execute_with_instructions")
    @patch("auto_slopp.workers.issue_worker.get_active_cli_command")
    def test_pr_creation_failure_fallback_to_existing_pr(
        self,
        mock_cli,
        mock_execute,
        mock_get_pr,
        mock_create_pr,
        mock_push,
        mock_settings,
        mock_current_branch,
        mock_create_branch,
        mock_checkout,
    ):
        """Test that when PR creation fails, fallback to existing PR succeeds."""
        mock_cli.return_value = "opencode"
        mock_settings.ralph_enabled = False
        mock_checkout.return_value = True
        mock_create_branch.return_value = True
        mock_execute.return_value = {"success": True}
        mock_current_branch.return_value = "ai/task-1"
        mock_push.return_value = (True, "")
        # First call returns None (no existing open PR), second call finds one after create fails
        mock_get_pr.side_effect = [
            None,
            {"state": "OPEN", "url": "https://github.com/test/pr/42"},
        ]
        mock_create_pr.return_value = None  # PR creation fails
        task_source = MockTaskSource(tasks=[Task(id=1, title="Test", body="")])
        worker = IssueWorker(task_source=task_source, dry_run=False)
        result = worker.run(Path("/tmp"))
        assert result["task_results"][0]["success"] is True
        assert result["task_results"][0]["pr_url"] == "https://github.com/test/pr/42"
        assert result["prs_created"] == 1
        assert task_source.on_task_complete_called is True

    @patch("auto_slopp.workers.issue_worker.checkout_branch_resilient")
    @patch("auto_slopp.workers.issue_worker.create_and_checkout_branch")
    @patch("auto_slopp.workers.issue_worker.settings")
    @patch("auto_slopp.workers.issue_worker.execute_with_instructions")
    @patch("auto_slopp.workers.issue_worker.get_active_cli_command")
    def test_on_task_start_called_before_branch_creation(
        self,
        mock_cli,
        mock_execute,
        mock_settings,
        mock_create_branch,
        mock_checkout,
    ):
        """Test that on_task_start is called before branch creation."""
        mock_cli.return_value = "opencode"
        mock_settings.ralph_enabled = False
        mock_checkout.return_value = True
        mock_create_branch.return_value = False  # Fail early to keep test simple
        task_source = MockTaskSource(tasks=[Task(id=1, title="Test", body="")])
        worker = IssueWorker(task_source=task_source, dry_run=False)
        worker.run(Path("/tmp"))
        assert task_source.on_task_start_called is True

    @patch("auto_slopp.workers.issue_worker.checkout_branch_resilient")
    @patch("auto_slopp.workers.issue_worker.create_and_checkout_branch")
    @patch("auto_slopp.workers.issue_worker.get_current_branch")
    @patch("auto_slopp.workers.issue_worker.settings")
    @patch("auto_slopp.workers.issue_worker.push_to_remote")
    @patch("auto_slopp.workers.issue_worker.create_pull_request")
    @patch("auto_slopp.workers.issue_worker.get_pr_for_branch")
    @patch("auto_slopp.workers.issue_worker.execute_with_instructions")
    @patch("auto_slopp.workers.issue_worker.get_active_cli_command")
    def test_correct_arguments_to_branch_push_pr(
        self,
        mock_cli,
        mock_execute,
        mock_get_pr,
        mock_create_pr,
        mock_push,
        mock_settings,
        mock_current_branch,
        mock_create_branch,
        mock_checkout,
    ):
        """Test that branch creation, push, and PR creation receive correct arguments."""
        mock_cli.return_value = "opencode"
        mock_settings.ralph_enabled = False
        mock_checkout.return_value = True
        mock_create_branch.return_value = True
        mock_execute.return_value = {"success": True}
        mock_current_branch.return_value = "ai/task-5"
        mock_push.return_value = (True, "")
        mock_get_pr.return_value = None
        mock_create_pr.return_value = {"url": "https://github.com/test/pr/1"}
        task_source = MockTaskSource(tasks=[Task(id=5, title="Fix login bug", body="Details")])
        worker = IssueWorker(task_source=task_source, dry_run=False)
        worker.run(Path("/tmp"))
        mock_create_branch.assert_called_once_with(Path("/tmp"), "ai/task-5", base_branch="main")
        mock_push.assert_called_once_with(Path("/tmp"), remote="origin", branch="ai/task-5")
        mock_create_pr.assert_called_once()
        call_kwargs = mock_create_pr.call_args
        assert call_kwargs[1]["title"] == "Task #5: Fix login bug"
        assert call_kwargs[1]["head"] == "ai/task-5"
        assert call_kwargs[1]["base"] == "main"

    @patch("auto_slopp.workers.issue_worker.checkout_branch_resilient")
    @patch("auto_slopp.workers.issue_worker.create_and_checkout_branch")
    @patch("auto_slopp.workers.issue_worker.get_current_branch")
    @patch("auto_slopp.workers.issue_worker.settings")
    @patch("auto_slopp.workers.issue_worker.push_to_remote")
    @patch("auto_slopp.workers.issue_worker.create_pull_request")
    @patch("auto_slopp.workers.issue_worker.get_pr_for_branch")
    @patch("auto_slopp.workers.issue_worker.execute_with_instructions")
    @patch("auto_slopp.workers.issue_worker.get_active_cli_command")
    def test_github_issue_worker_uses_correct_pr_title_format(
        self,
        mock_cli,
        mock_execute,
        mock_get_pr,
        mock_create_pr,
        mock_push,
        mock_settings,
        mock_current_branch,
        mock_create_branch,
        mock_checkout,
    ):
        """Test that GitHubIssueWorker uses correct PR title format for GitHub tasks."""
        mock_cli.return_value = "opencode"
        mock_settings.ralph_enabled = False
        mock_checkout.return_value = True
        mock_create_branch.return_value = True
        mock_execute.return_value = {"success": True}
        mock_current_branch.return_value = "ai/task-1"
        mock_push.return_value = (True, "")
        mock_get_pr.return_value = None
        mock_create_pr.return_value = {"url": "https://github.com/test/pr/1"}

        # Create IssueWorker with GitHubTaskSource
        task_source = GitHubTaskSource()
        worker = IssueWorker(task_source=task_source, dry_run=False)

        # Run the worker
        task = Task(id=123, title="Fix bug", body="")
        task_source.get_tasks = lambda _: [task]
        result = worker.run(Path("/tmp"))

        # Verify that create_pull_request was called with correct title format
        assert result["success"] is True
        mock_create_pr.assert_called_once()
        call_kwargs = mock_create_pr.call_args
        assert call_kwargs[1]["title"] == "#123: Fix bug"

    @patch("auto_slopp.workers.issue_worker.checkout_branch_resilient")
    @patch("auto_slopp.workers.issue_worker.create_and_checkout_branch")
    @patch("auto_slopp.workers.issue_worker.get_current_branch")
    @patch("auto_slopp.workers.issue_worker.settings")
    @patch("auto_slopp.workers.issue_worker.push_to_remote")
    @patch("auto_slopp.workers.issue_worker.create_pull_request")
    @patch("auto_slopp.workers.issue_worker.get_pr_for_branch")
    @patch("auto_slopp.workers.issue_worker.execute_with_instructions")
    @patch("auto_slopp.workers.issue_worker.get_active_cli_command")
    @patch("auto_slopp.workers.vikunja_task_source.commit")
    def test_vikunja_issue_worker_uses_correct_pr_title_format(
        self,
        mock_commit,
        mock_cli,
        mock_execute,
        mock_get_pr,
        mock_create_pr,
        mock_push,
        mock_settings,
        mock_current_branch,
        mock_create_branch,
        mock_checkout,
    ):
        """Test that VikunjaIssueWorker uses correct PR title format for Vikunja tasks."""
        mock_cli.return_value = "opencode"
        mock_settings.ralph_enabled = False
        mock_checkout.return_value = True
        mock_create_branch.return_value = True
        mock_execute.return_value = {"success": True}
        mock_current_branch.return_value = "ai/task-1"
        mock_push.return_value = (True, "")
        mock_get_pr.return_value = None
        mock_create_pr.return_value = {"url": "https://github.com/test/pr/1"}

        # Create IssueWorker with VikunjaTaskSource
        task_source = VikunjaTaskSource()
        worker = IssueWorker(task_source=task_source, dry_run=False)

        # Run the worker
        task = Task(id=456, title="Add feature", body="")
        task_source.get_tasks = lambda _: [task]
        result = worker.run(Path("/tmp"))

        # Verify that create_pull_request was called with correct title format
        assert result["success"] is True
        mock_create_pr.assert_called_once()
        call_kwargs = mock_create_pr.call_args
        assert call_kwargs[1]["title"] == "Vikunja Task #456: Add feature"

    @patch("auto_slopp.workers.issue_worker.checkout_branch_resilient")
    @patch("auto_slopp.workers.issue_worker.create_and_checkout_branch")
    @patch("auto_slopp.workers.issue_worker.get_current_branch")
    @patch("auto_slopp.workers.issue_worker.settings")
    @patch("auto_slopp.workers.issue_worker.push_to_remote")
    @patch("auto_slopp.workers.issue_worker.create_pull_request")
    @patch("auto_slopp.workers.issue_worker.get_pr_for_branch")
    @patch("auto_slopp.workers.issue_worker.execute_with_instructions")
    @patch("auto_slopp.workers.issue_worker.get_active_cli_command")
    def test_on_task_complete_receives_correct_pr_url(
        self,
        mock_cli,
        mock_execute,
        mock_get_pr,
        mock_create_pr,
        mock_push,
        mock_settings,
        mock_current_branch,
        mock_create_branch,
        mock_checkout,
    ):
        """Test that on_task_complete is called with the correct PR URL."""
        mock_cli.return_value = "opencode"
        mock_settings.ralph_enabled = False
        mock_checkout.return_value = True
        mock_create_branch.return_value = True
        mock_execute.return_value = {"success": True}
        mock_current_branch.return_value = "ai/task-1"
        mock_push.return_value = (True, "")
        mock_get_pr.return_value = None
        mock_create_pr.return_value = {"url": "https://github.com/test/pr/7"}

        task = Task(id=1, title="Test", body="")
        captured = {}

        class CapturingTaskSource(MockTaskSource):
            def on_task_complete(self, task, branch_name, pr_url):
                captured["branch_name"] = branch_name
                captured["pr_url"] = pr_url
                super().on_task_complete(task, branch_name, pr_url)

        task_source = CapturingTaskSource(tasks=[task])
        worker = IssueWorker(task_source=task_source, dry_run=False)
        worker.run(Path("/tmp"))
        assert captured["pr_url"] == "https://github.com/test/pr/7"
        assert captured["branch_name"] == "ai/task-1"

    @patch("auto_slopp.workers.issue_worker.checkout_branch_resilient")
    @patch("auto_slopp.workers.issue_worker.create_and_checkout_branch")
    @patch("auto_slopp.workers.issue_worker.get_current_branch")
    @patch("auto_slopp.workers.issue_worker.settings")
    @patch("auto_slopp.workers.issue_worker.push_to_remote")
    @patch("auto_slopp.workers.issue_worker.create_pull_request")
    @patch("auto_slopp.workers.issue_worker.get_pr_for_branch")
    @patch("auto_slopp.workers.issue_worker.get_active_cli_command")
    def test_ralph_enabled_success_with_push_and_pr(
        self,
        mock_cli,
        mock_get_pr,
        mock_create_pr,
        mock_push,
        mock_settings,
        mock_current_branch,
        mock_create_branch,
        mock_checkout,
    ):
        """Test successful Ralph-enabled workflow through push and PR creation."""
        mock_cli.return_value = "opencode"
        mock_settings.ralph_enabled = True
        mock_settings.github_issue_step_max_iterations = 10
        mock_checkout.return_value = True
        mock_create_branch.return_value = True
        mock_current_branch.return_value = "ai/task-1"
        mock_push.return_value = (True, "")
        mock_get_pr.return_value = None
        mock_create_pr.return_value = {"url": "https://github.com/test/pr/1"}
        task_source = MockTaskSource(tasks=[Task(id=1, title="Test", body="")])
        worker = IssueWorker(task_source=task_source, dry_run=False)
        worker.ralph_executor.execute = lambda *args, **kwargs: {
            "success": True,
            "loops_executed": 2,
            "steps_completed": 5,
            "total_steps": 5,
        }
        # Mock _generate_pr_body_from_task_file to avoid file system access
        worker._generate_pr_body_from_task_file = lambda **kwargs: "PR body"
        result = worker.run(Path("/tmp"))
        assert result["success"] is True
        assert result["tasks_processed"] == 1
        assert result["prs_created"] == 1
        assert result["tasks_completed"] == 1
        assert result["task_results"][0]["ralph_loops_executed"] == 2
        assert result["task_results"][0]["ralph_steps_completed"] == 5
        assert task_source.on_task_complete_called is True
        mock_push.assert_called_once()
        mock_create_pr.assert_called_once()
