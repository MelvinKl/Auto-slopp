"""Tests for git operations utilities."""

import subprocess
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from auto_slopp.utils.git_operations import (
    checkout_branch_resilient,
    create_and_checkout_branch,
    ensure_ralph_in_gitignore,
    get_current_branch,
    merge_main_into_branch,
    restore_stashed_changes,
    stash_changes,
)


class TestEnsureRalphInGitignore:
    """Test cases for ensure_ralph_in_gitignore function."""

    def test_ensure_ralph_when_gitignore_exists_without_ralph(self):
        """Test adding .ralph to existing .gitignore without .ralph entry."""
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            gitignore_path = repo_path / ".gitignore"
            gitignore_path.write_text("*.pyc\n__pycache__/\n")

            result = ensure_ralph_in_gitignore(repo_path)

            assert result is True
            content = gitignore_path.read_text()
            assert ".ralph/" in content

    def test_ensure_ralph_when_gitignore_exists_with_ralph(self):
        """Test when .gitignore already contains .ralph entry."""
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            gitignore_path = repo_path / ".gitignore"
            gitignore_path.write_text("*.pyc\n__pycache__/\n.ralph/\n")

            result = ensure_ralph_in_gitignore(repo_path)

            assert result is True
            content = gitignore_path.read_text()
            # Should not duplicate the entry
            assert content.count(".ralph/") == 1

    def test_ensure_ralph_when_gitignore_exists_with_ralph_no_slash(self):
        """Test when .gitignore already contains .ralph entry without trailing slash."""
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            gitignore_path = repo_path / ".gitignore"
            gitignore_path.write_text("*.pyc\n__pycache__/\n.ralph\n")

            result = ensure_ralph_in_gitignore(repo_path)

            assert result is True
            content = gitignore_path.read_text()
            # Should not add duplicate
            assert content.count(".ralph") == 1

    def test_ensure_ralph_when_gitignore_has_ralph_with_whitespace(self):
        """Test when .gitignore contains .ralph entry with surrounding whitespace."""
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            gitignore_path = repo_path / ".gitignore"
            gitignore_path.write_text("*.pyc\n__pycache__/\n .ralph/\n")

            result = ensure_ralph_in_gitignore(repo_path)

            assert result is True
            content = gitignore_path.read_text()
            # Should not add duplicate even with leading whitespace
            assert content.count(".ralph/") == 1

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            gitignore_path = repo_path / ".gitignore"
            gitignore_path.write_text("*.pyc\n__pycache__/\n.ralph/ \n")

            result = ensure_ralph_in_gitignore(repo_path)

            assert result is True
            content = gitignore_path.read_text()
            # Should not add duplicate even with trailing whitespace
            assert content.count(".ralph/") == 1

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            gitignore_path = repo_path / ".gitignore"
            gitignore_path.write_text("*.pyc\n__pycache__/\n .ralph \n")

            result = ensure_ralph_in_gitignore(repo_path)

            assert result is True
            content = gitignore_path.read_text()
            # Should not add duplicate even with both leading and trailing whitespace
            assert content.count(".ralph") == 1

    def test_ensure_ralph_when_no_gitignore(self):
        """Test creating .gitignore with .ralph when it doesn't exist."""
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)

            result = ensure_ralph_in_gitignore(repo_path)

            assert result is True
            gitignore_path = repo_path / ".gitignore"
            assert gitignore_path.exists()
            content = gitignore_path.read_text()
            assert content == ".ralph/\n"

    def test_ensure_ralph_handles_errors(self):
        """Test that errors are handled gracefully."""
        import os
        import tempfile

        # Skip if running as root (root can write to read-only files)
        if os.getuid() == 0:
            import pytest

            pytest.skip("Skipping read-only test when running as root")

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            gitignore_path = repo_path / ".gitignore"
            gitignore_path.write_text("*.pyc\n")

            # Make .gitignore read-only to cause a write error
            gitignore_path.chmod(0o444)

            try:
                result = ensure_ralph_in_gitignore(repo_path)
                assert result is False
            finally:
                # Restore permissions for cleanup
                gitignore_path.chmod(0o644)


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


