"""Tests for the general timeout applied to CLI commands.

These tests verify that:
  - The configurable ``general_timeout`` setting has the default of 300 seconds.
  - The low-level CLI runners (git, gh, vikunja) apply ``settings.general_timeout``
    when no explicit timeout is passed, and still honour an explicit value.
  - Direct git invocations (is_git_repo, git log/gh issue) use the general timeout.
"""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

from settings.main import Settings


def test_general_timeout_default_is_300():
    """The general timeout defaults to 300 seconds (5 minutes)."""
    settings = Settings()
    assert settings.general_timeout == 300


def test_general_timeout_adjustable_via_env():
    """The general timeout is adjustable through the environment."""
    env_vars = {k: v for k, v in os.environ.items() if not k.startswith("AUTO_SLOPP_")}
    with patch.dict(os.environ, env_vars), patch.dict(os.environ, {"AUTO_SLOPP_GENERAL_TIMEOUT": "12"}):
        test_settings = Settings()
        assert test_settings.general_timeout == 12


def _capture_kwargs(patched_run):
    """Return the kwargs of the most recent subprocess.run call."""
    return patched_run.call_args.kwargs


@patch("auto_slopp.utils.git_operations.subprocess.run")
def test_run_git_command_uses_general_timeout(mock_subprocess_run):
    """_run_git_command should pass settings.general_timeout when no explicit timeout is given."""
    from auto_slopp.utils.git_operations import _run_git_command

    result = MagicMock()
    result.returncode = 0
    result.stdout = ""
    result.stderr = ""
    mock_subprocess_run.return_value = result

    with patch("auto_slopp.utils.git_operations.settings.general_timeout", 300):
        _run_git_command("/tmp/repo", "rev-parse", "--abbrev-ref", "HEAD")

    assert _capture_kwargs(mock_subprocess_run)["timeout"] == 300


@patch("auto_slopp.utils.git_operations.subprocess.run")
def test_run_git_command_honours_explicit_timeout(mock_subprocess_run):
    """An explicit timeout must still override the general timeout."""
    from auto_slopp.utils.git_operations import _run_git_command

    result = MagicMock()
    result.returncode = 0
    result.stdout = ""
    result.stderr = ""
    mock_subprocess_run.return_value = result

    with patch("auto_slopp.utils.git_operations.settings.general_timeout", 300):
        _run_git_command("/tmp/repo", "rev-parse", "--abbrev-ref", "HEAD", timeout=45)

    assert _capture_kwargs(mock_subprocess_run)["timeout"] == 45


@patch("auto_slopp.utils.github_operations.subprocess.run")
def test_run_gh_command_uses_general_timeout(mock_subprocess_run):
    """_run_gh_command should pass settings.general_timeout when no explicit timeout is given."""
    from auto_slopp.utils.github_operations import _run_gh_command

    result = MagicMock()
    result.returncode = 0
    result.stdout = ""
    result.stderr = ""
    mock_subprocess_run.return_value = result

    with patch("auto_slopp.utils.github_operations.settings.general_timeout", 300):
        _run_gh_command("/tmp/repo", "issue", "list")

    assert _capture_kwargs(mock_subprocess_run)["timeout"] == 300


@patch("auto_slopp.utils.vikunja_operations.subprocess.run")
def test_run_vikunja_command_uses_general_timeout(mock_subprocess_run):
    """_run_vikunja_command should pass settings.general_timeout when no explicit timeout is given."""
    from auto_slopp.utils.vikunja_operations import _run_vikunja_command

    result = MagicMock()
    result.returncode = 0
    result.stdout = ""
    result.stderr = ""
    mock_subprocess_run.return_value = result

    with patch("auto_slopp.utils.vikunja_operations.settings.general_timeout", 120):
        _run_vikunja_command("-list-tasks")

    assert _capture_kwargs(mock_subprocess_run)["timeout"] == 120


@patch("auto_slopp.utils.git_operations.subprocess.run")
def test_is_git_repo_uses_general_timeout(mock_subprocess_run):
    """is_git_repo should invoke git with the general timeout."""
    from auto_slopp.utils.git_operations import is_git_repo

    result = MagicMock()
    result.returncode = 0
    result.stdout = "true"
    mock_subprocess_run.return_value = result

    with patch("auto_slopp.utils.git_operations.settings.general_timeout", 300):
        is_git_repo(Path("/tmp/repo"))

    assert _capture_kwargs(mock_subprocess_run)["timeout"] == 300
