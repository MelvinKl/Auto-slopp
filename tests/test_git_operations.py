"""Tests for git operations utilities."""

import subprocess
from pathlib import Path
from unittest.mock import Mock, patch

from auto_slopp.utils.git_operations import (
    checkout_branch_resilient,
    create_and_checkout_branch,
    get_current_branch,
    merge_main_into_branch,
)


class TestMergeMainIntoBranch:
    """Test cases for merge_main_into_branch function."""

    @patch("auto_slopp.utils.git_operations.get_current_branch")
    @patch("auto_slopp.utils.git_operations._run_git_command")
    def test_merge_main_on_main_branch(self, mock_run_git, mock_get_branch):
        """Test merge main while on main branch."""
        repo_dir = Path("/tmp/test_repo")
        mock_get_branch.return_value = "main"

        # Mock successful fetch and merge
        mock_run_git.side_effect = [
            Mock(returncode=0, stderr=""),  # git fetch origin main
            Mock(returncode=0, stderr=""),  # git merge FETCH_HEAD
        ]

        success, message = merge_main_into_branch(repo_dir, "main")

        assert success is True
        assert message == "Merge successful"
        # Check fetch command was called without :main
        mock_run_git.assert_any_call(repo_dir, "fetch", "origin", "main", check=False, timeout=60)

    @patch("auto_slopp.utils.git_operations.get_current_branch")
    @patch("auto_slopp.utils.git_operations._run_git_command")
    def test_merge_main_on_feature_branch(self, mock_run_git, mock_get_branch):
        """Test merge main while on feature branch."""
        repo_dir = Path("/tmp/test_repo")
        mock_get_branch.return_value = "feature/test"

        # Mock successful fetch and merge
        mock_run_git.side_effect = [
            Mock(returncode=0, stderr=""),  # git fetch origin main:main
            Mock(returncode=0, stderr=""),  # git merge FETCH_HEAD
        ]

        success, message = merge_main_into_branch(repo_dir, "feature/test")

        assert success is True
        assert message == "Merge successful"
        # Check fetch command was called with :main
        mock_run_git.assert_any_call(repo_dir, "fetch", "origin", "main:main", check=False, timeout=60)

    @patch("auto_slopp.utils.git_operations.get_current_branch")
    @patch("auto_slopp.utils.git_operations._run_git_command")
    def test_merge_main_fetch_fails_fallback(self, mock_run_git, mock_get_branch):
        """Test fallback when main:main fetch fails."""
        repo_dir = Path("/tmp/test_repo")
        mock_get_branch.return_value = "feature/test"

        # Mock git commands: first fetch fails, second succeeds, merge succeeds
        mock_run_git.side_effect = [
            Mock(returncode=1, stderr="refusing to fetch into current branch"),  # git fetch origin main:main (fails)
            Mock(returncode=0, stderr=""),  # git fetch origin main (succeeds)
            Mock(returncode=0, stderr=""),  # git merge FETCH_HEAD
        ]

        success, message = merge_main_into_branch(repo_dir, "feature/test")

        assert success is True
        assert message == "Merge successful"
        assert mock_run_git.call_count == 3


class TestCheckoutBranchResilient:
    """Test cases for checkout_branch_resilient function."""

    @patch("auto_slopp.utils.git_operations.subprocess.run")
    def test_checkout_success_first_attempt(self, mock_subprocess_run):
        """Test successful checkout on first attempt."""
        repo_dir = Path("/tmp/test_repo")
        branch = "feature/test"

        # Mock successful git commands
        mock_subprocess_run.side_effect = [
            Mock(returncode=0, stderr=""),  # git fetch
            Mock(returncode=0, stderr=""),  # git checkout
            Mock(returncode=0, stderr=""),  # git pull
        ]

        result = checkout_branch_resilient(repo_dir, branch)

        assert result is True
        assert mock_subprocess_run.call_count == 3


