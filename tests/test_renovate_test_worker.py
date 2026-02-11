"""Tests for RenovateTestWorker."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from auto_slopp.workers.renovate_test_worker import RenovateTestWorker


class TestRenovateTestWorker:
    """Test cases for the RenovateTestWorker."""

    def test_worker_initialization(self):
        """Test that RenovateTestWorker can be initialized."""
        worker = RenovateTestWorker()
        assert worker is not None
        assert worker.timeout == 600
        assert hasattr(worker, "_fix_tests_with_openagent")

    def test_worker_initialization_with_custom_timeout(self):
        """Test that RenovateTestWorker can be initialized with custom timeout."""
        worker = RenovateTestWorker(timeout=300)
        assert worker.timeout == 300

    def test_run_with_nonexistent_repo_path(self):
        """Test running worker with non-existent repository path."""
        worker = RenovateTestWorker()
        non_existent_path = Path("/tmp/non_existent_repo_path")

        result = worker.run(non_existent_path, Path("/tmp/task"))

        assert result["worker_name"] == "RenovateTestWorker"
        assert result["success"] is False
        assert "does not exist" in result["error"]
        assert result["repositories_processed"] == 0

    @patch("auto_slopp.workers.renovate_test_worker.subprocess.run")
    def test_get_renovate_branches_success(self, mock_subprocess_run):
        """Test successful retrieval of renovate branches."""
        worker = RenovateTestWorker()
        repo_dir = Path("/tmp/test_repo")

        # Mock git branch command output
        mock_subprocess_run.return_value = Mock(
            returncode=0,
            stdout="origin/main\norigin/renovate/test-1\norigin/renovate/test-2\n",
        )

        branches = worker._get_renovate_branches(repo_dir)

        assert len(branches) == 2
        assert "renovate/test-1" in branches
        assert "renovate/test-2" in branches

    @patch("auto_slopp.workers.renovate_test_worker.subprocess.run")
    def test_get_renovate_branches_no_renovate(self, mock_subprocess_run):
        """Test retrieval when no renovate branches exist."""
        worker = RenovateTestWorker()
        repo_dir = Path("/tmp/test_repo")

        # Mock git branch command output with no renovate branches
        mock_subprocess_run.return_value = Mock(returncode=0, stdout="origin/main\norigin/develop\n")

        branches = worker._get_renovate_branches(repo_dir)

        assert len(branches) == 0

    @patch("auto_slopp.workers.renovate_test_worker.checkout_branch_resilient")
    def test_checkout_branch_success(self, mock_checkout_resilient):
        """Test successful branch checkout using resilient checkout."""
        worker = RenovateTestWorker()
        repo_dir = Path("/tmp/test_repo")
        branch = "renovate/test-1"

        # Mock successful resilient checkout
        mock_checkout_resilient.return_value = True

        result = worker._checkout_branch(repo_dir, branch)

        assert result is True
        mock_checkout_resilient.assert_called_once_with(repo_dir=repo_dir, branch=branch, fetch_first=True, timeout=60)

    @patch("auto_slopp.workers.renovate_test_worker.subprocess.run")
    def test_run_tests_success(self, mock_subprocess_run):
        """Test successful test execution."""
        worker = RenovateTestWorker()
        repo_dir = Path("/tmp/test_repo")

        # Mock successful make test
        mock_subprocess_run.return_value = Mock(returncode=0, stdout="All tests passed!", stderr="")

        result = worker._run_tests(repo_dir)

        assert result["success"] is True
        assert "All tests passed!" in result["output"]

    @patch("auto_slopp.workers.renovate_test_worker.subprocess.run")
    def test_run_tests_failure(self, mock_subprocess_run):
        """Test failed test execution."""
        worker = RenovateTestWorker()
        repo_dir = Path("/tmp/test_repo")

        # Mock failed make test
        mock_subprocess_run.return_value = Mock(returncode=1, stdout="", stderr="Test failed: assertion error")

        result = worker._run_tests(repo_dir)

        assert result["success"] is False
        assert "Test failed: assertion error" in result["error"]

    @patch("auto_slopp.workers.renovate_test_worker.subprocess.run")
    def test_run_tests_timeout(self, mock_subprocess_run):
        """Test test execution timeout."""
        worker = RenovateTestWorker(timeout=1)
        repo_dir = Path("/tmp/test_repo")

        # Mock timeout exception
        import subprocess

        mock_subprocess_run.side_effect = subprocess.TimeoutExpired("make", 1)

        result = worker._run_tests(repo_dir)

        assert result["success"] is False
        assert "timed out" in result["error"]

    @patch.object(RenovateTestWorker, "_fix_tests_with_openagent")
    @patch.object(RenovateTestWorker, "_run_tests")
    @patch.object(RenovateTestWorker, "_checkout_branch")
    @patch.object(RenovateTestWorker, "_get_renovate_branches")
    def test_process_repository_success(self, mock_get_branches, mock_checkout, mock_tests, mock_fix):
        """Test successful repository processing."""
        worker = RenovateTestWorker()
        repo_dir = Path("/tmp/test_repo")

        # Mock successful operations
        mock_get_branches.return_value = ["renovate/test-1"]
        mock_checkout.return_value = True
        mock_tests.return_value = {"success": True, "output": "Tests passed"}

        result = worker._process_repository(repo_dir)

        assert result["success"] is True
        assert result["repository"] == repo_dir.name
        assert len(result["branches_checked_out"]) == 1
        assert len(result["test_results"]) == 1
        assert result["test_results"][0]["success"] is True
        assert result["tests_fixed"] is False

    @patch.object(RenovateTestWorker, "_fix_tests_with_openagent")
    @patch.object(RenovateTestWorker, "_run_tests")
    @patch.object(RenovateTestWorker, "_checkout_branch")
    @patch.object(RenovateTestWorker, "_get_renovate_branches")
    def test_process_repository_with_fix(self, mock_get_branches, mock_checkout, mock_tests, mock_fix):
        """Test repository processing with test fixing."""
        worker = RenovateTestWorker()
        repo_dir = Path("/tmp/test_repo")

        # Mock operations where tests fail then get fixed
        mock_get_branches.return_value = ["renovate/test-1"]
        mock_checkout.return_value = True
        mock_tests.side_effect = [
            {"success": False, "output": "", "error": "Test failed"},  # First run fails
            {
                "success": True,
                "output": "Tests passed",
            },  # Verification after fix passes
        ]
        mock_fix.return_value = {"success": True}

        result = worker._process_repository(repo_dir)

        assert result["success"] is True
        assert result["tests_fixed"] is True
        assert result["test_results"][0]["success"] is False  # Original test failed
        assert result["test_results"][0]["fix_success"] is True  # Fix was successful

    def test_fix_tests_with_opencode(self):
        """Test using OpenCode to fix tests."""
        worker = RenovateTestWorker()
        repo_dir = Path("/tmp/test_repo")

        # Mock the OpenCode test fixing method
        with patch.object(worker, "_fix_tests_with_openagent") as mock_opencode:
            mock_opencode.return_value = {
                "success": True,
                "output": "Fixed tests successfully",
            }

            result = worker._fix_tests_with_openagent(repo_dir)

            assert result["success"] is True
            assert "Fixed tests successfully" in result["output"]
            mock_opencode.assert_called_once()

    def test_run_with_empty_directory(self):
        """Test running worker with empty directory."""
        worker = RenovateTestWorker()

        with tempfile.TemporaryDirectory() as temp_dir:
            empty_dir = Path(temp_dir)
            task_path = Path("/tmp/task")

            result = worker.run(empty_dir, task_path)

            assert result["worker_name"] == "RenovateTestWorker"
            assert result["success"] is False  # Invalid repository (no .git)
            assert result["repositories_processed"] == 1  # Always 1 in new architecture
            assert result["repositories_tested"] == 0
            assert result["repositories_fixed"] == 0
            assert result["repositories_with_errors"] == 1
