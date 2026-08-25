"""Tests for PRWorker."""

from pathlib import Path
from unittest.mock import patch

from auto_slopp.workers.pr_worker import MAX_WORKFLOW_LOG_CHARS, PRWorker


class TestPRWorker:
    """Tests for PRWorker push behavior."""

    def test_pushes_once_when_tests_pass_without_fix(self):
        """Test that PRWorker pushes only once when tests pass immediately."""
        worker = PRWorker()
        repo_dir = Path("/tmp/repo")

        with (
            patch.object(worker, "_get_open_pr_branches", return_value=["feature"]),
            patch.object(worker, "_checkout_branch", return_value=True),
            patch.object(worker, "_update_branch_with_main", return_value=True),
            patch.object(
                worker,
                "_run_tests",
                return_value={"success": True, "output": "", "error": None},
            ),
            patch.object(worker, "_push_branch", return_value=True) as mock_push_branch,
        ):
            result = worker._process_repository(repo_dir)

        assert result["success"] is True
        assert mock_push_branch.call_count == 1

    def test_pushes_once_when_tests_pass_after_fix(self):
        """Test that PRWorker pushes only once after tests are fixed and pass."""
        worker = PRWorker()
        repo_dir = Path("/tmp/repo")

        with (
            patch.object(worker, "_get_open_pr_branches", return_value=["feature"]),
            patch.object(worker, "_checkout_branch", return_value=True),
            patch.object(worker, "_update_branch_with_main", return_value=True),
            patch.object(
                worker,
                "_run_tests",
                side_effect=[
                    {"success": False, "output": "", "error": "failed"},
                    {"success": True, "output": "", "error": None},
                ],
            ),
            patch.object(worker, "_fix_tests_with_cli", return_value={"success": True}),
            patch.object(worker, "_push_branch", return_value=True) as mock_push_branch,
            patch("auto_slopp.workers.pr_worker.has_changes", return_value=True),
            patch("auto_slopp.workers.pr_worker.commit_and_push_changes", return_value=(True, None)),
        ):
            result = worker._process_repository(repo_dir)

        assert result["success"] is True
        assert mock_push_branch.call_count == 1

    def test_commits_changes_after_cli_test_fix(self):
        """Test that PRWorker commits changes after CLI tool fixes tests."""
        worker = PRWorker()
        repo_dir = Path("/tmp/repo")

        with (
            patch.object(worker, "_get_open_pr_branches", return_value=["feature"]),
            patch.object(worker, "_checkout_branch", return_value=True),
            patch.object(worker, "_update_branch_with_main", return_value=True),
            patch.object(
                worker,
                "_run_tests",
                side_effect=[
                    {"success": False, "output": "", "error": "failed"},
                    {"success": True, "output": "", "error": None},
                ],
            ),
            patch.object(worker, "_fix_tests_with_cli", return_value={"success": True}),
            patch.object(worker, "_push_branch", return_value=True),
            patch("auto_slopp.workers.pr_worker.has_changes", return_value=True) as mock_has_changes,
            patch("auto_slopp.workers.pr_worker.commit_and_push_changes", return_value=(True, None)) as mock_commit,
        ):
            worker._process_repository(repo_dir)

        mock_has_changes.assert_called_once_with(repo_dir)
        mock_commit.assert_called_once_with(
            repo_dir,
            "fix: commit changes after CLI test fix for feature",
            push_if_remote=False,
        )

    def test_no_commit_when_no_changes_after_cli_test_fix(self):
        """Test that PRWorker skips commit when CLI tool made no changes."""
        worker = PRWorker()
        repo_dir = Path("/tmp/repo")

        with (
            patch.object(worker, "_get_open_pr_branches", return_value=["feature"]),
            patch.object(worker, "_checkout_branch", return_value=True),
            patch.object(worker, "_update_branch_with_main", return_value=True),
            patch.object(
                worker,
                "_run_tests",
                side_effect=[
                    {"success": False, "output": "", "error": "failed"},
                    {"success": True, "output": "", "error": None},
                ],
            ),
            patch.object(worker, "_fix_tests_with_cli", return_value={"success": True}),
            patch.object(worker, "_push_branch", return_value=True),
            patch("auto_slopp.workers.pr_worker.has_changes", return_value=False),
            patch("auto_slopp.workers.pr_worker.commit_and_push_changes", return_value=(True, None)) as mock_commit,
        ):
            worker._process_repository(repo_dir)

        mock_commit.assert_not_called()

    def test_commits_changes_after_cli_merge_fix(self):
        """Test that PRWorker commits changes after CLI tool fixes merge conflicts."""
        worker = PRWorker()
        repo_dir = Path("/tmp/repo")

        with (
            patch.object(worker, "_get_open_pr_branches", return_value=["feature"]),
            patch.object(worker, "_checkout_branch", return_value=True),
            patch.object(
                worker,
                "_update_branch_with_main",
                side_effect=[False, True],
            ),
            patch.object(
                worker,
                "_run_tests",
                return_value={"success": True, "output": "", "error": None},
            ),
            patch.object(worker, "_fix_merge_with_cli", return_value={"success": True}),
            patch.object(worker, "_push_branch", return_value=True),
            patch("auto_slopp.workers.pr_worker.has_changes", return_value=True) as mock_has_changes,
            patch("auto_slopp.workers.pr_worker.commit_and_push_changes", return_value=(True, None)) as mock_commit,
        ):
            worker._process_repository(repo_dir)

        mock_has_changes.assert_called_once_with(repo_dir)
        mock_commit.assert_called_once_with(
            repo_dir,
            "fix: commit changes after CLI merge fix for feature",
            push_if_remote=False,
        )

    def test_filters_prs_by_allowed_creator(self):
        """Test that PRWorker only processes PRs from allowed creator."""
        worker = PRWorker()
        repo_dir = Path("/tmp/repo")

        mock_prs = [
            {
                "headRefName": "feature-1",
                "author": {"login": "MelvinKl"},
                "number": 1,
                "title": "Feature 1",
            },
            {
                "headRefName": "feature-2",
                "author": {"login": "other-user"},
                "number": 2,
                "title": "Feature 2",
            },
            {
                "headRefName": "feature-3",
                "author": {"login": "MelvinKl"},
                "number": 3,
                "title": "Feature 3",
            },
        ]

        with (
            patch("auto_slopp.workers.pr_worker.get_open_prs", return_value=mock_prs),
            patch("auto_slopp.workers.pr_worker.settings") as mock_settings,
        ):
            mock_settings.github_issue_worker_allowed_creator = "MelvinKl"
            branches = worker._get_open_pr_branches(repo_dir)

        assert len(branches) == 2
        assert "feature-1" in branches
        assert "feature-3" in branches
        assert "feature-2" not in branches

    def test_skips_all_prs_when_none_from_allowed_creator(self):
        """Test that PRWorker skips all PRs when none are from allowed creator."""
        worker = PRWorker()
        repo_dir = Path("/tmp/repo")

        mock_prs = [
            {
                "headRefName": "feature-1",
                "author": {"login": "user1"},
                "number": 1,
                "title": "Feature 1",
            },
            {
                "headRefName": "feature-2",
                "author": {"login": "user2"},
                "number": 2,
                "title": "Feature 2",
            },
        ]

        with (
            patch("auto_slopp.workers.pr_worker.get_open_prs", return_value=mock_prs),
            patch("auto_slopp.workers.pr_worker.settings") as mock_settings,
        ):
            mock_settings.github_issue_worker_allowed_creator = "MelvinKl"
            branches = worker._get_open_pr_branches(repo_dir)

        assert len(branches) == 0

    def test_processes_all_prs_from_allowed_creator(self):
        """Test that PRWorker processes all PRs when all are from allowed creator."""
        worker = PRWorker()
        repo_dir = Path("/tmp/repo")

        mock_prs = [
            {
                "headRefName": "feature-1",
                "author": {"login": "MelvinKl"},
                "number": 1,
                "title": "Feature 1",
            },
            {
                "headRefName": "feature-2",
                "author": {"login": "MelvinKl"},
                "number": 2,
                "title": "Feature 2",
            },
        ]

        with (
            patch("auto_slopp.workers.pr_worker.get_open_prs", return_value=mock_prs),
            patch("auto_slopp.workers.pr_worker.settings") as mock_settings,
        ):
            mock_settings.github_issue_worker_allowed_creator = "MelvinKl"
            branches = worker._get_open_pr_branches(repo_dir)

        assert len(branches) == 2
        assert "feature-1" in branches
        assert "feature-2" in branches

    def test_handles_pr_without_author(self):
        """Test that PRWorker handles PRs with missing author information."""
        worker = PRWorker()
        repo_dir = Path("/tmp/repo")

        mock_prs = [
            {
                "headRefName": "feature-1",
                "author": None,
                "number": 1,
                "title": "Feature 1",
            },
            {
                "headRefName": "feature-2",
                "author": {},
                "number": 2,
                "title": "Feature 2",
            },
            {
                "headRefName": "feature-3",
                "author": {"login": "MelvinKl"},
                "number": 3,
                "title": "Feature 3",
            },
        ]

        with (
            patch("auto_slopp.workers.pr_worker.get_open_prs", return_value=mock_prs),
            patch("auto_slopp.workers.pr_worker.settings") as mock_settings,
        ):
            mock_settings.github_issue_worker_allowed_creator = "MelvinKl"
            branches = worker._get_open_pr_branches(repo_dir)

        assert len(branches) == 1
        assert "feature-3" in branches


