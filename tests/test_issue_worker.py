from pathlib import Path
from unittest.mock import patch

from auto_slopp.workers.issue_worker import IssueWorker
from auto_slopp.workers.task_source import Task
from tests.test_github_task_source import GitHubTaskSource
from tests.test_task_source import ConcreteTaskSource as BaseMockTaskSource
from tests.test_vikunja_task_source import VikunjaTaskSource


class MockTaskSource(BaseMockTaskSource):
    """Mock task source for testing that accepts tasks in constructor."""

    def __init__(self, tasks=None):
        self._tasks = tasks or [Task(id=1, title="Test", body="body")]
        self.on_task_start_called = False
        self.on_task_complete_called = False

    def get_tasks(self, repo_path):
        return self._tasks

    def on_task_start(self, task, branch_name):
        self.on_task_start_called = True
        super().on_task_start(task, branch_name)

    def on_task_complete(self, task, branch_name, pr_url):
        self.on_task_complete_called = True
        super().on_task_complete(task, branch_name, pr_url)


class CapturingTaskSource(MockTaskSource):
    """Mock task source that captures the PR URL and branch name."""

    def __init__(self, tasks=None):
        super().__init__(tasks)
        self.captured = {}

    def on_task_complete(self, task, branch_name, pr_url):
        self.captured["branch_name"] = branch_name
        self.captured["pr_url"] = pr_url
        super().on_task_complete(task, branch_name, pr_url)


