"""Tests for unified IssueWorker.

The ``_mock_pr_review_no_findings`` fixture in this module stubs
``IssueWorker._review_pull_request`` (which shells out to ``gh``) so tests
can focus on the behavior under test; see the fixture's docstring for why it
is intentionally not autouse.

Tests that want to exercise the real PR review loop simply do not request the
fixture and patch ``_review_pull_request`` themselves to script the review
outcomes (see ``TestPRReviewLoop``). To guard against the loop being silently
skipped, ``test_run_with_successful_execution`` patches
``_review_pull_request`` and asserts the loop was actually reached.
"""

import subprocess
import tempfile
from pathlib import Path
from typing import Any, NamedTuple
from unittest.mock import patch

import pytest

from auto_slopp.utils.linking import ensure_issue_link_in_pr_body
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


@pytest.fixture
def _mock_pr_review_no_findings():
    """Stub the PR review loop so tests focus on the behavior under test.

    This fixture is NOT autouse: it must be requested explicitly (via
    ``@pytest.mark.usefixtures``) by the tests that drive the worker through
    the PR review loop and want to avoid the real ``_review_pull_request``
    implementation (which shells out to ``gh``). Tests that do not request it
    exercise the real code path.
    """
    with patch.object(IssueWorker, "_review_pull_request", return_value=(False, "", [])):
        yield


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
    @pytest.mark.usefixtures("_mock_pr_review_no_findings")
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
        mock_settings.github_issue_pr_review_max_iterations = 1
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
    def test_ralph_executor_llm_unavailable_calls_on_skip(self, mock_settings, mock_create_branch, mock_checkout):
        """Test that on_skip is called when Ralph executor fails due to LLM unavailability."""
        mock_settings.ralph_enabled = True
        mock_settings.github_issue_step_max_iterations = 10
        mock_checkout.return_value = True
        mock_create_branch.return_value = True
        task_source = MockTaskSource(tasks=[Task(id=1, title="Test", body="")])
        worker = IssueWorker(task_source=task_source, dry_run=False)
        # Mock the RalphExecutor.execute to simulate LLM unavailability
        worker.ralph_executor.execute = lambda *args, **kwargs: {
            "success": False,
            "loops_executed": 1,
            "steps_completed": 0,
            "total_steps": 3,
            "max_loops_reached": False,
            "error": "No active CLI configuration available",
        }
        result = worker.run(Path("/tmp"))
        assert result["success"] is True
        assert result["tasks_processed"] == 0
        assert len(result["task_results"]) == 1
        assert result["task_results"][0]["success"] is True
        assert result["task_results"][0].get("skipped") is True
        assert task_source.on_skip_called is True
        assert "No active CLI configuration available" in task_source.skip_reason
        assert task_source.on_max_iterations_called is False
        assert task_source.on_task_failure_called is False

    @patch("auto_slopp.workers.issue_worker.checkout_branch_resilient")
    @patch("auto_slopp.workers.issue_worker.create_and_checkout_branch")
    @patch("auto_slopp.workers.issue_worker.has_changes")
    @patch("auto_slopp.workers.issue_worker.get_current_branch")
    @patch("auto_slopp.workers.issue_worker.settings")
    @patch("auto_slopp.workers.issue_worker.execute_with_instructions")
    @patch("auto_slopp.workers.issue_worker.get_active_cli_command")
    def test_direct_execution_llm_unavailable_calls_on_skip(
        self,
        mock_cli,
        mock_execute,
        mock_settings,
        mock_current_branch,
        mock_has_changes,
        mock_create_branch,
        mock_checkout,
    ):
        """Test that on_skip is called when direct CLI execution fails due to LLM unavailability."""
        mock_cli.return_value = "opencode"
        mock_settings.ralph_enabled = False
        mock_checkout.return_value = True
        mock_create_branch.return_value = True
        mock_execute.return_value = {
            "success": False,
            "error": "All CLI configurations exhausted",
        }
        mock_has_changes.return_value = False
        mock_current_branch.return_value = "ai/task-1"
        task_source = MockTaskSource(tasks=[Task(id=1, title="Test", body="")])
        worker = IssueWorker(task_source=task_source, dry_run=False)
        result = worker.run(Path("/tmp"))
        assert result["success"] is True
        assert result["tasks_processed"] == 0
        assert len(result["task_results"]) == 1
        assert result["task_results"][0]["success"] is True
        assert result["task_results"][0].get("skipped") is True
        assert task_source.on_skip_called is True
        assert "All CLI configurations exhausted" in task_source.skip_reason
        assert task_source.on_task_failure_called is False

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
    @pytest.mark.usefixtures("_mock_pr_review_no_findings")
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
        mock_settings.github_issue_pr_review_max_iterations = 1
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
    @pytest.mark.usefixtures("_mock_pr_review_no_findings")
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
        mock_settings.github_issue_pr_review_max_iterations = 1
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
    @pytest.mark.usefixtures("_mock_pr_review_no_findings")
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
        mock_settings.github_issue_pr_review_max_iterations = 1
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
    @patch("auto_slopp.workers.issue_worker.IssueWorker._review_pull_request")
    def test_run_with_successful_execution(
        self,
        mock_review,
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
        """Test that run handles successful execution with PR creation.

        ``_review_pull_request`` is patched and asserted to be called, so this
        test also verifies that the PR review loop is actually reached during a
        successful run.
        """
        mock_review.return_value = (False, "", [])
        mock_commits_ahead.return_value = 1
        mock_cli.return_value = "opencode"
        mock_settings.ralph_enabled = False
        mock_settings.github_issue_pr_review_max_iterations = 1
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
        # The PR review loop must have been reached (not silently stubbed away).
        mock_review.assert_called_once()

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
    @pytest.mark.usefixtures("_mock_pr_review_no_findings")
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
        mock_settings.github_issue_pr_review_max_iterations = 1
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
    @pytest.mark.usefixtures("_mock_pr_review_no_findings")
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
        mock_settings.github_issue_pr_review_max_iterations = 1
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
            "max_loops_reached": False,
            "error": "LLM timed out waiting for response",
        }
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
        assert worker._is_llm_unavailable("LLM is unavailable") is False  # Too broad, not a specific pattern
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
    @pytest.mark.usefixtures("_mock_pr_review_no_findings")
    def test_gitignore_integration_ralph_added_when_missing(
        self,
        mock_settings,
        mock_commits_ahead,
        mock_create_pr,
        mock_get_pr,
        mock_push,
    ):
        """Integration test: .ralph is added to .gitignore when missing."""
        mock_settings.ralph_enabled = True
        mock_settings.github_issue_step_max_iterations = 10
        mock_settings.github_issue_pr_review_max_iterations = 1
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
    @pytest.mark.usefixtures("_mock_pr_review_no_findings")
    def test_gitignore_integration_ralph_not_duplicated(
        self,
        mock_settings,
        mock_commits_ahead,
        mock_create_pr,
        mock_get_pr,
        mock_push,
    ):
        """Integration test: .ralph is not duplicated when already in .gitignore."""
        mock_settings.ralph_enabled = True
        mock_settings.github_issue_step_max_iterations = 10
        mock_settings.github_issue_pr_review_max_iterations = 1
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