class TestCreateAndCheckoutBranch:
    """Test cases for create_and_checkout_branch function."""

    def _create_test_repo(self, repo_path: Path) -> None:
        """Create a test git repository with main branch."""
        subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )

        test_file = repo_path / "README.md"
        test_file.write_text("# Test Repository")

        subprocess.run(["git", "add", "."], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )

        subprocess.run(
            ["git", "branch", "-M", "main"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )

    def test_create_new_branch_from_main(self):
        """Test creating a new branch from main."""
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            self._create_test_repo(repo_path)

            result = create_and_checkout_branch(repo_path, "test-branch", base_branch="main")

            assert result is True
            current_branch = get_current_branch(repo_path)
            assert current_branch == "test-branch"

    def test_checkout_existing_branch(self):
        """Test checking out an existing branch."""
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            self._create_test_repo(repo_path)

            branch_name = "existing-branch"
            create_and_checkout_branch(repo_path, branch_name, base_branch="main")

            create_and_checkout_branch(repo_path, "main", base_branch="main")

            current_branch = get_current_branch(repo_path)
            assert current_branch == "main"

            result = create_and_checkout_branch(repo_path, branch_name, base_branch="main")

            assert result is True
            current_branch = get_current_branch(repo_path)
            assert current_branch == branch_name

    def test_create_branch_with_special_characters(self):
        """Test creating a branch with special characters."""
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            self._create_test_repo(repo_path)

            branch_name = "ai/task-123-test-task-with-special-chars"
            result = create_and_checkout_branch(repo_path, branch_name, base_branch="main")

            assert result is True
            current_branch = get_current_branch(repo_path)
            assert current_branch == branch_name

    @patch("auto_slopp.utils.git_operations.checkout_branch_resilient")
    @patch("auto_slopp.utils.git_operations._run_git_command")
    def test_create_branch_failure(self, mock_run_git, mock_checkout):
        """Test branch creation failure."""
        repo_dir = Path("/tmp/test_repo")

        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "branch already exists"
        mock_result.stdout = ""
        mock_run_git.return_value = mock_result

        result = create_and_checkout_branch(repo_dir, "test-branch", base_branch="main")

        assert result is False

    @patch("auto_slopp.utils.git_operations.subprocess.run")
    @patch("auto_slopp.utils.git_operations.run_cli_executor")
    def test_checkout_failure_after_reset(self, mock_run_cli_executor, mock_subprocess_run):
        """Test checkout failure even after reset."""
        repo_dir = Path("/tmp/test_repo")
        branch = "feature/test"

        # Mock run_cli_executor to avoid actual execution
        mock_run_cli_executor.return_value = {
            "success": False,
            "error": "CLI executor failed",
        }

        # Mock git commands: both checkout attempts fail
        mock_subprocess_run.side_effect = [
            Mock(returncode=0, stderr=""),  # git fetch
            Mock(returncode=1, stderr="checkout failed"),  # git checkout (fails)
            Mock(returncode=0, stderr=""),  # git reset --hard
            Mock(returncode=0, stderr=""),  # git clean
            Mock(returncode=1, stderr="checkout still failed"),  # git checkout (fails again)
        ]

        result = checkout_branch_resilient(repo_dir, branch)

        assert result is False
        assert mock_subprocess_run.call_count == 5

    @patch("auto_slopp.utils.git_operations.subprocess.run")
    @patch("auto_slopp.utils.git_operations.run_cli_executor")
    def test_checkout_reset_failure(self, mock_run_cli_executor, mock_subprocess_run):
        """Test checkout failure when reset itself fails."""
        repo_dir = Path("/tmp/test_repo")
        branch = "feature/test"

        # Mock run_cli_executor to avoid actual execution
        mock_run_cli_executor.return_value = {
            "success": False,
            "error": "CLI executor failed",
        }

        # Mock git commands: checkout fails, reset also fails
        mock_subprocess_run.side_effect = [
            Mock(returncode=0, stderr=""),  # git fetch
            Mock(returncode=1, stderr="checkout failed"),  # git checkout (fails)
            Mock(returncode=1, stderr="reset failed"),  # git reset --hard (fails)
        ]

        result = checkout_branch_resilient(repo_dir, branch)

        assert result is False
        assert mock_subprocess_run.call_count == 3

    @patch("auto_slopp.utils.git_operations.subprocess.run")
    def test_checkout_timeout(self, mock_subprocess_run):
        """Test checkout timeout handling."""
        repo_dir = Path("/tmp/test_repo")
        branch = "feature/test"

        # Mock timeout on fetch
        mock_subprocess_run.side_effect = TimeoutError("timeout")

        result = checkout_branch_resilient(repo_dir, branch)

        assert result is False

    @patch("auto_slopp.utils.git_operations.subprocess.run")
    def test_checkout_without_fetch(self, mock_subprocess_run):
        """Test checkout without fetching first."""
        repo_dir = Path("/tmp/test_repo")
        branch = "feature/test"

        # Mock successful git commands (no fetch)
        mock_subprocess_run.side_effect = [
            Mock(returncode=0, stderr=""),  # git checkout
            Mock(returncode=0, stderr=""),  # git pull
        ]

        result = checkout_branch_resilient(repo_dir, branch, fetch_first=False)

        assert result is True
        assert mock_subprocess_run.call_count == 2

    @patch("auto_slopp.utils.git_operations.subprocess.run")
    def test_checkout_with_pull_failure(self, mock_subprocess_run):
        """Test checkout success even when pull fails."""
        repo_dir = Path("/tmp/test_repo")
        branch = "feature/test"

        # Mock git commands: checkout succeeds but pull fails
        mock_subprocess_run.side_effect = [
            Mock(returncode=0, stderr=""),  # git fetch
            Mock(returncode=0, stderr=""),  # git checkout
            Mock(returncode=1, stderr="pull failed"),  # git pull (fails but shouldn't affect checkout)
        ]

        result = checkout_branch_resilient(repo_dir, branch)

        assert result is True
        assert mock_subprocess_run.call_count == 3

    @patch("auto_slopp.utils.git_operations.subprocess.run")
    def test_checkout_with_clean_failure(self, mock_subprocess_run):
        """Test checkout success even when git clean fails."""
        repo_dir = Path("/tmp/test_repo")
        branch = "feature/test"

        # Mock git commands: first checkout fails, reset works, clean fails, retry checkout succeeds
        mock_subprocess_run.side_effect = [
            Mock(returncode=0, stderr=""),  # git fetch
            Mock(returncode=1, stderr="checkout failed"),  # git checkout (fails)
            Mock(returncode=0, stderr=""),  # git reset --hard
            Mock(returncode=1, stderr="clean failed"),  # git clean (fails but shouldn't stop retry)
            Mock(returncode=0, stderr=""),  # git checkout (succeeds)
            Mock(returncode=0, stderr=""),  # git pull
        ]

        result = checkout_branch_resilient(repo_dir, branch)

        assert result is True
        assert mock_subprocess_run.call_count == 6