class TestPRWorkerWorkflowRuns:
    """Test cases for PRWorker workflow run handling."""

    @patch("auto_slopp.workers.pr_worker.get_failed_workflow_logs")
    @patch("auto_slopp.workers.pr_worker.get_workflow_runs_for_branch")
    def test_get_and_log_workflow_runs_all_successful(self, mock_get_workflow_runs, mock_get_failed_logs):
        """Test _get_and_log_workflow_runs when all workflows are successful."""
        worker = PRWorker()
        repo_dir = Path("/tmp/repo")

        mock_get_workflow_runs.return_value = [
            {
                "conclusion": "success",
                "name": "CI",
                "headSha": "abc123",
                "event": "pull_request",
                "status": "completed",
                "databaseId": 123,
            },
            {
                "conclusion": "success",
                "name": "Lint",
                "headSha": "def456",
                "event": "pull_request",
                "status": "completed",
                "databaseId": 124,
            },
        ]

        result = worker._get_and_log_workflow_runs(repo_dir, "main")
        assert result == ([], [])  # No failed workflows
        mock_get_failed_logs.assert_not_called()

    @patch("auto_slopp.workers.pr_worker.get_failed_workflow_logs")
    @patch("auto_slopp.workers.pr_worker.get_workflow_runs_for_branch")
    def test_get_and_log_workflow_runs_with_failure(self, mock_get_workflow_runs, mock_get_failed_logs):
        """Test _get_and_log_workflow_runs when some workflows have failed."""
        worker = PRWorker()
        repo_dir = Path("/tmp/repo")

        mock_get_workflow_runs.return_value = [
            {
                "conclusion": "success",
                "name": "CI",
                "headSha": "abc123",
                "event": "pull_request",
                "status": "completed",
                "databaseId": 123,
            },
            {
                "conclusion": "failure",
                "name": "Lint",
                "headSha": "def456",
                "event": "pull_request",
                "status": "completed",
                "databaseId": 124,
            },
        ]

        mock_get_failed_logs.return_value = "failure log"

        result = worker._get_and_log_workflow_runs(repo_dir, "main")
        assert len(result[0]) == 1
        assert result[0][0]["conclusion"] == "failure"
        assert result[0][0]["name"] == "Lint"
        assert result[1] == [{"name": "Lint", "databaseId": 124, "log": "failure log"}]
        mock_get_failed_logs.assert_called_once_with(repo_dir, result[0][0])

    @patch("auto_slopp.workers.pr_worker.get_failed_workflow_logs")
    @patch("auto_slopp.workers.pr_worker.get_workflow_runs_for_branch")
    def test_get_and_log_workflow_runs_with_in_progress(self, mock_get_workflow_runs, mock_get_failed_logs):
        """Test _get_and_log_workflow_runs when some workflows are in progress."""
        worker = PRWorker()
        repo_dir = Path("/tmp/repo")

        mock_get_workflow_runs.return_value = [
            {
                "conclusion": None,
                "name": "CI",
                "headSha": "abc123",
                "event": "pull_request",
                "status": "in_progress",
                "databaseId": 123,
            },
            {
                "conclusion": "success",
                "name": "Lint",
                "headSha": "def456",
                "event": "pull_request",
                "status": "completed",
                "databaseId": 124,
            },
        ]

        result = worker._get_and_log_workflow_runs(repo_dir, "main")
        assert result == ([], [])  # In-progress workflows should not be considered failures

    @patch("auto_slopp.workers.pr_worker.get_failed_workflow_logs")
    @patch("auto_slopp.workers.pr_worker.get_workflow_runs_for_branch")
    def test_get_and_log_workflow_runs_with_queued(self, mock_get_workflow_runs, mock_get_failed_logs):
        """Test _get_and_log_workflow_runs when some workflows are queued."""
        worker = PRWorker()
        repo_dir = Path("/tmp/repo")

        mock_get_workflow_runs.return_value = [
            {
                "conclusion": None,
                "name": "CI",
                "headSha": "abc123",
                "event": "pull_request",
                "status": "queued",
                "databaseId": 123,
            },
            {
                "conclusion": "success",
                "name": "Lint",
                "headSha": "def456",
                "event": "pull_request",
                "status": "completed",
                "databaseId": 124,
            },
        ]

        result = worker._get_and_log_workflow_runs(repo_dir, "main")
        assert result == ([], [])  # Queued workflows should not be considered failures

    @patch("auto_slopp.workers.pr_worker.get_failed_workflow_logs")
    @patch("auto_slopp.workers.pr_worker.get_workflow_runs_for_branch")
    def test_get_and_log_workflow_runs_no_runs(self, mock_get_workflow_runs, mock_get_failed_logs):
        """Test _get_and_log_workflow_runs when no workflow runs are returned."""
        worker = PRWorker()
        repo_dir = Path("/tmp/repo")

        mock_get_workflow_runs.return_value = []

        result = worker._get_and_log_workflow_runs(repo_dir, "main")
        assert result == ([], [])  # No workflows means no failures


