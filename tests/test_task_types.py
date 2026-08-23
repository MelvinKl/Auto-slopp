"""Tests for task_types module."""

import pytest

from auto_slopp.workers.task_types import (
    TaskResult,
    TaskStatus,
    validate_task_result,
)


class TestValidateTaskResult:
    """Tests for validate_task_result function."""

    def test_valid_skipped_result(self):
        """Test that a valid skipped result passes validation."""
        result: TaskResult = {
            "repository": "test-repo",
            "task_id": 1,
            "task_title": "Test Task",
            "success": None,
            "status": TaskStatus.SKIPPED.value,
            "openagent_executed": False,
            "openagent_executions": 0,
            "task_completed": False,
            "tasks_completed": 0,
            "pr_created": False,
            "prs_created": 0,
            "error": None,
            "ralph_loops_executed": 0,
            "ralph_steps_completed": 0,
            "skipped": True,
            "skip_reason": "LLM unavailable",
        }
        validate_task_result(result)

    def test_valid_success_result(self):
        """Test that a valid success result passes validation."""
        result: TaskResult = {
            "repository": "test-repo",
            "task_id": 1,
            "task_title": "Test Task",
            "success": True,
            "status": TaskStatus.SUCCESS.value,
            "openagent_executed": True,
            "openagent_executions": 1,
            "task_completed": True,
            "tasks_completed": 1,
            "pr_created": True,
            "prs_created": 1,
            "error": None,
            "ralph_loops_executed": 1,
            "ralph_steps_completed": 5,
        }
        validate_task_result(result)

    def test_valid_failure_result(self):
        """Test that a valid failure result passes validation."""
        result: TaskResult = {
            "repository": "test-repo",
            "task_id": 1,
            "task_title": "Test Task",
            "success": False,
            "status": TaskStatus.FAILURE.value,
            "openagent_executed": True,
            "openagent_executions": 1,
            "task_completed": False,
            "tasks_completed": 0,
            "pr_created": False,
            "prs_created": 0,
            "error": "Some error",
            "ralph_loops_executed": 1,
            "ralph_steps_completed": 3,
        }
        validate_task_result(result)

    def test_skipped_status_without_skipped_flag_raises(self):
        """Test that status=SKIPPED without skipped=True raises ValueError."""
        result: TaskResult = {
            "repository": "test-repo",
            "task_id": 1,
            "task_title": "Test Task",
            "success": None,
            "status": TaskStatus.SKIPPED.value,
            "openagent_executed": False,
            "openagent_executions": 0,
            "task_completed": False,
            "tasks_completed": 0,
            "pr_created": False,
            "prs_created": 0,
            "error": None,
            "ralph_loops_executed": 0,
            "ralph_steps_completed": 0,
            "skipped": False,
        }
        with pytest.raises(ValueError, match="When status is SKIPPED, skipped must be True"):
            validate_task_result(result)

    def test_skipped_flag_without_skipped_status_raises(self):
        """Test that skipped=True without status=SKIPPED raises ValueError."""
        result: TaskResult = {
            "repository": "test-repo",
            "task_id": 1,
            "task_title": "Test Task",
            "success": True,
            "status": TaskStatus.SUCCESS.value,
            "openagent_executed": True,
            "openagent_executions": 1,
            "task_completed": True,
            "tasks_completed": 1,
            "pr_created": True,
            "prs_created": 1,
            "error": None,
            "ralph_loops_executed": 1,
            "ralph_steps_completed": 5,
            "skipped": True,
        }
        with pytest.raises(ValueError, match="skipped can only be True when status is SKIPPED"):
            validate_task_result(result)

    def test_success_none_without_skipped_status_raises(self):
        """Test that success=None without status=SKIPPED raises ValueError."""
        result: TaskResult = {
            "repository": "test-repo",
            "task_id": 1,
            "task_title": "Test Task",
            "success": None,
            "status": TaskStatus.SUCCESS.value,
            "openagent_executed": True,
            "openagent_executions": 1,
            "task_completed": True,
            "tasks_completed": 1,
            "pr_created": True,
            "prs_created": 1,
            "error": None,
            "ralph_loops_executed": 1,
            "ralph_steps_completed": 5,
        }
        with pytest.raises(ValueError, match="When success is None, status must be SKIPPED"):
            validate_task_result(result)

    def test_skipped_status_without_success_none_raises(self):
        """Test that status=SKIPPED without success=None raises ValueError."""
        result: TaskResult = {
            "repository": "test-repo",
            "task_id": 1,
            "task_title": "Test Task",
            "success": True,
            "status": TaskStatus.SKIPPED.value,
            "openagent_executed": False,
            "openagent_executions": 0,
            "task_completed": False,
            "tasks_completed": 0,
            "pr_created": False,
            "prs_created": 0,
            "error": None,
            "ralph_loops_executed": 0,
            "ralph_steps_completed": 0,
            "skipped": True,
        }
        with pytest.raises(ValueError, match="When status is SKIPPED, success must be None"):
            validate_task_result(result)

    def test_legacy_skipped_field_sync_with_status(self):
        """Test that manually manipulated skipped field is caught by validation.

        This verifies the legacy `skipped` field stays in sync with `status`
        when manually manipulated (e.g., by external code).
        """
        # Start with a valid skipped result
        result: TaskResult = {
            "repository": "test-repo",
            "task_id": 1,
            "task_title": "Test Task",
            "success": None,
            "status": TaskStatus.SKIPPED.value,
            "openagent_executed": False,
            "openagent_executions": 0,
            "task_completed": False,
            "tasks_completed": 0,
            "pr_created": False,
            "prs_created": 0,
            "error": None,
            "ralph_loops_executed": 0,
            "ralph_steps_completed": 0,
            "skipped": True,
            "skip_reason": "LLM unavailable",
        }
        validate_task_result(result)

        # Manually break the sync: keep status=SKIPPED but set skipped=False
        result["skipped"] = False
        with pytest.raises(ValueError, match="When status is SKIPPED, skipped must be True"):
            validate_task_result(result)

        # Manually break the sync: keep status=SUCCESS but set skipped=True
        result["status"] = TaskStatus.SUCCESS.value
        result["success"] = True
        result["skipped"] = True
        with pytest.raises(ValueError, match="skipped can only be True when status is SKIPPED"):
            validate_task_result(result)

    def test_pending_result_without_skipped(self):
        """Test that a pending (non-terminal) result fails validation."""
        result: TaskResult = {
            "repository": "test-repo",
            "task_id": 1,
            "task_title": "Test Task",
            "success": True,
            "status": TaskStatus.PENDING.value,
            "openagent_executed": False,
            "openagent_executions": 0,
            "task_completed": False,
            "tasks_completed": 0,
            "pr_created": False,
            "prs_created": 0,
            "error": None,
            "ralph_loops_executed": 0,
            "ralph_steps_completed": 0,
        }
        with pytest.raises(ValueError, match="terminal status"):
            validate_task_result(result)

    def test_skipped_result_with_empty_skip_reason(self):
        """Test that a skipped result with empty skip_reason passes validation."""
        result: TaskResult = {
            "repository": "test-repo",
            "task_id": 1,
            "task_title": "Test Task",
            "success": None,
            "status": TaskStatus.SKIPPED.value,
            "openagent_executed": False,
            "openagent_executions": 0,
            "task_completed": False,
            "tasks_completed": 0,
            "pr_created": False,
            "prs_created": 0,
            "error": None,
            "ralph_loops_executed": 0,
            "ralph_steps_completed": 0,
            "skipped": True,
            "skip_reason": "",
        }
        validate_task_result(result)
