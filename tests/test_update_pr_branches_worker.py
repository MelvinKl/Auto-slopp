"""Tests for UpdatePRBranchesWorker."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from auto_slopp.utils.github_operations import GitHubOperationError
from auto_slopp.workers.update_pr_branches_worker import UpdatePRBranchesWorker


class TestUpdatePRBranchesWorker:
    """Test cases for UpdatePRBranchesWorker."""

    @pytest.fixture
    def temp_repo_dir(self):
        """Create a temporary repository directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_dir = Path(temp_dir) / "test_repo"
            repo_dir.mkdir()
            os.chdir(repo_dir)
            os.system("git init")
            os.system("git config user.email 'test@example.com'")
            os.system("git config user.name 'Test User'")
            os.system("git checkout -b main")
            os.system("echo 'test' > test.txt")
            os.system("git add test.txt")
            os.system("git commit -m 'Initial commit'")
            yield repo_dir

    @pytest.fixture
    def temp_task_dir(self):
        """Create a temporary task directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir) / "test_task"

    def test_worker_initialization(self):
        """Test worker initialization."""
        worker = UpdatePRBranchesWorker()
        assert worker is not None
        assert worker.logger is not None

    def test_run_with_nonexistent_repo(self, temp_task_dir):
        """Test run with non-existent repository."""
        worker = UpdatePRBranchesWorker()
        result = worker.run(Path("/tmp/nonexistent"), temp_task_dir)

        assert result["success"] is False
        assert result["worker_name"] == "UpdatePRBranchesWorker"
        assert "does not exist" in result["error"]

    def test_get_open_pr_branches_empty(self, temp_repo_dir, temp_task_dir):
        """Test getting open PR branches when none exist."""
        worker = UpdatePRBranchesWorker()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                stdout="[]",
                stderr="",
                returncode=0,
            )

            branches = worker._get_open_pr_branches(temp_repo_dir)
            assert branches == []

    def test_get_open_pr_branches_with_prs(self, temp_repo_dir):
        """Test getting open PR branches when PRs exist."""
        worker = UpdatePRBranchesWorker()

        pr_data = [
            {"headRefName": "feature-branch-1"},
            {"headRefName": "feature-branch-2"},
        ]

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                stdout=json.dumps(pr_data),
                stderr="",
                returncode=0,
            )

            branches = worker._get_open_pr_branches(temp_repo_dir)
            assert branches == ["feature-branch-1", "feature-branch-2"]

    def test_get_open_pr_branches_error(self, temp_repo_dir):
        """Test error handling when getting PR branches fails."""
        worker = UpdatePRBranchesWorker()

        with patch("auto_slopp.utils.github_operations.subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                stdout="",
                stderr="Error getting PRs",
                returncode=1,
            )

            with pytest.raises(GitHubOperationError):
                worker._get_open_pr_branches(temp_repo_dir)

    @patch("auto_slopp.workers.update_pr_branches_worker.checkout_branch_resilient")
    def test_checkout_branch_success(self, mock_checkout, temp_repo_dir):
        """Test successful branch checkout."""
        worker = UpdatePRBranchesWorker()
        mock_checkout.return_value = True

        result = worker._checkout_branch(temp_repo_dir, "feature-branch")

        assert result is True
        mock_checkout.assert_called_once()

    @patch("auto_slopp.workers.update_pr_branches_worker.checkout_branch_resilient")
    def test_checkout_branch_failure(self, mock_checkout, temp_repo_dir):
        """Test failed branch checkout."""
        worker = UpdatePRBranchesWorker()
        mock_checkout.return_value = False

        result = worker._checkout_branch(temp_repo_dir, "feature-branch")

        assert result is False

    @patch("subprocess.run")
    def test_merge_main_success(self, mock_run, temp_repo_dir):
        """Test successful merge of origin/main."""
        worker = UpdatePRBranchesWorker()

        mock_run.return_value = Mock(
            stdout="Merge completed",
            stderr="",
            returncode=0,
        )

        result = worker._merge_main(temp_repo_dir)

        assert result is True
        assert mock_run.call_count == 2

    @patch("subprocess.run")
    def test_merge_main_failure(self, mock_run, temp_repo_dir):
        """Test failed merge of origin/main."""
        worker = UpdatePRBranchesWorker()

        mock_run.return_value = Mock(
            stdout="",
            stderr="Merge conflict",
            returncode=1,
        )

        result = worker._merge_main(temp_repo_dir)

        assert result is False
        assert mock_run.call_count >= 1

    @patch("subprocess.run")
    def test_push_branch_success(self, mock_run, temp_repo_dir):
        """Test successful push of branch."""
        worker = UpdatePRBranchesWorker()

        mock_run.return_value = Mock(
            stdout="Pushed",
            stderr="",
            returncode=0,
        )

        result = worker._push_branch(temp_repo_dir, "feature-branch")

        assert result is True

    @patch("subprocess.run")
    def test_push_branch_failure(self, mock_run, temp_repo_dir):
        """Test failed push of branch."""
        worker = UpdatePRBranchesWorker()

        mock_run.return_value = Mock(
            stdout="",
            stderr="Push failed",
            returncode=1,
        )

        result = worker._push_branch(temp_repo_dir, "feature-branch")

        assert result is False

    def test_result_structure(self, temp_repo_dir, temp_task_dir):
        """Test that worker result has correct structure."""
        worker = UpdatePRBranchesWorker()

        with patch.object(worker, "_get_open_pr_branches", return_value=[]):
            result = worker.run(temp_repo_dir, temp_task_dir)

        assert "worker_name" in result
        assert result["worker_name"] == "UpdatePRBranchesWorker"
        assert "success" in result
        assert "branches_updated" in result
        assert "branches_failed" in result
        assert "branch_results" in result
        assert isinstance(result["branches_updated"], int)
        assert isinstance(result["branches_failed"], int)
        assert isinstance(result["branch_results"], list)

    @patch("auto_slopp.workers.update_pr_branches_worker.checkout_branch_resilient")
    @patch("subprocess.run")
    def test_full_workflow(self, mock_run, mock_checkout, temp_repo_dir, temp_task_dir):
        """Test full workflow of updating PR branches."""
        worker = UpdatePRBranchesWorker()

        mock_checkout.return_value = True

        def run_side_effect(*args, **kwargs):
            cmd = args[0] if args else kwargs.get("cmd", [])
            if "gh" in cmd:
                return Mock(
                    stdout=json.dumps([{"headRefName": "feature-branch"}]),
                    stderr="",
                    returncode=0,
                )
            if "fetch" in cmd:
                return Mock(stdout="", stderr="", returncode=0)
            if "merge" in cmd:
                return Mock(stdout="", stderr="", returncode=0)
            if "push" in cmd:
                return Mock(stdout="", stderr="", returncode=0)
            return Mock(stdout="", stderr="", returncode=0)

        mock_run.side_effect = run_side_effect

        result = worker.run(temp_repo_dir, temp_task_dir)

        assert result["success"] is True
        assert result["branches_updated"] == 1
        assert result["branches_failed"] == 0
