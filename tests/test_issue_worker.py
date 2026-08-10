"""Tests for unified IssueWorker."""

import subprocess
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
        self.on_skip_called = False
        self.on_max_iterations_called = False
        self.on_skip_called = False
        self.skip_reason = None
        self.findings = None  # To store findings passed to on_task_complete

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

    def on_task_complete(self, task: Task, branch_name: str, pr_url: str, findings=None) -> None:
        self.on_task_complete_called = True
        self.findings = findings

    def on_task_failure(self, task: Task, error: str) -> None:
        self.on_task_failure_called = True

    def on_no_changes(self, task: Task) -> None:
        self.on_no_changes_called = True

    def on_skip(self, task: Task, reason: str) -> None:
        self.on_skip_called = True

    def on_max_iterations_reached(self, task: Task, steps_completed: int, total_steps: int, error: str) -> None:
        self.on_max_iterations_called = True

    def on_skip(self, task: Task, reason: str) -> None:
        self.on_skip_called = True
        self.skip_reason = reason


class CapturingTaskSourceWithFindings(MockTaskSource):
    """Mock TaskSource that captures the findings argument passed to on_task_complete."""

    def __init__(self, tasks=None):
        super().__init__(tasks)
        self.captured_findings = None

    def on_task_complete(self, task: Task, branch_name: str, pr_url: str, findings=None) -> None:
        super().on_task_complete(task, branch_name, pr_url, findings)
        self.captured_findings = findings


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

    @patch("auto_slopp.workers.issue_worker.commit_and_push_changes")
    @patch("auto_slopp.workers.issue_worker.checkout_branch_resilient")
    @patch("auto_slopp.workers.issue_worker.create_and_checkout_branch")
    @patch("auto_slopp.workers.issue_worker.has_changes")
    @patch("auto_slopp.workers.issue_worker.get_current_branch")
    @patch("auto_slopp.workers.issue_worker.push_to_remote")
    @patch("auto_slopp.workers.issue_worker.get_pr_for_branch")
    @patch("auto_slopp.workers.issue_worker.create_pull_request")
    @patch("auto_slopp.workers.issue_worker.execute_with_instructions")
    @patch("auto_slopp.workers.issue_worker.get_active_cli_command")
    @patch("auto_slopp.workers.issue_worker.settings")
    @patch("auto_slopp.workers.issue_worker.get_commits_ahead_of_branch")
    def test_pr_creation_failure_no_fallback(
        self,
        mock_commits_ahead,
        mock_settings,
        mock_active_cli,
        mock_execute,
        mock_create_pr,
        mock_get_pr,
        mock_push,
        mock_current_branch,
        mock_has_changes,
        mock_create_branch,
        mock_checkout,
        mock_commit_push,
    ):
        """Test that when PR creation fails and no existing open PR, task fails."""
        mock_commits_ahead.return_value = 1
        mock_settings.ralph_enabled = False
        mock_active_cli.return_value = "opencode"
        mock_has_changes.return_value = True
        mock_commit_push.return_value = (True, None)
        mock_checkout.return_value = True
        mock_create_branch.return_value = True
        mock_execute.return_value = {"success": True}
        mock_current_branch.return_value = "ai/task-1"
        mock_push.return_value = (True, "")
        mock_get_pr.return_value = None
        mock_create_pr.return_value = None  # PR creation fails
        task_source = MockTaskSource(tasks=[Task(id=1, title="Test", body="")])
        worker = IssueWorker(task_source=task_source, dry_run=False)
        result = worker.run(Path("/tmp"))
        assert result["task_results"][0]["success"] is False
        assert "Failed to create pull request" in result["task_results"][0]["error"]
        assert task_source.on_task_failure_called is True
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

    @patch("auto_slopp.workers.issue_worker.commit_and_push_changes")
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
    @patch("auto_slopp.workers.issue_worker.get_commits_ahead_of_branch")
    def test_multiple_tasks_processing(
        self,
        mock_commits_ahead,
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
        mock_commit_push,
    ):
        """Test that run processes multiple tasks correctly."""
        mock_commits_ahead.return_value = 1
        mock_cli.return_value = "opencode"
        mock_settings.ralph_enabled = False
        mock_commit_push.return_value = (True, None)
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
    def test_ralph_max_iterations_llm_unavailable_calls_on_skip(self, mock_settings, mock_create_branch, mock_checkout):
        """Test that on_skip is called (not on_max_iterations_reached) when LLM is unavailable during Ralph loop.

        This is the core integration test for the fix: when Ralph reaches max iterations
        due to LLM unavailability (e.g., timeout), the task should be skipped for retry
        rather than permanently dropped.
        """
        mock_settings.ralph_enabled = True
        mock_settings.github_issue_step_max_iterations = 10
        mock_checkout.return_value = True
        mock_create_branch.return_value = True
        task_source = MockTaskSource(tasks=[Task(id=1, title="Test", body="")])
        worker = IssueWorker(task_source=task_source, dry_run=False)

        # Mock RalphExecutor.execute to return max_loops_reached
        worker.ralph_executor.execute = lambda *args, **kwargs: {
            "success": False,
            "loops_executed": 10,
            "steps_completed": 8,
            "total_steps": 15,
            "max_loops_reached": True,
            "error": "Maximum iterations (10) reached before all steps completed",
        }
        # Simulate that the LLM timed out during the loop (the key scenario the fix addresses)
        worker.ralph_executor._last_iteration_failure_reason = "timed out waiting for response"

        result = worker.run(Path("/tmp"))
        assert result["success"] is True
        assert result["tasks_processed"] == 0
        assert result["tasks_skipped"] == 1
        assert len(result["task_results"]) == 1
        assert result["task_results"][0]["success"] is True
        assert result["task_results"][0]["skipped"] is True
        assert "skip_reason" in result["task_results"][0]
        # on_skip should be called, NOT on_max_iterations_reached
        assert task_source.on_skip_called is True
        assert task_source.on_max_iterations_called is False

    @patch("auto_slopp.workers.issue_worker.checkout_branch_resilient")
    @patch("auto_slopp.workers.issue_worker.create_and_checkout_branch")
    @patch("auto_slopp.workers.issue_worker.settings")
    def test_ralph_max_iterations_genuine_exhaustion_calls_on_max_iterations(
        self, mock_settings, mock_create_branch, mock_checkout
    ):
        """Test that on_max_iterations_reached is still called for genuine iteration exhaustion.

        When the LLM is available but the task simply can't be completed within the
        iteration budget, the task should be dropped via on_max_iterations_reached.
        """
        mock_settings.ralph_enabled = True
        mock_settings.github_issue_step_max_iterations = 10
        mock_checkout.return_value = True
        mock_create_branch.return_value = True
        task_source = MockTaskSource(tasks=[Task(id=1, title="Test", body="")])
        worker = IssueWorker(task_source=task_source, dry_run=False)

        # Mock RalphExecutor.execute to return max_loops_reached
        worker.ralph_executor.execute = lambda *args, **kwargs: {
            "success": False,
            "loops_executed": 10,
            "steps_completed": 8,
            "total_steps": 15,
            "max_loops_reached": True,
            "error": "Maximum iterations (10) reached before all steps completed",
        }
        # No LLM unavailability – genuine iteration exhaustion
        worker.ralph_executor._last_iteration_failure_reason = None
        worker.ralph_executor._last_error = "Step implementation failed: syntax error in code"
        result = worker.run(Path("/tmp"))
        assert result["success"] is True
        assert result["tasks_processed"] == 0
        assert len(result["task_results"]) == 1
        assert result["task_results"][0]["success"] is False
        # on_max_iterations_reached should be called, NOT on_skip
        assert task_source.on_max_iterations_called is True
        assert task_source.on_skip_called is False

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

    @patch("auto_slopp.workers.issue_worker.commit_and_push_changes")
    @patch("auto_slopp.workers.issue_worker.checkout_branch_resilient")
    @patch("auto_slopp.workers.issue_worker.create_and_checkout_branch")
    @patch("auto_slopp.workers.issue_worker.has_changes")
    @patch("auto_slopp.workers.issue_worker.get_current_branch")
    @patch("auto_slopp.workers.issue_worker.settings")
    @patch("auto_slopp.workers.issue_worker.push_to_remote")
    @patch("auto_slopp.workers.issue_worker.get_active_cli_command")
    @patch("auto_slopp.workers.issue_worker.get_commits_ahead_of_branch")
    def test_push_failure_calls_on_task_failure(
        self,
        mock_commits_ahead,
        mock_cli,
        mock_push,
        mock_settings,
        mock_current_branch,
        mock_has_changes,
        mock_create_branch,
        mock_checkout,
        mock_commit_push,
    ):
        """Test that push failure calls on_task_failure."""
        mock_cli.return_value = "opencode"
        mock_settings.ralph_enabled = True
        mock_settings.github_issue_step_max_iterations = 10
        mock_has_changes.return_value = True
        mock_commit_push.return_value = (True, None)
        mock_checkout.return_value = True
        mock_create_branch.return_value = True
        mock_current_branch.return_value = "ai/task-1"
        mock_push.return_value = (False, "Push rejected")
        mock_commits_ahead.return_value = 1  # Simulate commits ahead of main
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

    @patch("auto_slopp.workers.issue_worker.commit_and_push_changes")
    @patch("auto_slopp.workers.issue_worker.checkout_branch_resilient")
    @patch("auto_slopp.workers.issue_worker.create_and_checkout_branch")
    @patch("auto_slopp.workers.issue_worker.has_changes")
    @patch("auto_slopp.workers.issue_worker.get_current_branch")
    @patch("auto_slopp.workers.issue_worker.settings")
    @patch("auto_slopp.workers.issue_worker.push_to_remote")
    @patch("auto_slopp.workers.issue_worker.create_pull_request")
    @patch("auto_slopp.workers.issue_worker.get_pr_for_branch")
    @patch("auto_slopp.workers.issue_worker.get_commits_ahead_of_branch")
    @patch("auto_slopp.workers.issue_worker.get_active_cli_command")
    def test_commits_during_ralph_loop_still_creates_pr(
        self,
        mock_cli,
        mock_commits_ahead,
        mock_get_pr,
        mock_create_pr,
        mock_push,
        mock_settings,
        mock_current_branch,
        mock_has_changes,
        mock_create_branch,
        mock_checkout,
        mock_commit_push,
    ):
        """Test that PR is created when commits are made during Ralph loop (has_changes=False but commits ahead)."""
        mock_cli.return_value = "opencode"
        mock_settings.ralph_enabled = True
        mock_settings.github_issue_step_max_iterations = 10
        # has_changes returns False because Ralph already committed everything
        mock_has_changes.return_value = False
        # But there ARE commits ahead of main (committed during Ralph loop)
        mock_commits_ahead.return_value = 1
        mock_commit_push.return_value = (True, None)
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
            "loops_executed": 1,
            "steps_completed": 3,
            "total_steps": 3,
        }
        result = worker.run(Path("/tmp"))
        # Should process the task and create a PR (not close as "no changes")
        assert result["tasks_processed"] == 1
        assert result["prs_created"] == 1
        assert result["task_results"][0]["pr_created"] is True
        assert task_source.on_task_complete_called is True
        assert task_source.on_no_changes_called is False

    @patch("auto_slopp.workers.issue_worker.commit_and_push_changes")
    @patch("auto_slopp.workers.issue_worker.checkout_branch_resilient")
    @patch("auto_slopp.workers.issue_worker.create_and_checkout_branch")
    @patch("auto_slopp.workers.issue_worker.get_current_branch")
    @patch("auto_slopp.workers.issue_worker.settings")
    @patch("auto_slopp.workers.issue_worker.get_commits_ahead_of_branch")
    @patch("auto_slopp.workers.issue_worker.get_active_cli_command")
    def test_no_commits_ahead_closes_as_no_changes(
        self,
        mock_cli,
        mock_commits_ahead,
        mock_settings,
        mock_current_branch,
        mock_create_branch,
        mock_checkout,
        mock_commit_push,
    ):
        """Test that issue is closed as no_changes when there are no commits ahead of main."""
        mock_cli.return_value = "opencode"
        mock_settings.ralph_enabled = True
        mock_settings.github_issue_step_max_iterations = 10
        # No commits ahead of main - Ralph made no changes
        mock_commits_ahead.return_value = 0
        mock_checkout.return_value = True
        mock_create_branch.return_value = True
        mock_current_branch.return_value = "ai/task-1"
        task_source = MockTaskSource(tasks=[Task(id=1, title="Test", body="")])
        worker = IssueWorker(task_source=task_source, dry_run=False)
        worker.ralph_executor.execute = lambda *args, **kwargs: {
            "success": True,
            "loops_executed": 1,
            "steps_completed": 0,
            "total_steps": 3,
        }
        result = worker.run(Path("/tmp"))
        # Should close as no_changes (no commits were made)
        assert result["tasks_processed"] == 1
        assert result["task_results"][0]["no_changes"] is True
        assert task_source.on_no_changes_called is True
        assert task_source.on_task_complete_called is False

    @patch("auto_slopp.workers.issue_worker.commit_and_push_changes")
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
    @patch("auto_slopp.workers.issue_worker.get_commits_ahead_of_branch")
    def test_process_single_task_passes_condensed_comments_directly(
        self,
        mock_commits_ahead,
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
        mock_commit_push,
    ):
        """Test that _process_single_task() passes task.comments directly without re-condensing or replacing with placeholder.

        When GitHubTaskSource._condense_comments() returns [condensed_summary], the worker
        should pass this directly to the agent without modification. The old fallback logic
        that replaced task.comments with a placeholder like
        'Only one comment present; no additional comments to condense.' has been removed.
        """
        mock_commits_ahead.return_value = 1
        mock_cli.return_value = "opencode"
        mock_settings.ralph_enabled = False
        mock_commit_push.return_value = (True, None)
        mock_checkout.return_value = True
        mock_create_branch.return_value = True
        mock_execute.return_value = {"success": True}
        mock_has_changes.return_value = True
        mock_current_branch.return_value = "ai/task-1"
        mock_push.return_value = (True, "")
        mock_get_pr.return_value = None
        mock_create_pr.return_value = {"url": "https://github.com/test/pr/1"}

        # Simulate a task where comments have already been condensed by GitHubTaskSource
        # This is what happens when _condense_comments() returns [condensed_summary]
        condensed_comment = "Condensed summary of all comments from multiple authors"
        task = Task(id=1, title="Test", body="Test body", comments=[condensed_comment])
        task_source = MockTaskSource(tasks=[task])
        worker = IssueWorker(task_source=task_source, dry_run=False)
        result = worker.run(Path("/tmp"))

        assert result["success"] is True
        assert result["tasks_processed"] == 1
        # Verify execute_with_instructions was called
        mock_execute.assert_called_once()
        # Verify the instructions contain the condensed comment (not a placeholder)
        call_args = mock_execute.call_args
        instructions = call_args.args[0]
        assert condensed_comment in instructions
        # Verify no placeholder text was used
        assert "Only one comment present" not in instructions
        assert "no additional comments to condense" not in instructions

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

    @patch("auto_slopp.workers.issue_worker.commit_and_push_changes")
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
    @patch("auto_slopp.workers.issue_worker.get_commits_ahead_of_branch")
    def test_empty_pr_url_calls_on_task_failure(
        self,
        mock_commits_ahead,
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
        mock_commit_push,
    ):
        """Test that empty PR URL prevents marking task as complete."""
        mock_commits_ahead.return_value = 1
        mock_cli.return_value = "opencode"
        mock_settings.ralph_enabled = False
        mock_has_changes.return_value = True
        mock_commit_push.return_value = (True, None)
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

    @patch("auto_slopp.workers.issue_worker.commit_and_push_changes")
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
    @patch("auto_slopp.workers.issue_worker.get_commits_ahead_of_branch")
    def test_existing_open_pr_reused(
        self,
        mock_commits_ahead,
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
        mock_commit_push,
    ):
        """Test that an existing open PR is reused instead of creating a new one."""
        mock_commits_ahead.return_value = 1
        mock_cli.return_value = "opencode"
        mock_settings.ralph_enabled = False
        mock_has_changes.return_value = True
        mock_commit_push.return_value = (True, None)
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

    @patch("auto_slopp.workers.issue_worker.commit_and_push_changes")
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
    @patch("auto_slopp.workers.issue_worker.get_commits_ahead_of_branch")
    def test_run_with_successful_execution(
        self,
        mock_commits_ahead,
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
        mock_commit_push,
    ):
        """Test that run handles successful execution with PR creation."""
        mock_commits_ahead.return_value = 1
        mock_cli.return_value = "opencode"
        mock_settings.ralph_enabled = False
        mock_commit_push.return_value = (True, None)
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

    @patch("auto_slopp.workers.issue_worker.commit_and_push_changes")
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
    @patch("auto_slopp.workers.issue_worker.get_commits_ahead_of_branch")
    def test_github_issue_worker_uses_correct_pr_title_format(
        self,
        mock_commits_ahead,
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
        mock_commit_push,
    ):
        """Test that GitHubIssueWorker uses correct PR title format for GitHub tasks."""
        mock_commits_ahead.return_value = 1
        mock_cli.return_value = "opencode"
        mock_settings.ralph_enabled = False
        mock_has_changes.return_value = True
        mock_commit_push.return_value = (True, None)
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

    @patch("auto_slopp.workers.issue_worker.commit_and_push_changes")
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
    @patch("auto_slopp.workers.issue_worker.get_commits_ahead_of_branch")
    @patch("auto_slopp.workers.vikunja_task_source.commit")
    def test_vikunja_issue_worker_uses_correct_pr_title_format(
        self,
        mock_vikunja_commit,
        mock_commits_ahead,
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
        mock_commit_push,
    ):
        """Test that VikunjaIssueWorker uses correct PR title format for Vikunja tasks."""
        mock_commits_ahead.return_value = 1
        mock_cli.return_value = "opencode"
        mock_settings.ralph_enabled = False
        mock_has_changes.return_value = True
        mock_commit_push.return_value = (True, None)
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

    @patch("auto_slopp.workers.issue_worker.commit_and_push_changes")
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
    @patch("auto_slopp.workers.issue_worker.get_commits_ahead_of_branch")
    def test_on_task_complete_receives_correct_pr_url(
        self,
        mock_commits_ahead,
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
        mock_commit_push,
    ):
        """Test that on_task_complete is called with the correct PR URL."""
        mock_commits_ahead.return_value = 1
        mock_cli.return_value = "opencode"
        mock_settings.ralph_enabled = False
        mock_has_changes.return_value = True
        mock_commit_push.return_value = (True, None)
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

    @patch("auto_slopp.workers.issue_worker.commit_and_push_changes")
    @patch("auto_slopp.workers.issue_worker.checkout_branch_resilient")
    @patch("auto_slopp.workers.issue_worker.create_and_checkout_branch")
    @patch("auto_slopp.workers.issue_worker.has_changes")
    @patch("auto_slopp.workers.issue_worker.get_current_branch")
    @patch("auto_slopp.workers.issue_worker.settings")
    @patch("auto_slopp.workers.issue_worker.push_to_remote")
    @patch("auto_slopp.workers.issue_worker.create_pull_request")
    @patch("auto_slopp.workers.issue_worker.get_pr_for_branch")
    @patch("auto_slopp.workers.issue_worker.get_active_cli_command")
    @patch("auto_slopp.workers.issue_worker.get_commits_ahead_of_branch")
    def test_ralph_enabled_success_with_push_and_pr(
        self,
        mock_commits_ahead,
        mock_cli,
        mock_get_pr,
        mock_create_pr,
        mock_push,
        mock_settings,
        mock_current_branch,
        mock_has_changes,
        mock_create_branch,
        mock_checkout,
        mock_commit_push,
    ):
        """Test successful Ralph-enabled workflow through push and PR creation."""
        mock_commits_ahead.return_value = 1
        mock_cli.return_value = "opencode"
        mock_settings.ralph_enabled = True
        mock_settings.github_issue_step_max_iterations = 10
        mock_has_changes.return_value = True
        mock_commit_push.return_value = (True, None)
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

    @patch("auto_slopp.workers.github_task_source.get_issue_comments")
    def test_comment_condensation(self, mock_get_comments):
        """Test that GitHubTaskSource._condense_comments properly condenses comments."""
        task_source = GitHubTaskSource()

        # Test case 1: No comments
        mock_get_comments.return_value = []
        result = task_source._condense_comments(Path("/tmp"), 1, "author", "MelvinKl")
        assert result == []

        # Test case 2: One comment
        mock_get_comments.return_value = [{"id": 1, "body": "Only comment", "author": {"login": "author"}}]
        result = task_source._condense_comments(Path("/tmp"), 2, "author", "MelvinKl")
        assert result == ["Only comment"]

        # Test case 3: Multiple comments - should call CLI to condense
        mock_get_comments.return_value = [
            {"id": 1, "body": "First comment", "author": {"login": "author"}},
            {"id": 2, "body": "Second comment", "author": {"login": "author"}},
            {"id": 3, "body": "Third comment", "author": {"login": "author"}},
        ]
        with patch("auto_slopp.workers.github_task_source.execute_with_instructions") as mock_execute:
            mock_execute.return_value = {"success": True, "stdout": "Condensed summary"}
            with patch("auto_slopp.workers.github_task_source.comment_on_issue"):
                with patch("auto_slopp.workers.github_task_source.delete_issue_comment"):
                    result = task_source._condense_comments(Path("/tmp"), 3, "author", "MelvinKl")
                    assert result == ["Condensed summary"]

    def test_comments_pass_through_unchanged(self):
        """Test that task.comments are passed through without modification.

        Comment condensation is handled by GitHubTaskSource._condense_comments(),
        not by IssueWorker. IssueWorker should pass comments directly to the agent.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test case 1: No comments
            task_source = MockTaskSource(tasks=[Task(id=1, title="Test", body="", comments=[])])
            worker = IssueWorker(task_source=task_source, dry_run=True)
            worker.run(Path(temp_dir))
            assert task_source.tasks[0].comments == []

            # Test case 2: One comment
            task_source = MockTaskSource(tasks=[Task(id=2, title="Test", body="", comments=["Only comment"])])
            worker = IssueWorker(task_source=task_source, dry_run=True)
            worker.run(Path(temp_dir))
            assert task_source.tasks[0].comments == ["Only comment"]

            # Test case 3: Multiple comments
            comments = ["First comment", "Second comment", "Third comment"]
            task_source = MockTaskSource(tasks=[Task(id=3, title="Test", body="", comments=comments)])
            worker = IssueWorker(task_source=task_source, dry_run=True)
            worker.run(Path(temp_dir))
            assert task_source.tasks[0].comments == comments

    @patch("auto_slopp.workers.issue_worker.ensure_ralph_in_gitignore")
    @patch("auto_slopp.workers.issue_worker.checkout_branch_resilient")
    @patch("auto_slopp.workers.issue_worker.create_and_checkout_branch")
    @patch("auto_slopp.workers.issue_worker.settings")
    def test_ensure_ralph_in_gitignore_called(
        self, mock_settings, mock_create_branch, mock_checkout, mock_ensure_gitignore
    ):
        """Test that ensure_ralph_in_gitignore is called after branch creation and before Ralph execution."""
        mock_settings.ralph_enabled = True
        mock_settings.github_issue_step_max_iterations = 10
        mock_checkout.return_value = True
        mock_create_branch.return_value = True
        task_source = MockTaskSource(tasks=[Task(id=1, title="Test", body="")])
        worker = IssueWorker(task_source=task_source, dry_run=False)
        worker.ralph_executor.execute = lambda *args, **kwargs: {
            "success": True,
            "loops_executed": 1,
            "steps_completed": 3,
            "total_steps": 3,
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            worker.run(Path(temp_dir))

        # Verify ensure_ralph_in_gitignore was called
        mock_ensure_gitignore.assert_called_once()
        call_args = mock_ensure_gitignore.call_args
        assert call_args[0][0] == Path(temp_dir)

    @patch("auto_slopp.workers.issue_worker.ensure_ralph_in_gitignore")
    @patch("auto_slopp.workers.issue_worker.checkout_branch_resilient")
    @patch("auto_slopp.workers.issue_worker.create_and_checkout_branch")
    @patch("auto_slopp.workers.issue_worker.settings")
    def test_ensure_ralph_in_gitignore_no_warning_on_success(
        self, mock_settings, mock_create_branch, mock_checkout, mock_ensure_gitignore, caplog
    ):
        """Test that no warning is logged when ensure_ralph_in_gitignore returns True."""
        mock_settings.ralph_enabled = True
        mock_settings.github_issue_step_max_iterations = 10
        mock_checkout.return_value = True
        mock_create_branch.return_value = True
        mock_ensure_gitignore.return_value = True  # Simulate success
        task_source = MockTaskSource(tasks=[Task(id=1, title="Test", body="")])
        worker = IssueWorker(task_source=task_source, dry_run=False)
        worker.ralph_executor.execute = lambda *args, **kwargs: {
            "success": True,
            "loops_executed": 1,
            "steps_completed": 3,
            "total_steps": 3,
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            with caplog.at_level("WARNING", logger="auto_slopp.workers.issue_worker"):
                worker.run(Path(temp_dir))

        # No warning should be logged when ensure_ralph_in_gitignore succeeds
        gitignore_warnings = [r for r in caplog.records if "Failed to ensure .ralph in .gitignore" in r.getMessage()]
        assert len(gitignore_warnings) == 0

    @patch("auto_slopp.workers.issue_worker.checkout_branch_resilient")
    @patch("auto_slopp.workers.issue_worker.create_and_checkout_branch")
    @patch("auto_slopp.workers.issue_worker.settings")
    def test_llm_unavailable_calls_on_skip_ralph(self, mock_settings, mock_create_branch, mock_checkout):
        """Test that on_skip is called when LLM is unavailable during Ralph loop."""
        mock_settings.ralph_enabled = True
        mock_settings.github_issue_step_max_iterations = 10
        mock_checkout.return_value = True
        mock_create_branch.return_value = True
        task_source = MockTaskSource(tasks=[Task(id=1, title="Test", body="")])
        worker = IssueWorker(task_source=task_source, dry_run=False)
        worker.ralph_executor.execute = lambda *args, **kwargs: {
            "success": False,
            "loops_executed": 1,
            "steps_completed": 2,
            "total_steps": 5,
            "max_loops_reached": True,
            "error": "LLM timed out waiting for response",
        }
        worker.ralph_executor._is_llm_unavailable = lambda: True
        result = worker.run(Path("/tmp"))
        assert result["success"] is True
        assert result["tasks_processed"] == 0
        assert result["tasks_skipped"] == 1
        assert len(result["task_results"]) == 1
        assert result["task_results"][0]["success"] is True
        assert result["task_results"][0]["skipped"] is True
        assert "skip_reason" in result["task_results"][0]
        assert task_source.on_skip_called is True
        assert task_source.on_task_failure_called is False

    @patch("auto_slopp.workers.issue_worker.execute_with_instructions")
    @patch("auto_slopp.workers.issue_worker.get_active_cli_command")
    @patch("auto_slopp.workers.issue_worker.checkout_branch_resilient")
    @patch("auto_slopp.workers.issue_worker.create_and_checkout_branch")
    @patch("auto_slopp.workers.issue_worker.settings")
    def test_llm_unavailable_calls_on_skip_cli(
        self, mock_settings, mock_create_branch, mock_checkout, mock_cli, mock_execute
    ):
        """Test that on_skip is called when LLM is unavailable during CLI execution."""
        mock_settings.ralph_enabled = False
        mock_checkout.return_value = True
        mock_create_branch.return_value = True
        mock_cli.return_value = "opencode"
        mock_execute.return_value = {"success": False, "error": "LLM unavailable"}
        task_source = MockTaskSource(tasks=[Task(id=1, title="Test", body="")])
        worker = IssueWorker(task_source=task_source, dry_run=False)
        result = worker.run(Path("/tmp"))
        assert result["success"] is True
        assert result["tasks_processed"] == 0
        assert result["tasks_skipped"] == 1
        assert len(result["task_results"]) == 1
        assert result["task_results"][0]["success"] is True
        assert result["task_results"][0]["skipped"] is True
        assert "skip_reason" in result["task_results"][0]
        assert task_source.on_skip_called is True
        assert task_source.on_task_failure_called is False

    @patch("auto_slopp.workers.issue_worker.checkout_branch_resilient")
    @patch("auto_slopp.workers.issue_worker.create_and_checkout_branch")
    @patch("auto_slopp.workers.issue_worker.settings")
    def test_ralph_non_llm_error_calls_on_task_failure(self, mock_settings, mock_create_branch, mock_checkout):
        """Test that non-LLM errors still call on_task_failure, not on_skip."""
        mock_settings.ralph_enabled = True
        mock_settings.github_issue_step_max_iterations = 10
        mock_checkout.return_value = True
        mock_create_branch.return_value = True
        task_source = MockTaskSource(tasks=[Task(id=1, title="Test", body="")])
        worker = IssueWorker(task_source=task_source, dry_run=False)
        worker.ralph_executor.execute = lambda *args, **kwargs: {
            "success": False,
            "loops_executed": 1,
            "steps_completed": 2,
            "total_steps": 5,
            "max_loops_reached": False,
            "error": "Git push failed: permission denied",
        }
        result = worker.run(Path("/tmp"))
        assert result["success"] is True
        assert result["tasks_processed"] == 0
        assert result["tasks_skipped"] == 0
        assert len(result["task_results"]) == 1
        assert result["task_results"][0]["success"] is False
        assert task_source.on_task_failure_called is True
        assert task_source.on_skip_called is False

    def test_is_llm_unavailable(self):
        """Test that _is_llm_unavailable correctly detects LLM unavailability with specific patterns."""
        task_source = MockTaskSource()
        worker = IssueWorker(task_source=task_source)
        # Timeout patterns
        assert worker._is_llm_unavailable("LLM timed out waiting for response") is True
        assert worker._is_llm_unavailable("Request timed out") is True
        # Connection errors
        assert worker._is_llm_unavailable("Connection refused") is True
        assert worker._is_llm_unavailable("Connection reset by peer") is True
        # Rate limiting
        assert worker._is_llm_unavailable("Rate limit exceeded") is True
        assert worker._is_llm_unavailable("Too many requests") is True
        # HTTP 5xx errors
        assert worker._is_llm_unavailable("Service unavailable") is True
        assert worker._is_llm_unavailable("Gateway timeout") is True
        assert worker._is_llm_unavailable("HTTP 503 Service Unavailable") is True
        assert worker._is_llm_unavailable("HTTP 502 Bad Gateway") is True
        assert worker._is_llm_unavailable("HTTP 504 Gateway Timeout") is True
        assert worker._is_llm_unavailable("Internal server error") is True
        assert worker._is_llm_unavailable("LLM unavailable") is True
        # Non-LLM errors should return False
        assert worker._is_llm_unavailable("Git push failed") is False
        assert worker._is_llm_unavailable("Permission denied") is False
        assert worker._is_llm_unavailable("no cli configuration found") is False
        assert worker._is_llm_unavailable("LLM is unavailable") is True  # Shared pattern from constants
        assert worker._is_llm_unavailable("") is False

    @patch("auto_slopp.workers.issue_worker.settings")
    def test_is_llm_unavailable_via_cli_states(self, mock_settings):
        """Test that _is_llm_unavailable checks _cli_states against cli_configurations."""
        import time

        from auto_slopp.utils.cli_executor import _cli_states

        task_source = MockTaskSource()
        worker = IssueWorker(task_source=task_source)

        num_configs = 3
        mock_settings.cli_configurations = [type("Config", (), {"name": f"config{i}"}) for i in range(num_configs)]

        # Save original _cli_states
        original_cli_states = _cli_states.copy()

        try:
            # Test 1: All configs inactive, cooldown not expired -> True
            now = time.time()
            _cli_states.clear()
            _cli_states.update({i: {"active": False, "cooldown_until": now + 3600} for i in range(num_configs)})
            assert worker._is_llm_unavailable("") is True

            # Test 2: All configs active -> False
            _cli_states.clear()
            _cli_states.update({i: {"active": True, "cooldown_until": 0.0} for i in range(num_configs)})
            assert worker._is_llm_unavailable("") is False

            # Test 3: One config active, others inactive -> False
            _cli_states.clear()
            _cli_states.update(
                {
                    0: {"active": True, "cooldown_until": 0.0},
                    1: {"active": False, "cooldown_until": now + 3600},
                    2: {"active": False, "cooldown_until": now + 3600},
                }
            )
            assert worker._is_llm_unavailable("") is False

            # Test 4: All inactive but one cooldown expired -> False
            _cli_states.clear()
            _cli_states.update(
                {
                    0: {"active": False, "cooldown_until": now - 3600},
                    1: {"active": False, "cooldown_until": now + 3600},
                    2: {"active": False, "cooldown_until": now + 3600},
                }
            )
            assert worker._is_llm_unavailable("") is False

            # Test 5: String matching still works alongside cli_states check
            _cli_states.clear()
            _cli_states.update({i: {"active": True, "cooldown_until": 0.0} for i in range(num_configs)})
            assert worker._is_llm_unavailable("LLM timed out") is True
            assert worker._is_llm_unavailable("Git push failed") is False
        finally:
            # Restore original _cli_states
            _cli_states.clear()
            _cli_states.update(original_cli_states)

    def test_is_permanent_error(self):
        """Test that _is_permanent_error correctly detects permanent configuration issues."""
        task_source = MockTaskSource()
        worker = IssueWorker(task_source=task_source)
        # Permanent errors should return True
        assert worker._is_permanent_error("No CLI configuration found") is True
        assert worker._is_permanent_error("permission denied") is True
        assert worker._is_permanent_error("Authentication failed") is True
        assert worker._is_permanent_error("Unauthorized access") is True
        assert worker._is_permanent_error("Access denied") is True
        assert worker._is_permanent_error("Forbidden") is True
        assert worker._is_permanent_error("Invalid token") is True
        assert worker._is_permanent_error("Token expired") is True
        assert worker._is_permanent_error("Not configured") is True
        assert worker._is_permanent_error("Configuration error") is True
        assert worker._is_permanent_error("Missing configuration") is True
        # Transient errors should return False
        assert worker._is_permanent_error("LLM timed out") is False
        assert worker._is_permanent_error("Connection refused") is False
        assert worker._is_permanent_error("Rate limit exceeded") is False
        assert worker._is_permanent_error("") is False

    @patch("auto_slopp.workers.issue_worker.checkout_branch_resilient")
    @patch("auto_slopp.workers.issue_worker.create_and_checkout_branch")
    @patch("auto_slopp.workers.issue_worker.has_changes")
    @patch("auto_slopp.workers.issue_worker.get_current_branch")
    @patch("auto_slopp.workers.issue_worker.settings")
    @patch("auto_slopp.workers.issue_worker.get_active_cli_command")
    @patch("auto_slopp.workers.issue_worker.execute_with_instructions")
    def test_no_changes_llm_unavailable_calls_on_skip(
        self,
        mock_execute,
        mock_cli,
        mock_settings,
        mock_current_branch,
        mock_has_changes,
        mock_create_branch,
        mock_checkout,
    ):
        """Test that on_skip is called when LLM unavailable and no changes made (has_changes=False)."""
        mock_cli.return_value = "opencode"
        mock_settings.ralph_enabled = False
        mock_checkout.return_value = True
        mock_create_branch.return_value = True
        mock_execute.return_value = {"success": True}
        mock_has_changes.return_value = False
        mock_current_branch.return_value = "main"
        task_source = MockTaskSource(tasks=[Task(id=1, title="Test", body="")])
        worker = IssueWorker(task_source=task_source, dry_run=False)
        # Mock _is_llm_unavailable to return True
        worker._is_llm_unavailable = lambda _: True
        result = worker.run(Path("/tmp"))
        assert result["success"] is True
        assert result["tasks_processed"] == 0
        assert result["tasks_skipped"] == 1
        assert len(result["task_results"]) == 1
        assert result["task_results"][0]["success"] is True
        assert result["task_results"][0]["skipped"] is True
        assert result["task_results"][0]["skip_reason"] == "LLM unavailable - no changes made"
        assert task_source.on_skip_called is True
        assert task_source.on_no_changes_called is False

    @patch("auto_slopp.workers.issue_worker.commit_and_push_changes")
    @patch("auto_slopp.workers.issue_worker.checkout_branch_resilient")
    @patch("auto_slopp.workers.issue_worker.create_and_checkout_branch")
    @patch("auto_slopp.workers.issue_worker.has_changes")
    @patch("auto_slopp.workers.issue_worker.get_current_branch")
    @patch("auto_slopp.workers.issue_worker.settings")
    @patch("auto_slopp.workers.issue_worker.push_to_remote")
    @patch("auto_slopp.workers.issue_worker.get_commits_ahead_of_branch")
    @patch("auto_slopp.workers.issue_worker.get_active_cli_command")
    @patch("auto_slopp.workers.issue_worker.ensure_ralph_in_gitignore")
    def test_no_commits_ahead_llm_unavailable_calls_on_skip(
        self,
        mock_cli,
        mock_commits_ahead,
        mock_push,
        mock_settings,
        mock_current_branch,
        mock_has_changes,
        mock_create_branch,
        mock_checkout,
        mock_commit_push,
        mock_ensure_gitignore,
        caplog,
    ):
        """Test that on_skip is called when LLM unavailable and no commits ahead of main."""
        mock_cli.return_value = True  # ensure_ralph_in_gitignore
        mock_commits_ahead.return_value = "opencode"  # get_active_cli_command
        mock_checkout.return_value = True  # create_and_checkout_branch
        mock_create_branch.return_value = True  # has_changes
        mock_has_changes.return_value = "ai/task-1"  # get_current_branch
        mock_current_branch.ralph_enabled = True  # settings
        mock_current_branch.github_issue_step_max_iterations = 10  # settings
        mock_settings.return_value = (True, "")  # push_to_remote
        mock_push.return_value = 0  # get_commits_ahead_of_branch
        mock_commit_push.return_value = (True, "")  # checkout_branch_resilient
        mock_ensure_gitignore.return_value = (True, "")  # commit_and_push_changes
        task_source = MockTaskSource(tasks=[Task(id=1, title="Test", body="")])
        worker = IssueWorker(task_source=task_source, dry_run=False)
        worker.ralph_executor.execute = lambda *args, **kwargs: {
            "success": True,
            "loops_executed": 1,
            "steps_completed": 3,
            "total_steps": 3,
        }
        # Mock _is_llm_unavailable to return True
        worker._is_llm_unavailable = lambda _: True
        with tempfile.TemporaryDirectory() as temp_dir:
            with caplog.at_level("WARNING"):
                result = worker.run(Path(temp_dir))

        assert result["success"] is True
        assert result["tasks_processed"] == 0
        assert result["tasks_skipped"] == 1
        assert len(result["task_results"]) == 1
        assert result["task_results"][0]["success"] is True
        assert result["task_results"][0]["skipped"] is True
        assert result["task_results"][0]["skip_reason"] == "LLM unavailable - no commits ahead"
        assert task_source.on_skip_called is True
        assert task_source.on_no_changes_called is False
        # Verify ensure_ralph_in_gitignore was called
        mock_cli.assert_called_once()
        # Verify no warning was logged
        gitignore_warnings = [r for r in caplog.records if "Failed to ensure .ralph in .gitignore" in r.message]
        assert len(gitignore_warnings) == 0

    @patch("auto_slopp.workers.issue_worker.ensure_ralph_in_gitignore")
    @patch("auto_slopp.workers.issue_worker.checkout_branch_resilient")
    @patch("auto_slopp.workers.issue_worker.create_and_checkout_branch")
    @patch("auto_slopp.workers.issue_worker.settings")
    def test_ensure_ralph_in_gitignore_logs_warning_on_failure(
        self, mock_settings, mock_create_branch, mock_checkout, mock_ensure_gitignore, caplog
    ):
        """Test that warning is logged when ensure_ralph_in_gitignore returns False."""
        mock_settings.ralph_enabled = True
        mock_settings.github_issue_step_max_iterations = 10
        mock_checkout.return_value = True
        mock_create_branch.return_value = True
        mock_ensure_gitignore.return_value = False  # Simulate failure
        task_source = MockTaskSource(tasks=[Task(id=1, title="Test", body="")])
        worker = IssueWorker(task_source=task_source, dry_run=False)
        worker.ralph_executor.execute = lambda *args, **kwargs: {
            "success": True,
            "loops_executed": 1,
            "steps_completed": 3,
            "total_steps": 3,
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            with caplog.at_level("WARNING"):
                worker.run(Path(temp_dir))

        # Verify ensure_ralph_in_gitignore was called
        mock_ensure_gitignore.assert_called_once()
        # Verify warning was logged with repo_dir name in the message
        warning_records = [r for r in caplog.records if "Failed to ensure .ralph in .gitignore" in r.message]
        assert len(warning_records) == 1
        assert Path(temp_dir).name in warning_records[0].message
        assert "generated .ralph files may be committed to the repository" in warning_records[0].message

    def _create_test_repo(self, repo_path: Path) -> None:
        """Create a test git repository with main branch and no .gitignore."""
        subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )

        test_file = repo_path / "README.md"
        test_file.write_text("# Test Repository")

        subprocess.run(["git", "add", "."], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )

        subprocess.run(
            ["git", "branch", "-M", "main"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )

    @patch("auto_slopp.workers.issue_worker.push_to_remote")
    @patch("auto_slopp.workers.issue_worker.get_pr_for_branch")
    @patch("auto_slopp.workers.issue_worker.create_pull_request")
    @patch("auto_slopp.workers.issue_worker.get_commits_ahead_of_branch")
    @patch("auto_slopp.workers.issue_worker.settings")
    def test_gitignore_integration_ralph_added_when_missing(
        self, mock_settings, mock_commits_ahead, mock_create_pr, mock_get_pr, mock_push
    ):
        """Integration test: .ralph is added to .gitignore when missing."""
        mock_settings.ralph_enabled = True
        mock_settings.github_issue_step_max_iterations = 10
        mock_commits_ahead.return_value = 1
        mock_push.return_value = (True, "")
        mock_get_pr.return_value = None
        mock_create_pr.return_value = {"url": "https://github.com/test/pr/1"}

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            self._create_test_repo(repo_path)

            # Verify .gitignore doesn't exist initially
            gitignore_path = repo_path / ".gitignore"
            assert not gitignore_path.exists()

            task_source = MockTaskSource(tasks=[Task(id=1, title="Test Task", body="Test body")])
            worker = IssueWorker(task_source=task_source, dry_run=False)

            # Mock RalphExecutor to avoid actual CLI execution
            worker.ralph_executor.execute = lambda *args, **kwargs: {
                "success": True,
                "loops_executed": 1,
                "steps_completed": 3,
                "total_steps": 3,
            }

            # Mock _generate_pr_body_from_task_file to avoid file system access
            worker._generate_pr_body_from_task_file = lambda **kwargs: "PR body"

            # Run the worker
            result = worker.run(repo_path)

            # Verify the task was processed successfully
            assert result["success"] is True
            assert result["tasks_processed"] == 1

            # Verify .gitignore was created and contains .ralph
            assert gitignore_path.exists()
            content = gitignore_path.read_text()
            assert ".ralph/" in content

    @patch("auto_slopp.workers.issue_worker.push_to_remote")
    @patch("auto_slopp.workers.issue_worker.get_pr_for_branch")
    @patch("auto_slopp.workers.issue_worker.create_pull_request")
    @patch("auto_slopp.workers.issue_worker.get_commits_ahead_of_branch")
    @patch("auto_slopp.workers.issue_worker.settings")
    def test_gitignore_integration_ralph_not_duplicated(
        self, mock_settings, mock_commits_ahead, mock_create_pr, mock_get_pr, mock_push
    ):
        """Integration test: .ralph is not duplicated when already in .gitignore."""
        mock_settings.ralph_enabled = True
        mock_settings.github_issue_step_max_iterations = 10
        mock_commits_ahead.return_value = 1
        mock_push.return_value = (True, "")
        mock_get_pr.return_value = None
        mock_create_pr.return_value = {"url": "https://github.com/test/pr/1"}

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            self._create_test_repo(repo_path)

            # Create .gitignore with .ralph already present
            gitignore_path = repo_path / ".gitignore"
            gitignore_path.write_text("*.pyc\n__pycache__/\n.ralph/\n")

            task_source = MockTaskSource(tasks=[Task(id=1, title="Test Task", body="Test body")])
            worker = IssueWorker(task_source=task_source, dry_run=False)

            # Mock RalphExecutor to avoid actual CLI execution
            worker.ralph_executor.execute = lambda *args, **kwargs: {
                "success": True,
                "loops_executed": 1,
                "steps_completed": 3,
                "total_steps": 3,
            }

            # Mock _generate_pr_body_from_task_file to avoid file system access
            worker._generate_pr_body_from_task_file = lambda **kwargs: "PR body"

            # Run the worker
            result = worker.run(repo_path)

            # Verify the task was processed successfully
            assert result["success"] is True
            assert result["tasks_processed"] == 1

            # Verify .gitignore still contains .ralph only once
            content = gitignore_path.read_text()
            assert content.count(".ralph/") == 1
            assert "*.pyc" in content
            assert "__pycache__/" in content