class TestStashChanges:
    """Test cases for stash_changes and restore_stashed_changes functions."""

    def _create_test_repo_with_changes(self, repo_path: Path) -> None:
        """Create a test git repo with an uncommitted change."""
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
        test_file.write_text("# Test")
        subprocess.run(["git", "add", "."], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )
        # Create an uncommitted change
        test_file.write_text("# Test\nmodified")

    def test_stash_changes_with_uncommitted_changes(self):
        """Test stashing when there are uncommitted changes."""
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            self._create_test_repo_with_changes(repo_path)

            result = stash_changes(repo_path)

            assert result is not None
            assert "stash@{0}" in result
            # After stash, working directory should be clean
            status = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=repo_path,
                capture_output=True,
                text=True,
            )
            assert status.stdout.strip() == ""

    def test_stash_changes_without_uncommitted_changes(self):
        """Test stashing when there are no uncommitted changes."""
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            self._create_test_repo_with_changes(repo_path)
            # Clean working directory
            subprocess.run(
                ["git", "checkout", "--", "."],
                cwd=repo_path,
                check=True,
                capture_output=True,
            )

            result = stash_changes(repo_path)

            assert result is None

    def test_restore_stashed_changes(self):
        """Test restoring stashed changes."""
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            self._create_test_repo_with_changes(repo_path)

            # Stash then restore
            stash_changes(repo_path)
            result = restore_stashed_changes(repo_path)

            assert result is True
            # After restore, changes should be back in working directory
            status = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=repo_path,
                capture_output=True,
                text=True,
            )
            assert "M README.md" in status.stdout


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
    def test_checkout_failure_after_stash(self, mock_run_cli_executor, mock_subprocess_run):
        """Test checkout failure even after stash."""
        repo_dir = Path("/tmp/test_repo")
        branch = "feature/test"

        # Mock run_cli_executor to avoid actual execution
        mock_run_cli_executor.return_value = {
            "success": False,
            "error": "CLI executor failed",
        }

        # Mock git commands: both checkout attempts fail
        # stash_changes now calls: rev-parse HEAD, stash push
        def make_mock(returncode=0, stderr="", stdout=""):
            m = Mock()
            m.returncode = returncode
            m.stderr = stderr
            m.stdout = stdout
            return m

        mock_subprocess_run.side_effect = [
            make_mock(returncode=0),  # git fetch
            make_mock(returncode=1, stderr="checkout failed"),  # git checkout (fails)
            make_mock(
                returncode=0, stdout="M file.py"
            ),  # git status --porcelain (has_changes in checkout_branch_resilient)
            make_mock(returncode=0, stdout="M file.py"),  # git status --porcelain (has_changes in stash_changes)
            make_mock(returncode=0, stdout="feature/test"),  # git rev-parse --abbrev-ref HEAD
            make_mock(returncode=0),  # git stash push
            make_mock(returncode=1, stderr="checkout still failed"),  # git checkout (fails again)
            make_mock(returncode=0),  # git stash apply (restore on failure)
            make_mock(returncode=0),  # git stash drop (restore on failure)
        ]

        result = checkout_branch_resilient(repo_dir, branch)

        assert result is False
        assert mock_subprocess_run.call_count == 9

    @patch("auto_slopp.utils.git_operations.subprocess.run")
    @patch("auto_slopp.utils.git_operations.run_cli_executor")
    def test_checkout_stash_failure(self, mock_run_cli_executor, mock_subprocess_run):
        """Test checkout failure when stash itself fails."""
        repo_dir = Path("/tmp/test_repo")
        branch = "feature/test"

        # Mock run_cli_executor to avoid actual execution
        mock_run_cli_executor.return_value = {
            "success": False,
            "error": "CLI executor failed",
        }

        # Mock git commands: checkout fails, stash also fails
        # stash_changes now calls: rev-parse HEAD, stash push (fails)
        def make_mock(returncode=0, stderr="", stdout=""):
            m = Mock()
            m.returncode = returncode
            m.stderr = stderr
            m.stdout = stdout
            return m

        mock_subprocess_run.side_effect = [
            make_mock(returncode=0),  # git fetch
            make_mock(returncode=1, stderr="checkout failed"),  # git checkout (fails)
            make_mock(
                returncode=0, stdout="M file.py"
            ),  # git status --porcelain (has_changes in checkout_branch_resilient)
            make_mock(returncode=0, stdout="M file.py"),  # git status --porcelain (has_changes in stash_changes)
            make_mock(returncode=0, stdout="feature/test"),  # git rev-parse --abbrev-ref HEAD
            make_mock(returncode=1, stderr="stash failed"),  # git stash push (fails)
        ]

        result = checkout_branch_resilient(repo_dir, branch)

        assert result is False
        assert mock_subprocess_run.call_count == 6

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
    def test_checkout_failure_no_uncommitted_changes(self, mock_subprocess_run):
        """Test checkout failure path when there are no uncommitted changes.

        When the first checkout fails but there are no uncommitted changes,
        stash_changes should return None immediately (no git stash push),
        and the retry checkout should proceed.
        """
        repo_dir = Path("/tmp/test_repo")
        branch = "feature/test"

        # Mock git commands: first checkout fails, no changes to stash, retry succeeds
        # stash_changes returns None early when no changes, so no additional git commands
        # restore_stashed_changes is also skipped since stashed=False
        mock_subprocess_run.side_effect = [
            Mock(returncode=0, stderr=""),  # git fetch
            Mock(returncode=1, stderr="checkout failed"),  # git checkout (fails)
            Mock(returncode=0, stderr="", stdout=""),  # git status --porcelain (no changes, has_changes returns False)
            Mock(returncode=0, stderr=""),  # git checkout (retry succeeds)
            Mock(returncode=0, stderr=""),  # git pull
        ]

        result = checkout_branch_resilient(repo_dir, branch)

        assert result is True
        # Verify git stash push was NOT called (no uncommitted changes)
        stash_push_calls = [
            call
            for call in mock_subprocess_run.call_args_list
            if call[0] and call[0][0] == ["git"] and "stash" in call[0] and "push" in call[0]
        ]
        assert len(stash_push_calls) == 0, "git stash push should not be called when there are no changes"
        assert mock_subprocess_run.call_count == 5

    @patch("auto_slopp.utils.git_operations.subprocess.run")
    def test_checkout_with_stash_pop_failure(self, mock_subprocess_run):
        """Test checkout success even when git stash pop fails."""
        repo_dir = Path("/tmp/test_repo")
        branch = "feature/test"

        # Mock git commands: first checkout fails, stash works, retry checkout succeeds, restore fails
        # stash_changes now calls: rev-parse HEAD, stash push
        def make_mock(returncode=0, stderr="", stdout=""):
            m = Mock()
            m.returncode = returncode
            m.stderr = stderr
            m.stdout = stdout
            return m

        mock_subprocess_run.side_effect = [
            make_mock(returncode=0),  # git fetch
            make_mock(returncode=1, stderr="checkout failed"),  # git checkout (fails)
            make_mock(
                returncode=0, stdout="M file.py"
            ),  # git status --porcelain (has_changes in checkout_branch_resilient)
            make_mock(returncode=0, stdout="M file.py"),  # git status --porcelain (has_changes in stash_changes)
            make_mock(returncode=0, stdout="feature/test"),  # git rev-parse --abbrev-ref HEAD
            make_mock(returncode=0),  # git stash push (succeeds)
            make_mock(returncode=0),  # git checkout (succeeds)
            make_mock(
                returncode=1, stderr="stash apply failed"
            ),  # git stash apply (fails but checkout still succeeded)
            make_mock(returncode=0),  # git pull
        ]

        result = checkout_branch_resilient(repo_dir, branch)

        assert result is True
        assert mock_subprocess_run.call_count == 9


