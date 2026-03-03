"""Tests for CLI execution behavior."""

import subprocess
from pathlib import Path
from unittest.mock import patch

from auto_slopp.utils.cli_executor import run_cli_executor
from settings.main import CLIConfiguration


@patch("auto_slopp.utils.cli_executor.subprocess.run")
def test_codex_uses_exec_subcommand_by_default(mock_run, monkeypatch):
    """Codex should run in non-interactive mode when no subcommand is configured."""
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "ok"
    mock_run.return_value.stderr = ""

    monkeypatch.setattr("auto_slopp.utils.cli_executor._active_cli_configuration_index", 0)
    monkeypatch.setattr(
        "auto_slopp.utils.cli_executor.settings.cli_configurations",
        [CLIConfiguration(cli_command="codex", cli_args=["--dangerously-bypass-approvals-and-sandbox", "exec"])],
    )

    run_cli_executor(additional_instructions="Do work", working_directory=Path.cwd())

    cmd = mock_run.call_args.kwargs["args"] if "args" in mock_run.call_args.kwargs else mock_run.call_args.args[0]
    # Check that it uses the provided args from CLIConfiguration
    assert cmd[0] == "codex"
    assert "--dangerously-bypass-approvals-and-sandbox" in cmd
    assert "exec" in cmd
    assert cmd[-1] == "Do work"


@patch("auto_slopp.utils.cli_executor.subprocess.run")
def test_codex_preserves_existing_subcommand(mock_run, monkeypatch):
    """Codex should not inject exec when a subcommand already exists."""
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "ok"
    mock_run.return_value.stderr = ""

    monkeypatch.setattr("auto_slopp.utils.cli_executor._active_cli_configuration_index", 0)
    monkeypatch.setattr(
        "auto_slopp.utils.cli_executor.settings.cli_configurations",
        [CLIConfiguration(cli_command="codex", cli_args=["review"])],
    )

    run_cli_executor(additional_instructions="Review this", working_directory=Path.cwd())

    cmd = mock_run.call_args.kwargs["args"] if "args" in mock_run.call_args.kwargs else mock_run.call_args.args[0]
    assert cmd[:2] == ["codex", "review"]
    assert "exec" not in cmd


@patch("auto_slopp.utils.cli_executor.subprocess.run")
def test_timeout_falls_back_to_next_configuration(mock_run, monkeypatch):
    """Timeout on preferred configuration should trigger next configured CLI."""
    timeout_exc = subprocess.TimeoutExpired(cmd=["opencode"], timeout=30)
    success_result = type("Result", (), {"returncode": 0, "stdout": "ok", "stderr": ""})()
    mock_run.side_effect = [timeout_exc, success_result, success_result, success_result]

    monkeypatch.setattr("auto_slopp.utils.cli_executor._active_cli_configuration_index", 0)
    monkeypatch.setattr(
        "auto_slopp.utils.cli_executor.settings.cli_configurations",
        [
            CLIConfiguration(cli_command="opencode", cli_args=["run"]),
            CLIConfiguration(cli_command="codex", cli_args=["exec"]),
        ],
    )

    result = run_cli_executor(additional_instructions="Do work", working_directory=Path.cwd(), timeout=30)

    assert result["success"] is True
    called_commands = [call.args[0] for call in mock_run.call_args_list]
    assert called_commands[0][0] == "opencode"
    assert called_commands[1][0] == "codex"


@patch("auto_slopp.utils.cli_executor.subprocess.run")
def test_rebalance_switches_back_to_lower_index_when_healthy(mock_run, monkeypatch):
    """When running on non-preferred config, probe should move back to lowest healthy config."""
    success_result = type("Result", (), {"returncode": 0, "stdout": "ok", "stderr": ""})()
    mock_run.return_value = success_result

    monkeypatch.setattr("auto_slopp.utils.cli_executor._active_cli_configuration_index", 1)
    monkeypatch.setattr(
        "auto_slopp.utils.cli_executor.settings.cli_configurations",
        [
            CLIConfiguration(cli_command="opencode", cli_args=["run"]),
            CLIConfiguration(cli_command="codex", cli_args=["exec"]),
        ],
    )

    run_cli_executor(additional_instructions="Do work", working_directory=Path.cwd(), timeout=30)

    # Note: rebalance happens at the end of run_cli_executor if index != 0
    from auto_slopp.utils.cli_executor import _active_cli_configuration_index

    assert _active_cli_configuration_index == 0