class TestIssueWorker:
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
    @patch("auto_slopp.workers.issue_worker.execute_with_instructions")
    @patch("auto_slopp.workers.issue_worker.get_active_cli_command")
    def test_on_task_start_called_before_branch_creation(
        self,
        mock_cli,
        mock_execute_with_instructions,
        mock_get_commits_ahead_of_branch,
        mock_get_pr_for_branch,
        mock_create_pull_request,
        mock_push_to_remote,
        mock_settings,
        mock_get_current_branch,
        mock_has_changes,
        mock_create_and_checkout_branch,
        mock_checkout_branch_resilient,
        mock_commit_push,
    ):
        """Test that on_task_start is called before branch creation."""
        mock_cli.return_value = "opencode"
        mock_settings.ralph_enabled = False
        mock_checkout_branch_resilient.return_value = True
        mock_create_and_checkout_branch.return_value = False  # Fail early to keep test simple
        task_source = MockTaskSource(tasks=[Task(id=1, title="Test", body="")])
        worker = IssueWorker(task_source=task_source, dry_run=False)
        worker.run(Path("/tmp"))
        assert task_source.on_task_start_called is True

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
    @patch("auto_slopp.workers.issue_worker.execute_with_instructions")
    @patch("auto_slopp.workers.issue_worker.get_active_cli_command")
    def test_pr_creation_failure_fallback_to_existing_pr(
        self,
        mock_cli,
        mock_execute_with_instructions,
        mock_get_commits_ahead_of_branch,
        mock_get_pr_for_branch,
        mock_create_pull_request,
        mock_push_to_remote,
        mock_settings,
        mock_get_current_branch,
        mock_has_changes,
        mock_create_and_checkout_branch,
        mock_checkout_branch_resilient,
        mock_commit_push,
    ):
        """Test that when PR creation fails, fallback to existing PR succeeds."""
        mock_cli.return_value = "opencode"
        mock_settings.ralph_enabled = False
        mock_has_changes.return_value = True
        mock_commit_push.return_value = (True, None)
        mock_checkout_branch_resilient.return_value = True
        mock_create_and_checkout_branch.return_value = True
        mock_execute_with_instructions.return_value = {"success": True}
        mock_get_current_branch.return_value = "ai/task-1"
        mock_push_to_remote.return_value = (True, "")
        # First call returns None (no existing open PR), second call finds one after create fails
        mock_get_pr_for_branch.side_effect = [
            None,
            {"state": "OPEN", "url": "https://github.com/test/pr/42"},
        ]
        mock_create_pull_request.return_value = None  # PR creation fails
        task_source = MockTaskSource(tasks=[Task(id=1, title="Test", body="")])
        worker = IssueWorker(task_source=task_source, dry_run=False)
        result = worker.run(Path("/tmp"))
        assert result["task_results"][0]["success"] is True
        assert result["task_results"][0]["pr_url"] == "https://github.com/test/pr/42"
        assert result["prs_created"] == 1
        assert task_source.on_task_complete_called is True

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
    @patch("auto_slopp.workers.issue_worker.execute_with_instructions")
    @patch("auto_slopp.workers.issue_worker.get_active_cli_command")
    def test_existing_open_pr_reused(
        self,
        mock_cli,
        mock_execute_with_instructions,
        mock_get_commits_ahead_of_branch,
        mock_get_pr_for_branch,
        mock_create_pull_request,
        mock_push_to_remote,
        mock_settings,
        mock_get_current_branch,
        mock_has_changes,
        mock_create_and_checkout_branch,
        mock_checkout_branch_resilient,
        mock_commit_push,
    ):
        """Test that GitHubIssueWorker uses correct PR title format for GitHub tasks."""
        mock_cli.return_value = "opencode"
        mock_settings.ralph_enabled = False
        mock_has_changes.return_value = True
        mock_commit_push.return_value = (True, None)
        mock_checkout_branch_resilient.return_value = True
        mock_create_and_checkout_branch.return_value = True
        mock_execute_with_instructions.return_value = {"success": True}
        mock_get_current_branch.return_value = "ai/task-1"
        mock_push_to_remote.return_value = (True, "")
        mock_get_pr_for_branch.return_value = None
        mock_create_pull_request.return_value = {"url": "https://github.com/test/pr/1"}
        mock_get_commits_ahead_of_branch.return_value = 1

        # Create IssueWorker with GitHubTaskSource
        task_source = GitHubTaskSource()
        worker = IssueWorker(task_source=task_source, dry_run=False)

        # Run the worker
        task = Task(id=123, title="Fix bug", body="")
        task_source.get_tasks = lambda _: [task]
        result = worker.run(Path("/tmp"))

        # Verify that create_pull_request was called with correct title format
        assert result["success"] is True
        mock_create_pull_request.assert_called_once()
        call_kwargs = mock_create_pull_request.call_args
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
    @patch("auto_slopp.workers.issue_worker.get_commits_ahead_of_branch")
    @patch("auto_slopp.workers.issue_worker.execute_with_instructions")
    @patch("auto_slopp.workers.issue_worker.get_active_cli_command")
    def test_vikunja_task_pr_title_format(
        self,
        mock_commit_and_push_changes,
        mock_checkout_branch_resilient,
        mock_create_and_checkout_branch,
        mock_has_changes,
        mock_get_current_branch,
        mock_settings,
        mock_push_to_remote,
        mock_create_pull_request,
        mock_get_pr_for_branch,
        mock_get_commits_ahead_of_branch,
        mock_execute_with_instructions,
        mock_get_active_cli_command,
    ):
        """Test that VikunjaIssueWorker uses correct PR title format for Vikunja tasks."""
        mock_get_active_cli_command.return_value = "opencode"
        mock_settings.ralph_enabled = False
        mock_has_changes.return_value = True
        mock_commit_and_push_changes.return_value = (True, None)
        mock_checkout_branch_resilient.return_value = True
        mock_create_and_checkout_branch.return_value = True
        mock_execute_with_instructions.return_value = {"success": True}
        mock_get_current_branch.return_value = "ai/task-1"
        mock_push_to_remote.return_value = (True, "")
        mock_get_pr_for_branch.return_value = None
        mock_create_pull_request.return_value = {"url": "https://github.com/test/pr/1"}

        # Create IssueWorker with VikunjaTaskSource
        task_source = VikunjaTaskSource()
        worker = IssueWorker(task_source=task_source, dry_run=False)

        # Run the worker
        task = Task(id=456, title="Add feature", body="")
        task_source.get_tasks = lambda _: [task]
        result = worker.run(Path("/tmp"))

        # Verify that create_pull_request was called with correct title format
        assert result["success"] is True
        mock_create_pull_request.assert_called_once()
        call_kwargs = mock_create_pull_request.call_args
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
    @patch("auto_slopp.workers.issue_worker.get_commits_ahead_of_branch")
    @patch("auto_slopp.workers.issue_worker.execute_with_instructions")
    @patch("auto_slopp.workers.issue_worker.get_active_cli_command")
    def test_on_task_complete_receives_correct_pr_url(
        self,
        mock_commit_and_push_changes,
        mock_checkout_branch_resilient,
        mock_create_and_checkout_branch,
        mock_has_changes,
        mock_get_current_branch,
        mock_settings,
        mock_push_to_remote,
        mock_create_pull_request,
        mock_get_pr_for_branch,
        mock_get_commits_ahead_of_branch,
        mock_execute_with_instructions,
        mock_get_active_cli_command,
    ):
        """Test that on_task_complete is called with the correct PR URL."""
        mock_get_active_cli_command.return_value = "opencode"
        mock_settings.ralph_enabled = False
        mock_has_changes.return_value = True
        mock_commit_and_push_changes.return_value = (True, None)
        mock_checkout_branch_resilient.return_value = True
        mock_create_and_checkout_branch.return_value = True
        mock_execute_with_instructions.return_value = {"success": True}
        mock_get_current_branch.return_value = "ai/task-1"
        mock_push_to_remote.return_value = (True, "")
        mock_get_pr_for_branch.return_value = None
        mock_create_pull_request.return_value = {"url": "https://github.com/test/pr/7"}

        task = Task(id=1, title="Test", body="")
        task_source = CapturingTaskSource(tasks=[task])
        worker = IssueWorker(task_source=task_source, dry_run=False)
        worker.run(Path("/tmp"))
        assert task_source.captured["pr_url"] == "https://github.com/test/pr/7"
        assert task_source.captured["branch_name"] == "ai/task-1"

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
    @patch("auto_slopp.workers.issue_worker.execute_with_instructions")
    @patch("auto_slopp.workers.issue_worker.get_active_cli_command")
    def test_github_task_pr_title_format(
        self,
        mock_cli,
        mock_execute_with_instructions,
        mock_get_commits_ahead_of_branch,
        mock_get_pr_for_branch,
        mock_create_pull_request,
        mock_push_to_remote,
        mock_settings,
        mock_get_current_branch,
        mock_has_changes,
        mock_create_and_checkout_branch,
        mock_checkout_branch_resilient,
        mock_commit_push,
    ):
        """Test successful Ralph-enabled workflow through push and PR creation."""
        mock_cli.return_value = "opencode"
        mock_settings.ralph_enabled = True
        mock_settings.github_issue_step_max_iterations = 10
        mock_has_changes.return_value = True
        mock_commit_push.return_value = (True, None)
        mock_checkout_branch_resilient.return_value = True
        mock_create_and_checkout_branch.return_value = True
        mock_get_current_branch.return_value = "ai/task-1"
        mock_push_to_remote.return_value = (True, "")
        mock_get_pr_for_branch.return_value = None
        mock_create_pull_request.return_value = {"url": "https://github.com/test/pr/1"}
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
        mock_push_to_remote.assert_called_once()
        mock_create_pull_request.assert_called_once()
