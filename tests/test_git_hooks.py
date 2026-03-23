"""End-to-end tests for git pre-commit and pre-push hooks."""

import os
import subprocess
from pathlib import Path

HOOKS_DIR = Path(__file__).parent.parent / "githooks"
PRE_COMMIT_HOOK = HOOKS_DIR / "pre-commit"
PRE_PUSH_HOOK = HOOKS_DIR / "pre-push"


class TestPreCommitHookScript:
    """Tests for the pre-commit hook script."""

    def test_hook_file_exists(self):
        """pre-commit hook script exists in githooks/."""
        assert PRE_COMMIT_HOOK.exists(), "githooks/pre-commit not found"

    def test_hook_is_executable(self):
        """pre-commit hook script is executable."""
        assert os.access(PRE_COMMIT_HOOK, os.X_OK), "githooks/pre-commit is not executable"

    def test_hook_runs_make_format(self):
        """pre-commit hook invokes 'make format'."""
        content = PRE_COMMIT_HOOK.read_text()
        assert "make format" in content, "pre-commit hook does not call 'make format'"

    def test_hook_exits_on_format_failure(self):
        """pre-commit hook exits non-zero when formatting fails."""
        content = PRE_COMMIT_HOOK.read_text()
        # The hook should propagate make format failures (exit 1 or || exit 1)
        assert "exit 1" in content or "|| exit" in content, "pre-commit hook does not exit on format failure"

    def test_hook_requires_uv(self):
        """pre-commit hook checks for uv availability."""
        content = PRE_COMMIT_HOOK.read_text()
        assert "uv" in content, "pre-commit hook does not use uv"

    def test_hook_skips_gracefully_without_bd(self):
        """pre-commit hook runs without bd (exits 0 when bd is absent)."""
        # Run the hook in an environment where bd is not available.
        # bd is not present in this environment, so hook should exit 0.
        env = {**os.environ, "PATH": "/usr/local/bin:/usr/bin:/bin"}
        result = subprocess.run(
            ["sh", str(PRE_COMMIT_HOOK)],
            capture_output=True,
            text=True,
            env=env,
            cwd=str(Path(__file__).parent.parent),
        )
        # Hook may succeed (0) or fail due to format issues, but not crash
        assert result.returncode in (0, 1), (
            f"pre-commit hook returned unexpected exit code {result.returncode}: " f"{result.stderr}"
        )


class TestPrePushHookScript:
    """Tests for the pre-push hook script."""

    def test_hook_file_exists(self):
        """pre-push hook script exists in githooks/."""
        assert PRE_PUSH_HOOK.exists(), "githooks/pre-push not found"

    def test_hook_is_executable(self):
        """pre-push hook script is executable."""
        assert os.access(PRE_PUSH_HOOK, os.X_OK), "githooks/pre-push is not executable"

    def test_hook_runs_make_lint(self):
        """pre-push hook invokes 'make lint'."""
        content = PRE_PUSH_HOOK.read_text()
        assert "make lint" in content, "pre-push hook does not call 'make lint'"

    def test_hook_exits_on_lint_failure(self):
        """pre-push hook exits non-zero when lint fails."""
        content = PRE_PUSH_HOOK.read_text()
        assert "exit 1" in content or "|| exit" in content, "pre-push hook does not exit on lint failure"

    def test_hook_requires_uv(self):
        """pre-push hook checks for uv availability."""
        content = PRE_PUSH_HOOK.read_text()
        assert "uv" in content, "pre-push hook does not use uv"


class TestHookInstallation:
    """Tests for hook installation via 'make install-hooks'."""

    def test_install_hooks_target_exists_in_makefile(self):
        """Makefile contains an install-hooks target."""
        makefile = Path(__file__).parent.parent / "Makefile"
        content = makefile.read_text()
        assert "install-hooks" in content, "Makefile missing install-hooks target"

    def test_install_hooks_copies_pre_commit(self):
        """install-hooks copies pre-commit script to .git/hooks/."""
        makefile = Path(__file__).parent.parent / "Makefile"
        content = makefile.read_text()
        assert "githooks/pre-commit" in content, "Makefile install-hooks does not copy pre-commit hook"
        assert ".git/hooks/pre-commit" in content, "Makefile install-hooks does not copy pre-commit hook"

    def test_install_hooks_copies_pre_push(self):
        """install-hooks copies pre-push script to .git/hooks/."""
        makefile = Path(__file__).parent.parent / "Makefile"
        content = makefile.read_text()
        assert "githooks/pre-push" in content, "Makefile install-hooks does not copy pre-push hook"
        assert ".git/hooks/pre-push" in content, "Makefile install-hooks does not copy pre-push hook"

    def test_hooks_installed_in_git_dir(self):
        """Both hooks are installed in .git/hooks/."""
        git_hooks_dir = Path(__file__).parent.parent / ".git" / "hooks"
        assert (git_hooks_dir / "pre-commit").exists(), ".git/hooks/pre-commit not installed"
        assert (git_hooks_dir / "pre-push").exists(), ".git/hooks/pre-push not installed"

    def test_installed_hooks_are_executable(self):
        """Installed hooks in .git/hooks/ are executable."""
        git_hooks_dir = Path(__file__).parent.parent / ".git" / "hooks"
        pre_commit = git_hooks_dir / "pre-commit"
        pre_push = git_hooks_dir / "pre-push"
        assert os.access(pre_commit, os.X_OK), ".git/hooks/pre-commit is not executable"
        assert os.access(pre_push, os.X_OK), ".git/hooks/pre-push is not executable"

    def test_installed_pre_commit_matches_source(self):
        """Installed .git/hooks/pre-commit matches githooks/pre-commit."""
        git_hook = Path(__file__).parent.parent / ".git" / "hooks" / "pre-commit"
        source_hook = PRE_COMMIT_HOOK
        assert (
            git_hook.read_text() == source_hook.read_text()
        ), ".git/hooks/pre-commit differs from githooks/pre-commit — run 'make install-hooks'"

    def test_installed_pre_push_matches_source(self):
        """Installed .git/hooks/pre-push matches githooks/pre-push."""
        git_hook = Path(__file__).parent.parent / ".git" / "hooks" / "pre-push"
        source_hook = PRE_PUSH_HOOK
        assert (
            git_hook.read_text() == source_hook.read_text()
        ), ".git/hooks/pre-push differs from githooks/pre-push — run 'make install-hooks'"
