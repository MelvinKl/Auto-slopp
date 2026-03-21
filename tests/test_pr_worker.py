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