class TestCheckoutBranchResilientIntegration:
    """Integration tests for checkout_branch_resilient with real git repos."""

    def _create_repo_with_branch(self, repo_path: Path) -> None:
        """Create a test repo with main branch and a feature branch."""
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

        # Create initial file on main (rename default branch)
        test_file = repo_path / "README.md"
        test_file.write_text("# Main Branch Content")
        subprocess.run(["git", "add", "."], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(["git", "branch", "-M", "main"], cwd=repo_path, check=True, capture_output=True)

        # Create feature branch with different content
        subprocess.run(["git", "checkout", "-b", "feature"], cwd=repo_path, check=True, capture_output=True)
        test_file.write_text("# Feature Branch Content")
        subprocess.run(["git", "add", "."], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Feature commit"], cwd=repo_path, check=True, capture_output=True)

        # Switch back to main
        subprocess.run(["git", "checkout", "main"], cwd=repo_path, check=True, capture_output=True)

    @pytest.mark.integration
    def test_checkout_stashes_and_restores_uncommitted_changes(self):
        """Integration test: checkout stashes uncommitted changes and restores them.

        Scenario:
        1. Create a repo with main and feature branches
        2. On main, create an extra file (only on main) and modify it without committing
        3. Attempt to checkout feature branch (should fail due to local changes)
        4. checkout_branch_resilient should stash, checkout, and restore changes
        5. Verify the local uncommitted changes are preserved
        """
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            self._create_repo_with_branch(repo_path)

            # Create an extra file on main only (won't conflict with feature branch)
            extra_file = repo_path / "local_notes.txt"
            extra_file.write_text("# Local Uncommitted Change")
            subprocess.run(["git", "add", "."], cwd=repo_path, check=True, capture_output=True)

            # Verify we have uncommitted changes
            status = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=repo_path,
                capture_output=True,
                text=True,
            )
            assert "local_notes.txt" in status.stdout, "Should have uncommitted changes"

            # Attempt checkout - should succeed via stash mechanism
            result = checkout_branch_resilient(repo_path, "feature", fetch_first=False)

            assert result is True, "checkout_branch_resilient should succeed"

            # Verify we're on the feature branch
            current_branch = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=repo_path,
                capture_output=True,
                text=True,
            )
            assert current_branch.stdout.strip() == "feature", "Should be on feature branch"

            # Verify the file still exists with our content (restored from stash)
            assert extra_file.exists(), "Stashed file should be restored after checkout"
            restored_content = extra_file.read_text()
            assert "Local Uncommitted Change" in restored_content, "The uncommitted change content should be preserved"

            # Verify the stash was cleaned up (no stash entries left)
            stash_list = subprocess.run(
                ["git", "stash", "list"],
                cwd=repo_path,
                capture_output=True,
                text=True,
            )
            assert stash_list.stdout.strip() == "", "Stash should be empty after pop"

    @pytest.mark.integration
    def test_checkout_no_changes_skips_stash(self):
        """Integration test: checkout succeeds without stash when no uncommitted changes.

        Scenario:
        1. Create a repo with main and feature branches
        2. On main, ensure working directory is clean
        3. Attempt to checkout feature branch
        4. Verify checkout succeeds without stashing
        """
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            self._create_repo_with_branch(repo_path)

            # Verify working directory is clean
            status = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=repo_path,
                capture_output=True,
                text=True,
            )
            assert status.stdout.strip() == "", "Working directory should be clean"

            # Attempt checkout
            result = checkout_branch_resilient(repo_path, "feature", fetch_first=False)

            assert result is True, "checkout_branch_resilient should succeed"

            # Verify we're on the feature branch
            current_branch = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=repo_path,
                capture_output=True,
                text=True,
            )
            assert current_branch.stdout.strip() == "feature", "Should be on feature branch"

            # Verify working directory is clean (no stash was created)
            status_after = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=repo_path,
                capture_output=True,
                text=True,
            )
            assert status_after.stdout.strip() == "", "Working directory should remain clean"

            # Verify no stash entries
            stash_list = subprocess.run(
                ["git", "stash", "list"],
                cwd=repo_path,
                capture_output=True,
                text=True,
            )
            assert stash_list.stdout.strip() == "", "No stash should be created when no changes exist"
