"""Tests for BackportWorker."""

import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from auto_slopp.workers.backport_worker import BackportWorker


class TestBackportWorker:
    """Test cases for BackportWorker."""

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
        """Test worker initialization with different parameters."""
        worker = BackportWorker()
        assert worker.source_branch == "main"
        assert worker.target_branches == []
        assert worker.commits == []
        assert worker.dry_run is False

        worker = BackportWorker(
            source_branch="develop",
            target_branches=["release-1.0", "release-2.0"],
            commits=["abc123", "def456"],
            dry_run=True,
        )
        assert worker.source_branch == "develop"
        assert worker.target_branches == ["release-1.0", "release-2.0"]
        assert worker.commits == ["abc123", "def456"]
        assert worker.dry_run is True

    def test_validate_input_nonexistent_repo(self):
        """Test validation with non-existent repository."""
        worker = BackportWorker()
        start_time = datetime.now(timezone.utc)
        result = worker._validate_input(
            Path("/nonexistent/path"),
            Path("/task"),
            start_time,
        )
        assert result is not None
        assert result["success"] is False
        assert "does not exist" in result["error"]

    def test_create_results_dict(self):
        """Test results dictionary creation."""
        worker = BackportWorker(
            source_branch="main",
            target_branches=["release-1.0"],
            commits=["abc123"],
            dry_run=True,
        )
        result = worker._create_results_dict(
            Mock(),
            Path("/repo"),
            Path("/task"),
        )
        assert result["worker_name"] == "BackportWorker"
        assert result["source_branch"] == "main"
        assert result["target_branches"] == ["release-1.0"]
        assert result["commits"] == ["abc123"]
        assert result["dry_run"] is True
        assert result["success"] is True

    def test_get_commits_to_backport_with_explicit_commits(self):
        """Test getting commits when explicitly provided."""
        worker = BackportWorker(commits=["abc123", "def456"])
        commits = worker._get_commits_to_backport(Path("/fake"))
        assert commits == ["abc123", "def456"]

    def test_get_commits_to_backport_from_git(self):
        """Test getting commits from git log."""
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
            os.system("echo 'test2' > test2.txt")
            os.system("git add test2.txt")
            os.system("git commit -m 'Second commit'")

            worker = BackportWorker()
            commits = worker._get_commits_to_backport(repo_dir)

            assert len(commits) >= 1

    def test_cherry_pick_commit_dry_run(self):
        """Test cherry-pick in dry-run mode."""
        worker = BackportWorker(dry_run=True)
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
            os.system("git checkout -b release-1.0")

            result = worker._cherry_pick_commit(repo_dir, "HEAD", "release-1.0")
            assert result is True

    def test_process_backports_with_target_branches(self):
        """Test processing backports with target branches."""
        worker = BackportWorker(
            source_branch="main",
            target_branches=["release-1.0"],
            dry_run=True,
        )

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
            os.system("git checkout -b release-1.0")

            result = worker._process_backports(repo_dir)
            assert result["success"] is True

    def test_log_completion_summary(self):
        """Test completion summary logging."""
        worker = BackportWorker()
        results = {
            "commits_backported": 5,
            "commits_failed": 1,
        }
        worker._log_completion_summary(results)

    def test_run_with_valid_repo(self):
        """Test running worker with valid repository."""
        worker = BackportWorker(
            source_branch="main",
            target_branches=["release-1.0"],
            dry_run=True,
        )

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
            os.system("git checkout -b release-1.0")

            task_dir = Path(temp_dir) / "task"
            task_dir.mkdir()

            result = worker.run(repo_dir, task_dir)

            assert result["success"] is True
            assert result["worker_name"] == "BackportWorker"
            assert result["source_branch"] == "main"
            assert "execution_time" in result