class TestEnsureIssueLinkInPRBody:
    """Unit tests for the ensure_issue_link_in_pr_body helper function."""

    def test_body_with_closes_keyword(self):
        """Body already contains 'Closes #1' — should return unchanged."""
        body = "This PR fixes the bug.\nCloses #1"
        result = ensure_issue_link_in_pr_body(body, 1)
        assert result == body

    def test_body_with_fixes_keyword(self):
        """Body already contains 'Fixes #1' — should return unchanged."""
        body = "This PR fixes the bug.\nFixes #1"
        result = ensure_issue_link_in_pr_body(body, 1)
        assert result == body

    def test_body_with_resolves_keyword(self):
        """Body already contains 'Resolves #1' — should return unchanged."""
        body = "This PR resolves the issue.\nResolves #1"
        result = ensure_issue_link_in_pr_body(body, 1)
        assert result == body

    def test_body_with_uppercase_closes_keyword(self):
        """Body contains 'CLOSES #1' (uppercase) — should return unchanged (case-insensitive)."""
        body = "This PR fixes the bug.\nCLOSES #1"
        result = ensure_issue_link_in_pr_body(body, 1)
        assert result == body

    def test_body_with_mixed_case_closes_keyword(self):
        """Body contains 'cLoSeS #1' (mixed case) — should return unchanged."""
        body = "This PR fixes the bug.\ncLoSeS #1"
        result = ensure_issue_link_in_pr_body(body, 1)
        assert result == body

    def test_body_without_any_closing_keyword(self):
        """Body has no closing keyword — should prepend 'Closes #1'."""
        body = "This PR fixes the bug.\nChanges made to module X."
        result = ensure_issue_link_in_pr_body(body, 1)
        assert result.startswith("Closes #1\n\n")
        assert body in result

    def test_body_with_closes_different_issue(self):
        """Body closes a different issue — should prepend current issue."""
        body = "This PR fixes the bug.\nCloses #99"
        result = ensure_issue_link_in_pr_body(body, 1)
        assert "Closes #1" in result
        assert "Closes #99" in result

    def test_body_with_closes_no_space_before_hash(self):
        """Body has 'Closes#1' (no space) — should prepend 'Closes #1'."""
        body = "This PR fixes the bug.\nCloses#1"
        result = ensure_issue_link_in_pr_body(body, 1)
        assert result.startswith("Closes #1\n\n")

    def test_empty_body(self):
        """Empty body — should prepend 'Closes #1'."""
        result = ensure_issue_link_in_pr_body("", 1)
        assert result == "Closes #1\n\n\n"

    def test_body_with_multiple_closing_keywords_same_issue(self):
        """Body has multiple closing keywords for the same issue — should return unchanged."""
        body = "Closes #1\nFixes #1\nResolves #1"
        result = ensure_issue_link_in_pr_body(body, 1)
        assert result == body

    def test_single_digit_issue_id(self):
        """Issue ID is a single digit — should work correctly."""
        result = ensure_issue_link_in_pr_body("Some PR body", 5)
        assert "Closes #5" in result

    def test_large_issue_id(self):
        """Issue ID is a large number — should work correctly."""
        result = ensure_issue_link_in_pr_body("Some PR body", 99999)
        assert "Closes #99999" in result

    def test_prepend_format(self):
        """Prepended link should have correct format: 'Closes #N\n\n{body}\n'."""
        body = "Detailed PR description"
        result = ensure_issue_link_in_pr_body(body, 42)
        assert result == "Closes #42\n\nDetailed PR description\n"

    def test_body_with_fixes_keyword_different_issue(self):
        """Body closes a different issue with 'Fixes' — should prepend 'Closes #current'."""
        body = "Fixes #500\nSome changes"
        result = ensure_issue_link_in_pr_body(body, 10)
        assert result.startswith("Closes #10\n\n")
        assert "Fixes #500" in result

    def test_no_space_between_keyword_and_hash(self):
        """Body has 'Closes#1' (no space) — regex requires space, so should prepend."""
        body = "This PR fixes the bug.\nCloses#1"
        result = ensure_issue_link_in_pr_body(body, 1)
        assert result.startswith("Closes #1\n\n")

    def test_issue_number_as_part_of_larger_number(self):
        """Body has 'Closes #1234' — should NOT match #1 (word boundary prevents false positive)."""
        body = "This PR fixes the bug.\nCloses #1234"
        result = ensure_issue_link_in_pr_body(body, 1)
        assert result.startswith("Closes #1\n\n")

    def test_multiple_spaces_between_keyword_and_hash(self):
        r"""Body has 'Closes  #1' (multiple spaces) — regex \s+ handles this."""
        body = "This PR fixes the bug.\nCloses  #1"
        result = ensure_issue_link_in_pr_body(body, 1)
        assert result == body

    def test_keyword_as_part_of_larger_word(self):
        """Body has 'Uncloses #1' — word boundary prevents matching 'closes' inside 'uncloses'."""
        body = "This PR uncloses #1\nSome changes"
        result = ensure_issue_link_in_pr_body(body, 1)
        assert result.startswith("Closes #1\n\n")


