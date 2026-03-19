"""Tests for PRWorker."""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

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
        ):
            result = worker._process_repository(repo_dir)

        assert result["success"] is True
        assert mock_push_branch.call_count == 1

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

        with patch("auto_slopp.workers.pr_worker.get_open_prs", return_value=mock_prs):
            with patch("auto_slopp.workers.pr_worker.settings") as mock_settings:
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

        with patch("auto_slopp.workers.pr_worker.get_open_prs", return_value=mock_prs):
            with patch("auto_slopp.workers.pr_worker.settings") as mock_settings:
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

        with patch("auto_slopp.workers.pr_worker.get_open_prs", return_value=mock_prs):
            with patch("auto_slopp.workers.pr_worker.settings") as mock_settings:
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

        with patch("auto_slopp.workers.pr_worker.get_open_prs", return_value=mock_prs):
            with patch("auto_slopp.workers.pr_worker.settings") as mock_settings:
                mock_settings.github_issue_worker_allowed_creator = "MelvinKl"
                branches = worker._get_open_pr_branches(repo_dir)

        assert len(branches) == 1
        assert "feature-3" in branches

    def test_run_tests_success(self):
        """Test successful test execution."""
        worker = PRWorker()
        repo_dir = Path("/tmp/repo")

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "All tests passed"

        with patch("subprocess.run", return_value=mock_result):
            result = worker._run_tests(repo_dir)
            assert result["success"] is True
            assert result["output"] == "All tests passed"
            assert result["error"] is None

    def test_run_tests_failure(self):
        """Test failed test execution."""
        worker = PRWorker()
        repo_dir = Path("/tmp/repo")

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = "Tests failed"
        mock_result.stderr = "Error: test failed"

        with patch("subprocess.run", return_value=mock_result):
            result = worker._run_tests(repo_dir)
            assert result["success"] is False
            assert result["output"] == "Tests failed"
            assert result["error"] == "Error: test failed"

    def test_run_tests_timeout(self):
        """Test test execution timeout."""
        worker = PRWorker(timeout=5)
        repo_dir = Path("/tmp/repo")

        with patch(
            "subprocess.run",
            side_effect=subprocess.TimeoutExpired(cmd="make test", timeout=5),
        ):
            result = worker._run_tests(repo_dir)
            assert result["success"] is False
            assert "timed out" in result["error"]

    def test_run_tests_exception(self):
        """Test test execution exception."""
        worker = PRWorker()
        repo_dir = Path("/tmp/repo")

        with patch("subprocess.run", side_effect=OSError("Test error")):
            result = worker._run_tests(repo_dir)
            assert result["success"] is False
            assert "Error running tests" in result["error"]

    def test_checkout_branch_success(self):
        """Test successful branch checkout."""
        worker = PRWorker()
        repo_dir = Path("/tmp/repo")

        with patch(
            "auto_slopp.workers.pr_worker.checkout_branch_resilient",
            return_value=True,
        ):
            result = worker._checkout_branch(repo_dir, "feature")
            assert result is True

    def test_checkout_branch_failure(self):
        """Test failed branch checkout."""
        worker = PRWorker()
        repo_dir = Path("/tmp/repo")

        with patch(
            "auto_slopp.workers.pr_worker.checkout_branch_resilient",
            return_value=False,
        ):
            result = worker._checkout_branch(repo_dir, "feature")
            assert result is False

    def test_update_branch_with_main_success(self):
        """Test successful branch update with main."""
        worker = PRWorker()
        repo_dir = Path("/tmp/repo")

        with patch(
            "auto_slopp.workers.pr_worker.merge_main_into_branch",
            return_value=(True, "Merge successful"),
        ):
            result = worker._update_branch_with_main(repo_dir, "feature")
            assert result is True

    def test_update_branch_with_main_failure(self):
        """Test failed branch update with main."""
        worker = PRWorker()
        repo_dir = Path("/tmp/repo")

        with patch(
            "auto_slopp.workers.pr_worker.merge_main_into_branch",
            return_value=(False, "Merge conflict"),
        ):
            result = worker._update_branch_with_main(repo_dir, "feature")
            assert result is False

    def test_push_branch_success(self):
        """Test successful branch push."""
        worker = PRWorker()
        repo_dir = Path("/tmp/repo")

        with patch(
            "auto_slopp.workers.pr_worker.push_branch",
            return_value=True,
        ):
            result = worker._push_branch(repo_dir, "feature")
            assert result is True

    def test_push_branch_failure(self):
        """Test failed branch push."""
        worker = PRWorker()
        repo_dir = Path("/tmp/repo")

        with patch(
            "auto_slopp.workers.pr_worker.push_branch",
            return_value=False,
        ):
            result = worker._push_branch(repo_dir, "feature")
            assert result is False

    def test_fix_tests_with_cli_success(self):
        """Test successful test fix with CLI."""
        worker = PRWorker()
        repo_dir = Path("/tmp/repo")

        with patch(
            "auto_slopp.workers.pr_worker.run_cli_executor",
            return_value={"success": True, "stdout": "Tests fixed", "return_code": 0},
        ):
            result = worker._fix_tests_with_cli(repo_dir)
            assert result["success"] is True
            assert result["output"] == "Tests fixed"

    def test_fix_tests_with_cli_failure(self):
        """Test failed test fix with CLI."""
        worker = PRWorker()
        repo_dir = Path("/tmp/repo")

        with patch(
            "auto_slopp.workers.pr_worker.run_cli_executor",
            return_value={"success": False, "error": "Fix failed", "return_code": 1},
        ):
            result = worker._fix_tests_with_cli(repo_dir)
            assert result["success"] is False
            assert result["error"] == "Fix failed"

    def test_fix_merge_with_cli_success(self):
        """Test successful merge fix with CLI."""
        worker = PRWorker()
        repo_dir = Path("/tmp/repo")

        with patch(
            "auto_slopp.workers.pr_worker.run_cli_executor",
            return_value={"success": True, "stdout": "Merge fixed", "return_code": 0},
        ):
            result = worker._fix_merge_with_cli(repo_dir)
            assert result["success"] is True
            assert result["output"] == "Merge fixed"

    def test_fix_merge_with_cli_failure(self):
        """Test failed merge fix with CLI."""
        worker = PRWorker()
        repo_dir = Path("/tmp/repo")

        with patch(
            "auto_slopp.workers.pr_worker.run_cli_executor",
            return_value={"success": False, "error": "Fix failed", "return_code": 1},
        ):
            result = worker._fix_merge_with_cli(repo_dir)
            assert result["success"] is False
            assert result["error"] == "Fix failed"

    def test_process_repository_with_merge_conflict_fixed(self):
        """Test processing repository when merge conflict is fixed by CLI."""
        worker = PRWorker()
        repo_dir = Path("/tmp/repo")

        with (
            patch.object(worker, "_get_open_pr_branches", return_value=["feature"]),
            patch.object(worker, "_checkout_branch", return_value=True),
            patch.object(worker, "_update_branch_with_main", side_effect=[False, True]),
            patch.object(
                worker,
                "_fix_merge_with_cli",
                return_value={"success": True},
            ),
            patch.object(
                worker,
                "_run_tests",
                return_value={"success": True, "output": "", "error": None},
            ),
            patch.object(worker, "_push_branch", return_value=True) as mock_push,
        ):
            result = worker._process_repository(repo_dir)

        assert result["success"] is True
        assert mock_push.call_count == 1

    def test_process_repository_with_merge_fix_failure(self):
        """Test processing repository when merge fix fails."""
        worker = PRWorker()
        repo_dir = Path("/tmp/repo")

        with (
            patch.object(worker, "_get_open_pr_branches", return_value=["feature"]),
            patch.object(worker, "_checkout_branch", return_value=True),
            patch.object(worker, "_update_branch_with_main", side_effect=[False, True]),
            patch.object(
                worker,
                "_fix_merge_with_cli",
                return_value={"success": False, "error": "Cannot fix"},
            ),
        ):
            result = worker._process_repository(repo_dir)

        assert result["error"] is not None
        assert "Cannot fix" in result["error"]

    def test_process_repository_checkout_failure(self):
        """Test processing repository when checkout fails."""
        worker = PRWorker()
        repo_dir = Path("/tmp/repo")

        with (
            patch.object(worker, "_get_open_pr_branches", return_value=["feature"]),
            patch.object(worker, "_checkout_branch", return_value=False),
        ):
            result = worker._process_repository(repo_dir)

        assert result["success"] is True
        assert result["error"] == "Failed to checkout branch feature"

    def test_process_repository_no_open_pr_branches(self):
        """Test processing repository with no open PR branches."""
        worker = PRWorker()
        repo_dir = Path("/tmp/repo")

        with patch.object(worker, "_get_open_pr_branches", return_value=[]):
            result = worker._process_repository(repo_dir)

        assert result["success"] is True
        assert result["error"] is None

    def test_process_repository_push_failure(self):
        """Test processing repository when push fails after tests pass."""
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
            patch.object(worker, "_push_branch", return_value=False),
        ):
            result = worker._process_repository(repo_dir)

        assert result["success"] is True
        assert "Failed to push" in result["error"]

    def test_run_with_invalid_repository(self):
        """Test run with invalid repository."""
        worker = PRWorker()
        repo_dir = MagicMock(spec=Path)
        repo_dir.exists.return_value = True
        repo_dir.name = "nonexistent"

        with patch(
            "auto_slopp.workers.pr_worker.validate_repository",
            return_value={"valid": False, "errors": ["Not a git repo"]},
        ):
            result = worker.run(repo_dir)

        assert result["success"] is False
        assert result["repositories_invalid"] == 1
        assert result["repositories_with_errors"] == 1

    def test_process_repository_exception(self):
        """Test processing repository handles unexpected exceptions."""
        worker = PRWorker()
        repo_dir = Path("/tmp/repo")

        with (
            patch.object(
                worker,
                "_get_open_pr_branches",
                side_effect=RuntimeError("Unexpected error"),
            ),
        ):
            result = worker._process_repository(repo_dir)

        assert result["success"] is False
        assert "Unexpected error" in result["error"]
