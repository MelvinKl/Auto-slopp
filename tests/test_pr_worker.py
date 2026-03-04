"""Tests for PRWorker."""

from pathlib import Path
from unittest.mock import patch

from auto_slopp.workers.pr_worker import PRWorker


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
            patch.object(worker, "_run_tests", return_value={"success": True, "output": "", "error": None}),
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
        ):
            result = worker._process_repository(repo_dir)

        assert result["success"] is True
        assert mock_push_branch.call_count == 1