class TestPRBodyLinkingIntegration:
    """Integration tests verifying PR bodies contain valid issue links in both code paths."""

    def test_ralph_disabled_get_default_pr_body_has_link(self):
        """When ralph_enabled=False, get_default_pr_body produces a body with valid link."""
        task = Task(id=23, title="Test Task", body="Some task body")
        pr_body = GitHubTaskSource().get_default_pr_body(task)
        assert "Closes #23" in pr_body or "Fixes #23" in pr_body or "Resolves #23" in pr_body

    def test_ralph_disabled_get_default_pr_body_empty_body(self):
        """When ralph_enabled=False and task body is empty, get_default_pr_body still has link."""
        task = Task(id=5, title="Test Task", body="")
        pr_body = GitHubTaskSource().get_default_pr_body(task)
        assert "Closes #5" in pr_body or "Fixes #5" in pr_body or "Resolves #5" in pr_body

    def test_ralph_disabled_get_default_pr_body_with_existing_link(self):
        """When ralph_enabled=False and task body already has closing keyword, it's preserved."""
        task = Task(id=10, title="Test Task", body="Fixes #10\nSome changes")
        pr_body = GitHubTaskSource().get_default_pr_body(task)
        assert "Fixes #10" in pr_body
        # Should not have a duplicate link
        assert pr_body.count("#10") == 1

    def test_ralph_disabled_get_default_pr_body_with_different_link(self):
        """When ralph_enabled=False and task body closes a different issue, current issue link is added."""
        task = Task(id=7, title="Test Task", body="Fixes #99\nSome changes")
        pr_body = GitHubTaskSource().get_default_pr_body(task)
        assert "Closes #7" in pr_body  # Current issue link added
        assert "Fixes #99" in pr_body  # Original link preserved

    def test_ralph_disabled_get_default_pr_body_vikunja_has_link(self):
        """VikunjaTaskSource.get_default_pr_body uses ensure_issue_link_in_pr_body.

        The PR body should contain both the Vikunja format prefix AND a valid
        closing keyword for the issue to ensure proper GitHub issue linking.
        """
        task = Task(id=42, title="Test Task", body="Some task body")
        pr_body = VikunjaTaskSource().get_default_pr_body(task)
        # Vikunja format uses "Vikunja Task #42:" prefix
        assert "Vikunja Task #42: Test Task" in pr_body
        # Should also contain a valid closing keyword for proper GitHub linking
        assert "Closes #42" in pr_body

    def test_ralph_disabled_get_default_pr_body_large_issue_id(self):
        """When ralph_enabled=False with large issue ID, get_default_pr_body still has valid link."""
        task = Task(id=99999, title="Test Task", body="Some task body")
        pr_body = GitHubTaskSource().get_default_pr_body(task)
        assert "Closes #99999" in pr_body or "Fixes #99999" in pr_body or "Resolves #99999" in pr_body


