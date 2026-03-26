"""End-to-end integration tests for VikunjaWorker."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from auto_slopp.workers.vikunja_worker import VikunjaWorker


class TestVikunjaWorkerEndToEnd:
    """End-to-end integration tests for VikunjaWorker."""

    @pytest.mark.integration
    @pytest.mark.skip(reason="Integration tests need updating for new IssueWorker architecture")
    def test_end_to_end_workflow_with_test_task(self):
        """Test complete VikunjaWorker workflow with a realistic test task."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)

            ai_label = [{"title": "ai"}]
            test_task = {
                "id": 6,
                "title": "Test: Verify VikunjaWorker integration",
                "description": """This is a test task to verify that the VikunjaWorker is working correctly.

The worker should:
1. Find this task in the Auto-slopp project
2. Verify it has the 'ai' label
3. Create a new branch
4. Process the task instructions
5. Push changes (if any)

This task can be used for testing the complete workflow.

For testing purposes, this task can be closed after verification.""",
                "priority": 0,
                "labels": ai_label,
            }

            with (
                patch("auto_slopp.workers.issue_worker.checkout_branch_resilient") as mock_checkout,
                patch("auto_slopp.workers.vikunja_task_source.find_or_create_project") as mock_project,
                patch("auto_slopp.workers.vikunja_task_source.get_open_tasks_by_project") as mock_tasks,
                patch("auto_slopp.workers.vikunja_task_source.verify_blocking_closed") as mock_verify_deps,
                patch("auto_slopp.workers.vikunja_task_source.update_task_status") as mock_status,
                patch("auto_slopp.workers.vikunja_task_source.comment_on_task") as mock_comment,
                patch("auto_slopp.workers.issue_worker.create_and_checkout_branch") as mock_branch,
                patch("auto_slopp.workers.issue_worker.execute_with_instructions") as mock_exec,
                patch("auto_slopp.workers.issue_worker.get_current_branch") as mock_get_branch,
                patch("auto_slopp.workers.issue_worker.push_to_remote") as mock_push,
            ):
                mock_checkout.return_value = True
                mock_project.return_value = {"id": 14, "title": repo_path.name}
                mock_tasks.return_value = [test_task]
                mock_verify_deps.return_value = True
                mock_branch.return_value = True
                mock_exec.return_value = {"success": True}
                mock_get_branch.return_value = "ai/task-6-test-verify-vikunjaworker-integration"
                mock_push.return_value = (True, "pushed")
                mock_status.return_value = True
                mock_comment.return_value = True

                worker = VikunjaWorker(dry_run=False)
                result = worker.run(repo_path)

                assert result["success"] is True
                assert result["tasks_processed"] == 1
                assert result["openagent_executions"] == 1
                assert result["tasks_completed"] == 1
                assert len(result["task_results"]) == 1
                assert result["task_results"][0]["success"] is True

                mock_checkout.assert_called_once()
                mock_project.assert_called_once_with(repo_path.name)
                mock_tasks.assert_called_once_with(14)
                mock_branch.assert_called_once()
                mock_exec.assert_called_once()
                mock_push.assert_called_once()

                assert mock_status.call_count == 2
                status_calls = [call.args for call in mock_status.call_args_list]
                assert (6, "in_progress") in status_calls
                assert (6, "done") in status_calls

                assert mock_comment.call_count == 2

                task_result = result["task_results"][0]
                assert task_result["task_id"] == 6
                assert task_result["task_title"] == "Test: Verify VikunjaWorker integration"
                assert task_result["openagent_executed"] is True
                assert task_result["task_completed"] is True

    @pytest.mark.integration
    @pytest.mark.skip(reason="Integration tests need updating for new IssueWorker architecture")
    def test_end_to_end_workflow_dry_run(self):
        """Test complete VikunjaWorker workflow in dry_run mode."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)

            ai_label = [{"title": "ai"}]
            test_task = {
                "id": 6,
                "title": "Test: Verify VikunjaWorker integration",
                "description": "Test description for dry run",
                "priority": 0,
                "labels": ai_label,
            }

            with (
                patch("auto_slopp.workers.issue_worker.checkout_branch_resilient") as mock_checkout,
                patch("auto_slopp.workers.vikunja_task_source.find_or_create_project") as mock_project,
                patch("auto_slopp.workers.vikunja_task_source.get_open_tasks_by_project") as mock_tasks,
                patch("auto_slopp.workers.vikunja_task_source.verify_blocking_closed") as mock_verify_deps,
            ):
                mock_project.return_value = {"id": 14, "title": repo_path.name}
                mock_tasks.return_value = [test_task]
                mock_verify_deps.return_value = True

                worker = VikunjaWorker(dry_run=True)
                result = worker.run(repo_path)

                assert result["success"] is True
                assert result["dry_run"] is True
                assert result["tasks_processed"] == 1
                assert result["tasks_completed"] == 0

                mock_checkout.assert_not_called()

                task_result = result["task_results"][0]
                assert task_result["success"] is True
                assert task_result["openagent_executed"] is True
                assert task_result["task_id"] == 6

    @pytest.mark.integration
    @pytest.mark.skip(reason="Integration tests need updating for new IssueWorker architecture")
    def test_end_to_end_workflow_no_changes(self):
        """Test complete workflow when no changes are made."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)

            ai_label = [{"title": "ai"}]
            test_task = {
                "id": 7,
                "title": "Test: No changes task",
                "description": "This task should result in no changes",
                "priority": 0,
                "labels": ai_label,
            }

            with (
                patch("auto_slopp.workers.issue_worker.checkout_branch_resilient") as mock_checkout,
                patch("auto_slopp.workers.vikunja_task_source.find_or_create_project") as mock_project,
                patch("auto_slopp.workers.vikunja_task_source.get_open_tasks_by_project") as mock_tasks,
                patch("auto_slopp.workers.vikunja_task_source.verify_blocking_closed") as mock_verify_deps,
                patch("auto_slopp.workers.vikunja_task_source.update_task_status") as mock_status,
                patch("auto_slopp.workers.vikunja_task_source.comment_on_task") as mock_comment,
                patch("auto_slopp.workers.issue_worker.create_and_checkout_branch") as mock_branch,
                patch("auto_slopp.workers.issue_worker.execute_with_instructions") as mock_exec,
                patch("auto_slopp.workers.issue_worker.get_current_branch") as mock_get_branch,
            ):
                mock_checkout.return_value = True
                mock_project.return_value = {"id": 14, "title": repo_path.name}
                mock_tasks.return_value = [test_task]
                mock_verify_deps.return_value = True
                mock_branch.return_value = True
                mock_exec.return_value = {"success": True}
                mock_get_branch.return_value = "main"
                mock_status.return_value = True
                mock_comment.return_value = True

                worker = VikunjaWorker(dry_run=False)
                result = worker.run(repo_path)

                assert result["success"] is True
                assert result["tasks_processed"] == 1
                assert result["tasks_completed"] == 1

                task_result = result["task_results"][0]
                assert task_result["success"] is True
                assert task_result["no_changes"] is True
                assert task_result["task_completed"] is True

                mock_status.assert_any_call(7, "done")
                assert mock_comment.call_count == 2

    @pytest.mark.integration
    @pytest.mark.skip(reason="Integration tests need updating for new IssueWorker architecture")
    def test_end_to_end_workflow_with_failure(self):
        """Test complete workflow with CLI execution failure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)

            ai_label = [{"title": "ai"}]
            test_task = {
                "id": 8,
                "title": "Test: Failing task",
                "description": "This task should fail",
                "priority": 0,
                "labels": ai_label,
            }

            with (
                patch("auto_slopp.workers.issue_worker.checkout_branch_resilient") as mock_checkout,
                patch("auto_slopp.workers.vikunja_task_source.find_or_create_project") as mock_project,
                patch("auto_slopp.workers.vikunja_task_source.get_open_tasks_by_project") as mock_tasks,
                patch("auto_slopp.workers.vikunja_task_source.verify_blocking_closed") as mock_verify_deps,
                patch("auto_slopp.workers.vikunja_task_source.update_task_status") as mock_status,
                patch("auto_slopp.workers.vikunja_task_source.comment_on_task") as mock_comment,
                patch("auto_slopp.workers.issue_worker.create_and_checkout_branch") as mock_branch,
                patch("auto_slopp.workers.issue_worker.execute_with_instructions") as mock_exec,
                patch("auto_slopp.workers.vikunja_worker.get_active_cli_command") as mock_cli,
            ):
                mock_checkout.return_value = True
                mock_project.return_value = {"id": 14, "title": repo_path.name}
                mock_tasks.return_value = [test_task]
                mock_verify_deps.return_value = True
                mock_branch.return_value = True
                mock_exec.return_value = {
                    "success": False,
                    "error": "CLI execution failed",
                }
                mock_cli.return_value = "slopmachine"
                mock_status.return_value = True
                mock_comment.return_value = True

                worker = VikunjaWorker(dry_run=False)
                result = worker.run(repo_path)

                assert result["success"] is True
                assert result["tasks_processed"] == 0
                assert result["tasks_completed"] == 0

                task_result = result["task_results"][0]
                assert task_result["success"] is False
                assert task_result["task_failed"] is True
                assert task_result["task_commented"] is True

                mock_status.assert_any_call(8, "failed")
                assert mock_comment.call_count == 2

    @pytest.mark.integration
    @pytest.mark.skip(reason="Integration tests need updating for new IssueWorker architecture")
    def test_end_to_end_workflow_multiple_tasks(self):
        """Test complete workflow with multiple tasks sorted by priority."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)

            ai_label = [{"title": "ai"}]
            tasks = [
                {
                    "id": 10,
                    "title": "Low priority task",
                    "description": "Low priority description",
                    "priority": 1,
                    "labels": ai_label,
                },
                {
                    "id": 11,
                    "title": "High priority task",
                    "description": "High priority description",
                    "priority": 5,
                    "labels": ai_label,
                },
                {
                    "id": 12,
                    "title": "Medium priority task",
                    "description": "Medium priority description",
                    "priority": 3,
                    "labels": ai_label,
                },
            ]

            with (
                patch("auto_slopp.workers.issue_worker.checkout_branch_resilient") as mock_checkout,
                patch("auto_slopp.workers.vikunja_task_source.find_or_create_project") as mock_project,
                patch("auto_slopp.workers.vikunja_task_source.get_open_tasks_by_project") as mock_tasks,
                patch("auto_slopp.workers.vikunja_task_source.verify_blocking_closed") as mock_verify_deps,
                patch("auto_slopp.workers.vikunja_task_source.update_task_status") as mock_status,
                patch("auto_slopp.workers.vikunja_task_source.comment_on_task") as mock_comment,
                patch("auto_slopp.workers.issue_worker.create_and_checkout_branch") as mock_branch,
                patch("auto_slopp.workers.issue_worker.execute_with_instructions") as mock_exec,
                patch("auto_slopp.workers.issue_worker.get_current_branch") as mock_get_branch,
                patch("auto_slopp.workers.issue_worker.push_to_remote") as mock_push,
            ):
                mock_checkout.return_value = True
                mock_project.return_value = {"id": 14, "title": repo_path.name}
                mock_tasks.return_value = tasks
                mock_verify_deps.return_value = True
                mock_branch.return_value = True
                mock_exec.return_value = {"success": True}
                mock_get_branch.return_value = "ai/task-test"
                mock_push.return_value = (True, "pushed")
                mock_status.return_value = True
                mock_comment.return_value = True

                worker = VikunjaWorker(dry_run=False)
                result = worker.run(repo_path)

                assert result["success"] is True
                assert result["tasks_processed"] == 3
                assert result["openagent_executions"] == 3
                assert result["tasks_completed"] == 3
                assert len(result["task_results"]) == 3

                processed_ids = [t["task_id"] for t in result["task_results"]]
                assert processed_ids == [11, 12, 10]

                assert result["task_results"][0]["task_id"] == 11
                assert result["task_results"][1]["task_id"] == 12
                assert result["task_results"][2]["task_id"] == 10

                assert all(t["success"] for t in result["task_results"])
                assert all(t["openagent_executed"] for t in result["task_results"])
                assert all(t["task_completed"] for t in result["task_results"])

    @pytest.mark.integration
    @pytest.mark.skip(reason="Integration tests need updating for new IssueWorker architecture")
    def test_end_to_end_workflow_task_filtering(self):
        """Test complete workflow with task filtering by label and dependencies."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)

            ai_label = [{"title": "ai"}]
            other_label = [{"title": "other"}]
            tasks = [
                {
                    "id": 20,
                    "title": "Task with ai label and no deps",
                    "description": "Should be processed",
                    "priority": 0,
                    "labels": ai_label,
                },
                {
                    "id": 21,
                    "title": "Task without ai label",
                    "description": "Should be filtered out",
                    "priority": 0,
                    "labels": other_label,
                },
                {
                    "id": 22,
                    "title": "Task with ai label but has deps",
                    "description": "Should be filtered out",
                    "priority": 0,
                    "labels": ai_label,
                },
            ]

            with (
                patch("auto_slopp.workers.issue_worker.checkout_branch_resilient") as mock_checkout,
                patch("auto_slopp.workers.vikunja_task_source.find_or_create_project") as mock_project,
                patch("auto_slopp.workers.vikunja_task_source.get_open_tasks_by_project") as mock_tasks,
                patch("auto_slopp.workers.vikunja_task_source.verify_blocking_closed") as mock_verify_deps,
                patch("auto_slopp.workers.vikunja_task_source.update_task_status") as mock_status,
                patch("auto_slopp.workers.vikunja_task_source.comment_on_task") as mock_comment,
                patch("auto_slopp.workers.issue_worker.create_and_checkout_branch") as mock_branch,
                patch("auto_slopp.workers.issue_worker.execute_with_instructions") as mock_exec,
                patch("auto_slopp.workers.issue_worker.get_current_branch") as mock_get_branch,
                patch("auto_slopp.workers.issue_worker.push_to_remote") as mock_push,
            ):
                mock_checkout.return_value = True
                mock_project.return_value = {"id": 14, "title": repo_path.name}
                mock_tasks.return_value = tasks
                mock_verify_deps.side_effect = lambda tid: tid == 20
                mock_branch.return_value = True
                mock_exec.return_value = {"success": True}
                mock_get_branch.return_value = "ai/task-20"
                mock_push.return_value = (True, "pushed")
                mock_status.return_value = True
                mock_comment.return_value = True

                worker = VikunjaWorker(dry_run=False)
                result = worker.run(repo_path)

                assert result["success"] is True
                assert result["tasks_processed"] == 1
                assert len(result["task_results"]) == 1

                assert result["task_results"][0]["task_id"] == 20
                assert result["task_results"][0]["success"] is True

    @pytest.mark.integration
    @pytest.mark.skip(reason="Integration tests need updating for new IssueWorker architecture")
    def test_end_to_end_workflow_instruction_building(self):
        """Test that instructions are built correctly for end-to-end workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)

            ai_label = [{"title": "ai"}]
            test_task = {
                "id": 30,
                "title": "Test: Instruction building",
                "description": "Test description for instruction building",
                "priority": 0,
                "labels": ai_label,
            }

            with (
                patch("auto_slopp.workers.issue_worker.checkout_branch_resilient") as mock_checkout,
                patch("auto_slopp.workers.vikunja_task_source.find_or_create_project") as mock_project,
                patch("auto_slopp.workers.vikunja_task_source.get_open_tasks_by_project") as mock_tasks,
                patch("auto_slopp.workers.vikunja_task_source.verify_blocking_closed") as mock_verify_deps,
                patch("auto_slopp.workers.vikunja_task_source.update_task_status") as mock_status,
                patch("auto_slopp.workers.vikunja_task_source.comment_on_task") as mock_comment,
                patch("auto_slopp.workers.issue_worker.create_and_checkout_branch") as mock_branch,
                patch("auto_slopp.workers.issue_worker.execute_with_instructions") as mock_exec,
                patch("auto_slopp.workers.issue_worker.get_current_branch") as mock_get_branch,
                patch("auto_slopp.workers.issue_worker.push_to_remote") as mock_push,
            ):
                mock_checkout.return_value = True
                mock_project.return_value = {"id": 14, "title": repo_path.name}
                mock_tasks.return_value = [test_task]
                mock_verify_deps.return_value = True
                mock_branch.return_value = True
                mock_exec.return_value = {"success": True}
                mock_get_branch.return_value = "ai/task-30-test-instruction-building"
                mock_push.return_value = (True, "pushed")
                mock_status.return_value = True
                mock_comment.return_value = True

                worker = VikunjaWorker(dry_run=False)
                result = worker.run(repo_path)

                assert result["success"] is True
                assert mock_exec.called

                instructions_call = mock_exec.call_args[0][0]
                assert "Test: Instruction building" in instructions_call
                assert "Test description for instruction building" in instructions_call
                assert "already on branch 'ai/task-30-test-instruction-building'" in instructions_call
                assert "Plan:" in instructions_call
                assert "make test" in instructions_call
                assert "make lint" in instructions_call
