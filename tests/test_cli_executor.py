"""Tests for CLI execution behavior."""

from pathlib import Path
from unittest.mock import patch

from auto_slopp.utils.cli_executor import run_cli_executor


@patch("auto_slopp.utils.cli_executor.subprocess.run")
def test_codex_uses_exec_subcommand_by_default(mock_run, monkeypatch):
    """Codex should run in non-interactive mode when no subcommand is configured."""
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "ok"
    mock_run.return_value.stderr = ""

    monkeypatch.setattr("auto_slopp.utils.cli_executor.settings.cli_command", "codex")
    monkeypatch.setattr(
        "auto_slopp.utils.cli_executor.settings.cli_args",
        ["--dangerously-bypass-approvals-and-sandbox"],
    )

    run_cli_executor(additional_instructions="Do work", working_directory=Path.cwd())

    cmd = mock_run.call_args.kwargs["args"] if "args" in mock_run.call_args.kwargs else mock_run.call_args.args[0]
    assert cmd[:3] == ["codex", "exec", "--dangerously-bypass-approvals-and-sandbox"]
    assert cmd[-1] == "Do work"


@patch("auto_slopp.utils.cli_executor.subprocess.run")
def test_codex_preserves_existing_subcommand(mock_run, monkeypatch):
    """Codex should not inject exec when a subcommand already exists."""
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "ok"
    mock_run.return_value.stderr = ""

    monkeypatch.setattr("auto_slopp.utils.cli_executor.settings.cli_command", "codex")
    monkeypatch.setattr("auto_slopp.utils.cli_executor.settings.cli_args", ["review"])

    run_cli_executor(additional_instructions="Review this", working_directory=Path.cwd())

    cmd = mock_run.call_args.kwargs["args"] if "args" in mock_run.call_args.kwargs else mock_run.call_args.args[0]
    assert cmd[:2] == ["codex", "review"]
    assert "exec" not in cmd[1:3]