class TestGeneratePRBodyFromTaskFileIntegration:
    """Integration tests verifying _generate_pr_body_from_task_file produces valid issue links
    in both ralph_enabled=True and ralph_enabled=False code paths."""

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
    @pytest.mark.usefixtures("_mock_pr_review_no_findings")
    def test_ralph_enabled_pr_body_contains_issue_link(
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
        """When ralph_enabled=True, _generate_pr_body_from_task_file produces a PR body with valid issue link.

        This tests the full flow: Ralph executes, PR body is generated via
        _generate_pr_body_from_task_file, and the resulting PR body contains a
        valid closing keyword (Closes/Fixes/Resolves) for the issue.

        We mock _get_issue_task_path to return a non-existent path so that
        _generate_pr_body_from_task_file falls back to task_source.get_default_pr_body(),
        which uses ensure_issue_link_in_pr_body.
        """
        mock_commits_ahead.return_value = 1
        mock_cli.return_value = "opencode"
        mock_settings.ralph_enabled = True
        mock_settings.github_issue_step_max_iterations = 10
        mock_settings.github_issue_pr_review_max_iterations = 1
        mock_has_changes.return_value = True
        mock_commit_push.return_value = (True, None)
        mock_checkout.return_value = True
        mock_create_branch.return_value = True
        mock_current_branch.return_value = "ai/task-42"
        mock_push.return_value = (True, "")
        mock_get_pr.return_value = None
        mock_create_pr.return_value = {"url": "https://github.com/test/pr/1"}

        task_source = GitHubTaskSource()
        task_source.get_tasks = lambda _: [Task(id=42, title="Test Task", body="Test body")]
        worker = IssueWorker(task_source=task_source, dry_run=False)
        worker.ralph_executor.execute = lambda *args, **kwargs: {
            "success": True,
            "loops_executed": 2,
            "steps_completed": 5,
            "total_steps": 5,
        }

        # Mock _get_issue_task_path to return a non-existent path so that
        # _generate_pr_body_from_task_file falls back to get_default_pr_body
        worker.ralph_executor._get_issue_task_path = lambda repo_dir, task_id: Path("/nonexistent/task")

        result = worker.run(Path("/tmp"))

        assert result["success"] is True
        assert result["tasks_processed"] == 1
        assert result["prs_created"] == 1
        # Verify the PR body passed to create_pull_request contains a valid issue link
        call_kwargs = mock_create_pr.call_args
        pr_body = call_kwargs[1]["body"]
        assert "Closes #42" in pr_body or "Fixes #42" in pr_body or "Resolves #42" in pr_body

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
    @pytest.mark.usefixtures("_mock_pr_review_no_findings")
    def test_ralph_disabled_pr_body_contains_issue_link(
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
        """When ralph_enabled=False, get_default_pr_body produces a PR body with valid issue link.

        This tests the full flow: CLI executes, PR body is generated via
        task_source.get_default_pr_body(), and the resulting PR body contains a
        valid closing keyword (Closes/Fixes/Resolves) for the issue.
        """
        mock_commits_ahead.return_value = 1
        mock_cli.return_value = "opencode"
        mock_settings.ralph_enabled = False
        mock_settings.github_issue_pr_review_max_iterations = 1
        mock_commit_push.return_value = (True, None)
        mock_checkout.return_value = True
        mock_create_branch.return_value = True
        mock_execute.return_value = {"success": True}
        mock_has_changes.return_value = True
        mock_current_branch.return_value = "ai/task-7"
        mock_push.return_value = (True, "")
        mock_get_pr.return_value = None
        mock_create_pr.return_value = {"url": "https://github.com/test/pr/1"}

        # Use GitHubTaskSource which uses ensure_issue_link_in_pr_body in get_default_pr_body
        task_source = GitHubTaskSource()
        task_source.get_tasks = lambda _: [Task(id=7, title="Test Task", body="Test body")]
        worker = IssueWorker(task_source=task_source, dry_run=False)
        result = worker.run(Path("/tmp"))

        assert result["success"] is True
        assert result["tasks_processed"] == 1
        assert result["prs_created"] == 1
        # Verify the PR body passed to create_pull_request contains a valid issue link
        call_kwargs = mock_create_pr.call_args
        pr_body = call_kwargs[1]["body"]
        assert "Closes #7" in pr_body or "Fixes #7" in pr_body or "Resolves #7" in pr_body

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
    @pytest.mark.usefixtures("_mock_pr_review_no_findings")
    def test_ralph_enabled_pr_body_preserves_existing_link(
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
        """When ralph_enabled=True and the generated body already has a closing keyword, it is preserved.

        This tests that ensure_issue_link_in_pr_body does NOT duplicate an existing valid link.
        """
        mock_commits_ahead.return_value = 1
        mock_cli.return_value = "opencode"
        mock_settings.ralph_enabled = True
        mock_settings.github_issue_step_max_iterations = 10
        mock_settings.github_issue_pr_review_max_iterations = 1
        mock_has_changes.return_value = True
        mock_commit_push.return_value = (True, None)
        mock_checkout.return_value = True
        mock_create_branch.return_value = True
        mock_current_branch.return_value = "ai/task-55"
        mock_push.return_value = (True, "")
        mock_get_pr.return_value = None
        mock_create_pr.return_value = {"url": "https://github.com/test/pr/1"}

        task_source = MockTaskSource(tasks=[Task(id=55, title="Test Task", body="Test body")])
        worker = IssueWorker(task_source=task_source, dry_run=False)
        worker.ralph_executor.execute = lambda *args, **kwargs: {
            "success": True,
            "loops_executed": 1,
            "steps_completed": 3,
            "total_steps": 3,
        }

        # Mock _generate_pr_body_from_task_file to return a body WITH a closing keyword
        worker._generate_pr_body_from_task_file = lambda **kwargs: "Implemented the feature.\nFixes #55"

        result = worker.run(Path("/tmp"))

        assert result["success"] is True
        assert result["tasks_processed"] == 1
        # Verify the PR body passed to create_pull_request contains exactly one issue link
        call_kwargs = mock_create_pr.call_args
        pr_body = call_kwargs[1]["body"]
        assert pr_body == "Implemented the feature.\nFixes #55"
        assert pr_body.count("#55") == 1


class TestIssueWorkerPrReviewLoop:
    """Tests for the PR review -> fix loop in IssueWorker."""

    # ------------------------------------------------------------------
    # _review_pull_request unit tests
    # ------------------------------------------------------------------

    @patch("auto_slopp.workers.issue_worker.run_cli_executor")
    @patch("auto_slopp.workers.issue_worker.get_pr_files")
    def test_review_pull_request_splits_and_dedupes_findings(self, mock_files, mock_cli):
        """Actionable findings (issue:/suggestion:) are deduped; nits/chores are informational only."""
        mock_files.return_value = "diff --git a/x b/x"
        mock_cli.return_value = {
            "success": True,
            "stdout": (
                "issue: fix bug A\n"
                "suggestion: use helper\n"
                "issue: fix bug A\n"
                "nit: rename var\n"
                "chore: update deps\n"
                "praise: nice work\n"
                "question: why x?\n"
            ),
        }
        worker = IssueWorker(task_source=MockTaskSource())
        has_findings, comment, findings, error = worker._review_pull_request(
            Path("/tmp"), "https://github.com/o/r/pull/7", "title", "body"
        )
        assert has_findings is True
        assert error is None
        assert findings == ["issue: fix bug A", "suggestion: use helper"]
        # Informational lines are surfaced on the PR but are not findings
        assert "issue: fix bug A" in comment
        assert "suggestion: use helper" in comment
        assert "Non-blocking notes" in comment
        assert "nit: rename var" in comment
        assert "chore: update deps" in comment
        # Duplicates must not appear twice in the findings list or comment
        assert comment.count("issue: fix bug A") == 1

    @patch("auto_slopp.workers.issue_worker.run_cli_executor")
    @patch("auto_slopp.workers.issue_worker.get_pr_files")
    def test_review_pull_request_nits_only_do_not_block(self, mock_files, mock_cli):
        """Nits and chores alone must not trigger a fix round."""
        mock_files.return_value = "diff --git a/x b/x"
        mock_cli.return_value = {"success": True, "stdout": "nit: rename var\nchore: update deps\n"}
        worker = IssueWorker(task_source=MockTaskSource())
        has_findings, comment, findings, error = worker._review_pull_request(
            Path("/tmp"), "https://github.com/o/r/pull/7", "title", "body"
        )
        assert has_findings is False
        assert findings == []
        assert error is None
        assert "Non-blocking notes" in comment

    @patch("auto_slopp.workers.issue_worker.run_cli_executor")
    @patch("auto_slopp.workers.issue_worker.get_pr_files")
    def test_review_pull_request_cli_failure_returns_error_tuple(self, mock_files, mock_cli):
        """A failed review CLI run returns a 4-tuple with an error, not a truncated tuple."""
        mock_files.return_value = "diff --git a/x b/x"
        mock_cli.return_value = {"success": False, "error": "boom"}
        worker = IssueWorker(task_source=MockTaskSource())
        has_findings, _comment, findings, error = worker._review_pull_request(
            Path("/tmp"), "https://github.com/o/r/pull/7", "title", "body"
        )
        assert has_findings is False
        assert findings == []
        assert error is not None
        assert "boom" in error

    @patch("auto_slopp.workers.issue_worker.get_pr_files")
    def test_review_pull_request_diff_failure_returns_error_tuple(self, mock_files):
        mock_files.side_effect = Exception("gh failed")
        worker = IssueWorker(task_source=MockTaskSource())
        has_findings, _comment, findings, error = worker._review_pull_request(
            Path("/tmp"), "https://github.com/o/r/pull/7", "title", "body"
        )
        assert has_findings is False
        assert findings == []
        assert error is not None
        assert "Failed to get PR diff" in error

    def test_review_pull_request_bad_url_returns_error_tuple(self):
        worker = IssueWorker(task_source=MockTaskSource())
        has_findings, _comment, findings, error = worker._review_pull_request(Path("/tmp"), "not-a-url", "t", "b")
        assert has_findings is False
        assert findings == []
        assert error is not None

    # ------------------------------------------------------------------
    # End-to-end loop behavior through worker.run()
    # ------------------------------------------------------------------

    def _make_worker(self, task_source):
        worker = IssueWorker(task_source=task_source, dry_run=False)
        worker._generate_pr_body_from_task_file = lambda **kwargs: "PR body"
        return worker

    @patch("auto_slopp.workers.issue_worker.remove_label_from_issue")
    @patch("auto_slopp.workers.issue_worker.submit_pr_review")
    @patch("auto_slopp.workers.issue_worker.run_cli_executor")
    @patch("auto_slopp.workers.issue_worker.create_pull_request")
    @patch("auto_slopp.workers.issue_worker.get_pr_for_branch")
    @patch("auto_slopp.workers.issue_worker.push_to_remote")
    @patch("auto_slopp.workers.issue_worker.get_commits_ahead_of_branch")
    @patch("auto_slopp.workers.issue_worker.commit_and_push_changes")
    @patch("auto_slopp.workers.issue_worker.has_changes")
    @patch("auto_slopp.workers.issue_worker.get_current_branch")
    @patch("auto_slopp.workers.issue_worker.execute_with_instructions")
    @patch("auto_slopp.workers.issue_worker.get_active_cli_command")
    @patch("auto_slopp.workers.issue_worker.checkout_branch_resilient")
    @patch("auto_slopp.workers.issue_worker.create_and_checkout_branch")
    @patch("auto_slopp.workers.issue_worker.settings")
    def _run_with_review_sequence(
        self,
        review_sequence,
        mock_settings,
        mock_create_branch,
        mock_checkout,
        mock_cli,
        mock_execute,
        mock_current_branch,
        mock_has_changes,
        mock_commit_push,
        mock_commits_ahead,
        mock_push,
        mock_get_pr,
        mock_create_pr,
        mock_fix_cli,
        mock_submit_review,
        mock_remove_label,
    ):
        mock_settings.ralph_enabled = False
        mock_settings.github_issue_pr_review_max_iterations = 5
        mock_settings.cli_configurations = []
        mock_checkout.return_value = True
        mock_create_branch.return_value = True
        mock_cli.return_value = "opencode"
        mock_execute.return_value = {"success": True}
        mock_current_branch.return_value = "ai/task-1"
        mock_commits_ahead.return_value = 1
        mock_has_changes.return_value = True
        mock_commit_push.return_value = (True, None)
        mock_push.return_value = (True, "")
        mock_get_pr.return_value = None
        mock_create_pr.return_value = {"url": "https://github.com/test/repo/pull/7"}
        mock_submit_review.return_value = True
        mock_remove_label.return_value = True
        mock_fix_cli.return_value = {"success": True}

        with patch.object(IssueWorker, "_review_pull_request") as mock_review:
            mock_review.side_effect = review_sequence
            task_source = MockTaskSource(tasks=[Task(id=1, title="Test", body="")])
            worker = self._make_worker(task_source)
            result = worker.run(Path("/tmp"))
        return result, task_source, mock_review, mock_fix_cli, mock_submit_review

    def test_review_loop_stops_on_repeated_findings(self):
        """Stall detection: repeated identical findings stop the loop after one fix round."""
        review_sequence = [
            (True, "findings", ["issue: bug in foo"], None),
            (True, "findings", ["issue: bug in foo"], None),  # identical -> stall
        ]
        result, task_source, mock_review, mock_fix_cli, _mock_submit_review = self._run_with_review_sequence(
            review_sequence
        )
        task_result = result["task_results"][0]
        assert result["success"] is True
        assert task_result["success"] is True
        assert task_result["task_completed"] is False
        assert task_result["pr_review_done"] is True
        assert task_result["pr_review_iterations"] == 2
        # Only ONE fix round was executed (the second round detected no progress)
        assert mock_fix_cli.call_count == 1
        assert mock_review.call_count == 2
        # Issue stays open for the next cycle: not completed, not failed
        assert task_source.on_task_complete_called is False
        assert task_source.on_task_failure_called is False

    def test_review_loop_completes_when_clean(self):
        """A clean second review completes the task normally."""
        review_sequence = [
            (True, "findings", ["issue: bug in foo"], None),
            (False, "clean", [], None),
        ]
        result, task_source, _mock_review, mock_fix_cli, mock_submit_review = self._run_with_review_sequence(
            review_sequence
        )
        task_result = result["task_results"][0]
        assert task_result["success"] is True
        assert task_result["task_completed"] is True
        assert task_result["pr_review_iterations"] == 2
        assert mock_fix_cli.call_count == 1
        assert mock_submit_review.call_count == 2
        assert task_source.on_task_complete_called is True

    def test_review_loop_nits_only_completes_immediately(self):
        """A review with only nits/chores does not trigger any fix round."""
        review_sequence = [(False, "only nits", [], None)]
        result, task_source, _mock_review, mock_fix_cli, _mock_submit_review = self._run_with_review_sequence(
            review_sequence
        )
        task_result = result["task_results"][0]
        assert task_result["success"] is True
        assert task_result["task_completed"] is True
        assert task_result["pr_review_iterations"] == 1
        assert mock_fix_cli.call_count == 0
        assert task_source.on_task_complete_called is True

    def test_review_loop_no_progress_on_new_subset_stops(self):
        """New findings continue the loop; a round with only previously seen findings stops it."""
        review_sequence = [
            (True, "findings", ["issue: a", "issue: b"], None),
            (True, "findings", ["issue: a"], None),  # progress: b fixed
            (True, "findings", ["issue: a"], None),  # no progress: a still there, nothing new
        ]
        result, _task_source, _mock_review, mock_fix_cli, _ = self._run_with_review_sequence(review_sequence)
        task_result = result["task_results"][0]
        assert task_result["pr_review_done"] is True
        assert task_result["task_completed"] is False
        assert task_result["pr_review_iterations"] == 3
        # Fix rounds happened for rounds 1 and 2 only
        assert mock_fix_cli.call_count == 2

    def test_review_failure_completes_task_without_posting(self):
        """A review tooling failure does not fail the task, does not post the error to the PR,
        and completes the task since the work is done and review is best-effort."""
        review_sequence = [(False, "", [], "CLI tool failed to review PR #7: boom")]
        result, task_source, _mock_review, mock_fix_cli, mock_submit_review = self._run_with_review_sequence(
            review_sequence
        )
        assert task_result.get("pr_review_error") is not None
        assert mock_submit_review.call_count == 0
        assert mock_fix_cli.call_count == 0
        assert task_source.on_task_complete_called is True
        assert task_source.on_task_failure_called is False
        assert task_source.on_skip_called is False

    def test_review_failure_llm_unavailable_skips_task(self):
        """An LLM-unavailable review error skips the task like other LLM outages."""
        review_sequence = [(False, "", [], "CLI tool failed to review PR #7: connection reset by peer")]
        result, task_source, _, mock_fix_cli, mock_submit_review = self._run_with_review_sequence(review_sequence)
        task_result = result["task_results"][0]
        assert task_result["success"] is True
        assert task_result.get("skipped") is True
        assert task_source.on_skip_called is True
        assert mock_fix_cli.call_count == 0
        assert mock_submit_review.call_count == 0

    def test_fix_round_making_no_changes_stops_loop(self):
        """If the fixer changes nothing, the loop stops instead of re-reviewing the unchanged PR."""
        review_sequence = [
            (True, "findings", ["issue: bug in foo"], None),
        ]
        # Implementation phase needs changes; fix phase has none
        # Sequence: post-implementation check, pre-push check, fix-phase check
        has_changes_values = iter([True, True, False])
        with (
            patch("auto_slopp.workers.issue_worker.remove_label_from_issue") as mock_remove_label,
            patch("auto_slopp.workers.issue_worker.submit_pr_review") as mock_submit_review,
            patch("auto_slopp.workers.issue_worker.run_cli_executor") as mock_fix_cli,
            patch("auto_slopp.workers.issue_worker.create_pull_request") as mock_create_pr,
            patch("auto_slopp.workers.issue_worker.get_pr_for_branch") as mock_get_pr,
            patch("auto_slopp.workers.issue_worker.push_to_remote") as mock_push,
            patch("auto_slopp.workers.issue_worker.get_commits_ahead_of_branch") as mock_commits_ahead,
            patch("auto_slopp.workers.issue_worker.commit_and_push_changes") as mock_commit_push,
            patch("auto_slopp.workers.issue_worker.has_changes") as mock_has_changes,
            patch("auto_slopp.workers.issue_worker.get_current_branch") as mock_current_branch,
            patch("auto_slopp.workers.issue_worker.execute_with_instructions") as mock_execute,
            patch("auto_slopp.workers.issue_worker.get_active_cli_command") as mock_cli,
            patch("auto_slopp.workers.issue_worker.checkout_branch_resilient") as mock_checkout,
            patch("auto_slopp.workers.issue_worker.create_and_checkout_branch") as mock_create_branch,
            patch("auto_slopp.workers.issue_worker.settings") as mock_settings,
        ):
            mock_settings.ralph_enabled = False
            mock_settings.github_issue_pr_review_max_iterations = 5
            mock_settings.cli_configurations = []
            mock_checkout.return_value = True
            mock_create_branch.return_value = True
            mock_cli.return_value = "opencode"
            mock_execute.return_value = {"success": True}
            mock_current_branch.return_value = "ai/task-1"
            mock_commits_ahead.return_value = 1
            mock_has_changes.side_effect = lambda *a, **k: next(has_changes_values, False)
            mock_commit_push.return_value = (True, None)
            mock_push.return_value = (True, "")
            mock_get_pr.return_value = None
            mock_create_pr.return_value = {"url": "https://github.com/test/repo/pull/7"}
            mock_submit_review.return_value = True
            mock_remove_label.return_value = True
            mock_fix_cli.return_value = {"success": True}

            with patch.object(IssueWorker, "_review_pull_request") as mock_review:
                mock_review.side_effect = review_sequence
                task_source = MockTaskSource(tasks=[Task(id=1, title="Test", body="")])
                worker = self._make_worker(task_source)
                result = worker.run(Path("/tmp"))

        task_result = result["task_results"][0]
        assert task_result["success"] is True
        assert task_result["task_completed"] is False
        assert task_result["pr_review_done"] is True
        assert task_result["pr_review_iterations"] == 1
        # No second review happened even though max iterations allow it
        assert mock_review.call_count == 1
        assert task_source.on_task_failure_called is False