class TestPRWorkerWorkflowFix:
    """Test cases for PRWorker fixing failing GitHub Actions workflows."""

    def test_fixes_failed_workflows_and_continues(self):
        """Test that PRWorker fixes failed GitHub Actions workflows and continues instead of skipping."""
        worker = PRWorker()
        repo_dir = Path("/tmp/repo")

        with (
            patch.object(worker, "_get_open_pr_branches", return_value=["feature"]),
            patch.object(worker, "_checkout_branch", return_value=True),
            patch.object(
                worker,
                "_get_and_log_workflow_runs",
                return_value=(
                    [{"conclusion": "failure", "name": "CI"}],
                    [{"name": "CI", "databaseId": 123, "log": "line1\nline2"}],
                ),
            ),
            patch.object(worker, "_fix_workflows_with_cli", return_value={"success": True}) as mock_fix,
            patch.object(worker, "_update_branch_with_main", return_value=True),
            patch.object(
                worker,
                "_run_tests",
                return_value={"success": True, "output": "", "error": None},
            ),
            patch.object(worker, "_push_branch", return_value=True) as mock_push_branch,
            patch("auto_slopp.workers.pr_worker.has_changes", return_value=True),
            patch("auto_slopp.workers.pr_worker.commit_and_push_changes", return_value=(True, None)) as mock_commit,
        ):
            result = worker._process_repository(repo_dir)

        assert result["success"] is True
        assert result["workflows_fixed"] is True
        mock_fix.assert_called_once_with(repo_dir, [{"name": "CI", "databaseId": 123, "log": "line1\nline2"}])
        mock_commit.assert_called_once_with(
            repo_dir,
            "fix: commit changes after CLI workflow fix for feature",
            push_if_remote=False,
        )
        mock_push_branch.assert_called_once_with(repo_dir, "feature")

    def test_continues_when_workflow_fix_fails(self):
        """Test that PRWorker continues processing the branch even when the workflow fix fails."""
        worker = PRWorker()
        repo_dir = Path("/tmp/repo")

        with (
            patch.object(worker, "_get_open_pr_branches", return_value=["feature"]),
            patch.object(worker, "_checkout_branch", return_value=True),
            patch.object(
                worker,
                "_get_and_log_workflow_runs",
                return_value=(
                    [{"conclusion": "failure", "name": "CI"}],
                    [{"name": "CI", "databaseId": 123, "log": "failure log"}],
                ),
            ),
            patch.object(
                worker,
                "_fix_workflows_with_cli",
                return_value={"success": False, "error": "fix failed"},
            ),
            patch.object(worker, "_update_branch_with_main", return_value=True),
            patch.object(
                worker,
                "_run_tests",
                return_value={"success": True, "output": "", "error": None},
            ),
            patch.object(worker, "_push_branch", return_value=True) as mock_push_branch,
            patch("auto_slopp.workers.pr_worker.commit_and_push_changes", return_value=(True, None)) as mock_commit,
        ):
            result = worker._process_repository(repo_dir)

        assert result["success"] is True
        assert "fix failed" in result["error"]
        mock_commit.assert_not_called()
        mock_push_branch.assert_called_once_with(repo_dir, "feature")

    def test_does_not_fix_when_no_failed_workflows(self):
        """Test that PRWorker does not invoke the workflow fix when there are no failed runs."""
        worker = PRWorker()
        repo_dir = Path("/tmp/repo")

        with (
            patch.object(worker, "_get_open_pr_branches", return_value=["feature"]),
            patch.object(worker, "_checkout_branch", return_value=True),
            patch.object(worker, "_get_and_log_workflow_runs", return_value=([], [])),
            patch.object(worker, "_fix_workflows_with_cli") as mock_fix,
            patch.object(worker, "_update_branch_with_main", return_value=True),
            patch.object(
                worker,
                "_run_tests",
                return_value={"success": True, "output": "", "error": None},
            ),
            patch.object(worker, "_push_branch", return_value=True),
        ):
            result = worker._process_repository(repo_dir)

        assert result["success"] is True
        mock_fix.assert_not_called()

    def test_fix_workflows_with_cli_truncates_long_logs(self):
        """Test that _fix_workflows_with_cli truncates oversized logs."""
        worker = PRWorker()
        repo_dir = Path("/tmp/repo")
        long_log = "x" * (MAX_WORKFLOW_LOG_CHARS + 100)

        with patch("auto_slopp.workers.pr_worker.run_cli_executor") as mock_cli:
            mock_cli.return_value = {"success": True, "stdout": "done", "return_code": 0}
            worker._fix_workflows_with_cli(repo_dir, [{"name": "CI", "databaseId": 1, "log": long_log}])

        instructions = mock_cli.call_args.kwargs["additional_instructions"]
        assert "truncated" in instructions
        assert "x" * (MAX_WORKFLOW_LOG_CHARS + 100) not in instructions
        assert len(instructions) < MAX_WORKFLOW_LOG_CHARS + 500

    def test_fix_workflows_with_cli_builds_instructions_from_logs(self):
        """Test that _fix_workflows_with_cli passes the failure logs to the CLI executor."""
        worker = PRWorker()
        repo_dir = Path("/tmp/repo")

        with patch("auto_slopp.workers.pr_worker.run_cli_executor") as mock_cli:
            mock_cli.return_value = {"success": True, "stdout": "done", "return_code": 0}
            result = worker._fix_workflows_with_cli(
                repo_dir,
                [
                    {"name": "CI", "databaseId": 1, "log": "log one"},
                    {"name": "Lint", "databaseId": 2, "log": "log two"},
                ],
            )

        assert result["success"] is True
        instructions = mock_cli.call_args.kwargs["additional_instructions"]
        assert "CI" in instructions
        assert "log one" in instructions
        assert "Lint" in instructions
        assert "log two" in instructions
        assert mock_cli.call_args.kwargs["working_directory"] == repo_dir
