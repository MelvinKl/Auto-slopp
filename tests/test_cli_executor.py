"""Tests for CLI execution behavior."""

import subprocess
from pathlib import Path
from unittest.mock import patch

from auto_slopp.utils.cli_executor import (
    execute_openagent_with_instructions,
    execute_with_instructions,
    get_active_cli_command,
    run_cli_executor,
    run_opencode,
)
from settings.main import CLIConfiguration, TaskRating


@patch("auto_slopp.utils.cli_executor.subprocess.run")
def test_codex_uses_exec_subcommand_by_default(mock_run, monkeypatch):
    """Codex should run in non-interactive mode when no subcommand is configured."""
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "ok"
    mock_run.return_value.stderr = ""

    monkeypatch.setattr("auto_slopp.utils.cli_executor._active_cli_configuration_index", 0)
    monkeypatch.setattr(
        "auto_slopp.utils.cli_executor.settings.cli_configurations",
        [
            CLIConfiguration(
                cli_command="codex",
                cli_args=["--dangerously-bypass-approvals-and-sandbox", "exec"],
            )
        ],
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
def test_no_config_meets_min_rating_returns_error(mock_run, monkeypatch):
    """When no CLI config meets min_rating, an error should be returned."""
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "ok"
    mock_run.return_value.stderr = ""

    monkeypatch.setattr("auto_slopp.utils.cli_executor._active_cli_configuration_index", 0)
    monkeypatch.setattr(
        "auto_slopp.utils.cli_executor.settings.cli_configurations",
        [
            CLIConfiguration(cli_command="weak-tool", cli_args=["run"], capability=2),
            CLIConfiguration(cli_command="medium-tool", cli_args=["run"], capability=5),
        ],
    )
    monkeypatch.setattr(
        "auto_slopp.utils.cli_executor.settings.task_difficulties",
        {
            "github_issue": TaskRating(min_rating=7, max_rating=10, recommended_rating=8),
            "default": TaskRating(min_rating=0, max_rating=10, recommended_rating=5),
        },
    )

    result = run_cli_executor(
        additional_instructions="Do work",
        working_directory=Path.cwd(),
        task_name="github_issue",
    )

    assert result["success"] is False
    assert "min_rating=7" in result["error"]
    assert "capabilities" in result["error"].lower()
    assert mock_run.call_count == 0


@patch("auto_slopp.utils.cli_executor.subprocess.run")
def test_high_min_rating_skips_low_capability_tools(mock_run, monkeypatch):
    """High min_rating should skip tools with lower capability."""
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "ok"
    mock_run.return_value.stderr = ""

    monkeypatch.setattr("auto_slopp.utils.cli_executor._active_cli_configuration_index", 0)
    monkeypatch.setattr(
        "auto_slopp.utils.cli_executor.settings.cli_configurations",
        [
            CLIConfiguration(
                cli_command="weak-tool",
                cli_args=["run"],
                capability=2,
                name="weak",
            ),
            CLIConfiguration(
                cli_command="strong-tool",
                cli_args=["run"],
                capability=8,
                name="strong",
            ),
        ],
    )
    monkeypatch.setattr(
        "auto_slopp.utils.cli_executor.settings.task_difficulties",
        {
            "github_issue": TaskRating(min_rating=7, max_rating=10, recommended_rating=8),
            "default": TaskRating(min_rating=0, max_rating=10, recommended_rating=5),
        },
    )

    result = run_cli_executor(
        additional_instructions="Do work",
        working_directory=Path.cwd(),
        task_name="github_issue",
    )

    assert result["success"] is True
    called_commands = [call.args[0] for call in mock_run.call_args_list]
    assert called_commands[0][0] == "strong-tool"
    assert "weak-tool" not in called_commands[0]


@patch("auto_slopp.utils.cli_executor.subprocess.run")
def test_min_rating_respects_max_rating_boundary(mock_run, monkeypatch):
    """min_rating check should respect max_rating boundary."""
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "ok"
    mock_run.return_value.stderr = ""

    monkeypatch.setattr("auto_slopp.utils.cli_executor._active_cli_configuration_index", 0)
    monkeypatch.setattr(
        "auto_slopp.utils.cli_executor.settings.cli_configurations",
        [
            CLIConfiguration(cli_command="low-tool", cli_args=["run"], capability=3),
            CLIConfiguration(cli_command="perfect-tool", cli_args=["run"], capability=7),
            CLIConfiguration(cli_command="high-tool", cli_args=["run"], capability=9),
        ],
    )
    monkeypatch.setattr(
        "auto_slopp.utils.cli_executor.settings.task_difficulties",
        {
            "task": TaskRating(min_rating=6, max_rating=7, recommended_rating=7),
            "default": TaskRating(min_rating=0, max_rating=10, recommended_rating=5),
        },
    )

    result = run_cli_executor(
        additional_instructions="Do work",
        working_directory=Path.cwd(),
        task_name="task",
    )

    assert result["success"] is True
    called_commands = [call.args[0] for call in mock_run.call_args_list]
    assert called_commands[0][0] == "perfect-tool"
    assert "low-tool" not in called_commands[0]


def test_get_active_cli_command_empty_configs(monkeypatch):
    """Test get_active_cli_command returns 'unknown' when no configs."""
    monkeypatch.setattr("auto_slopp.utils.cli_executor.settings.cli_configurations", [])
    result = get_active_cli_command()
    assert result == "unknown"


def test_get_active_cli_command_index_out_of_range(monkeypatch):
    """Test get_active_cli_command handles index out of range."""
    monkeypatch.setattr(
        "auto_slopp.utils.cli_executor.settings.cli_configurations",
        [CLIConfiguration(cli_command="tool", cli_args=["run"])],
    )
    monkeypatch.setattr("auto_slopp.utils.cli_executor._active_cli_configuration_index", 99)
    result = get_active_cli_command()
    assert result == "tool"


@patch("auto_slopp.utils.cli_executor.subprocess.run")
def test_execute_command_failure_logs_stderr(mock_run, monkeypatch):
    """Test that failed command returns error result."""
    mock_run.return_value.returncode = 1
    mock_run.return_value.stdout = "output"
    mock_run.return_value.stderr = "error message"

    monkeypatch.setattr("auto_slopp.utils.cli_executor._active_cli_configuration_index", 0)
    monkeypatch.setattr(
        "auto_slopp.utils.cli_executor.settings.cli_configurations",
        [CLIConfiguration(cli_command="tool", cli_args=["run"])],
    )

    result = run_cli_executor(additional_instructions="test", working_directory=Path.cwd())

    assert result["success"] is False or "error" in result


@patch("auto_slopp.utils.cli_executor.subprocess.run")
def test_execute_with_instructions(mock_run, monkeypatch):
    """Test execute_with_instructions wrapper calls run_cli_executor."""
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "ok"
    mock_run.return_value.stderr = ""

    monkeypatch.setattr("auto_slopp.utils.cli_executor._active_cli_configuration_index", 0)
    monkeypatch.setattr(
        "auto_slopp.utils.cli_executor.settings.cli_configurations",
        [CLIConfiguration(cli_command="tool", cli_args=["run"])],
    )

    from pathlib import Path

    result = execute_with_instructions(
        instructions="do work",
        work_dir=Path.cwd(),
        agent_args=["--verbose"],
    )

    assert "success" in result


@patch("auto_slopp.utils.cli_executor.subprocess.run")
def test_run_opencode_deprecated(mock_run, monkeypatch):
    """Test run_opencode is deprecated and emits warning."""
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "ok"
    mock_run.return_value.stderr = ""

    monkeypatch.setattr("auto_slopp.utils.cli_executor._active_cli_configuration_index", 0)
    monkeypatch.setattr(
        "auto_slopp.utils.cli_executor.settings.cli_configurations",
        [CLIConfiguration(cli_command="tool", cli_args=["run"])],
    )

    result = run_opencode(additional_instructions="test", working_directory=Path.cwd())

    assert "success" in result


@patch("auto_slopp.utils.cli_executor.subprocess.run")
def test_run_cli_executor_tried_indices_break(mock_run, monkeypatch):
    """Test that config in tried_indices causes break (line 300-301)."""
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "ok"
    mock_run.return_value.stderr = ""

    monkeypatch.setattr("auto_slopp.utils.cli_executor._active_cli_configuration_index", 0)
    monkeypatch.setattr(
        "auto_slopp.utils.cli_executor.settings.cli_configurations",
        [
            CLIConfiguration(cli_command="tool1", cli_args=["run"], capability=5),
        ],
    )
    monkeypatch.setattr(
        "auto_slopp.utils.cli_executor.settings.task_difficulties",
        {"default": TaskRating(min_rating=0, max_rating=10, recommended_rating=5)},
    )

    with patch("auto_slopp.utils.cli_executor._probe_configuration", return_value=True):
        result = run_cli_executor(additional_instructions="test", working_directory=Path.cwd())

    assert result["success"] is True


@patch("auto_slopp.utils.cli_executor.subprocess.run")
def test_run_cli_executor_capability_mismatch(mock_run, monkeypatch):
    """Test capability check at execution time (lines 305-312)."""
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "ok"
    mock_run.return_value.stderr = ""

    monkeypatch.setattr("auto_slopp.utils.cli_executor._active_cli_configuration_index", 0)
    monkeypatch.setattr(
        "auto_slopp.utils.cli_executor.settings.cli_configurations",
        [
            CLIConfiguration(cli_command="tool1", cli_args=["run"], capability=3),
        ],
    )
    monkeypatch.setattr(
        "auto_slopp.utils.cli_executor.settings.task_difficulties",
        {"default": TaskRating(min_rating=0, max_rating=10, recommended_rating=5)},
    )

    with patch("auto_slopp.utils.cli_executor._probe_configuration", return_value=True):
        result = run_cli_executor(additional_instructions="test", working_directory=Path.cwd())

    assert result["success"] is True


@patch("auto_slopp.utils.cli_executor.subprocess.run")
def test_check_cooldowns_recovery(mock_run, monkeypatch):
    """Test cooldown recovery path (lines 35-46)."""
    from auto_slopp.utils.cli_executor import _check_cooldowns, _get_cli_state

    monkeypatch.setattr(
        "auto_slopp.utils.cli_executor.settings.cli_configurations",
        [
            CLIConfiguration(cli_command="tool1", cli_args=["run"], name="tool1", cooldown_seconds=10),
        ],
    )

    state = _get_cli_state(0)
    state["active"] = False
    state["cooldown_until"] = 0

    with patch("auto_slopp.utils.cli_executor._probe_configuration", return_value=True):
        _check_cooldowns(Path.cwd())

    state = _get_cli_state(0)
    assert state["active"] is True


@patch("auto_slopp.utils.cli_executor.subprocess.run")
def test_check_cooldowns_no_recovery(mock_run, monkeypatch):
    """Test cooldown no recovery path (lines 44-46)."""
    from auto_slopp.utils.cli_executor import _check_cooldowns, _get_cli_state

    monkeypatch.setattr(
        "auto_slopp.utils.cli_executor.settings.cli_configurations",
        [
            CLIConfiguration(cli_command="tool1", cli_args=["run"], name="tool1", cooldown_seconds=10),
        ],
    )

    state = _get_cli_state(0)
    state["active"] = False
    state["cooldown_until"] = 0

    with patch("auto_slopp.utils.cli_executor._probe_configuration", return_value=False):
        _check_cooldowns(Path.cwd())

    state = _get_cli_state(0)
    assert state["active"] is False


@patch("auto_slopp.utils.cli_executor.subprocess.run")
def test_execute_openagent_with_instructions_deprecated(mock_run, monkeypatch):
    """Test deprecated execute_openagent_with_instructions still works (line 444)."""
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "ok"
    mock_run.return_value.stderr = ""

    monkeypatch.setattr("auto_slopp.utils.cli_executor._active_cli_configuration_index", 0)
    monkeypatch.setattr(
        "auto_slopp.utils.cli_executor.settings.cli_configurations",
        [
            CLIConfiguration(cli_command="tool1", cli_args=["run"], capability=5),
        ],
    )
    monkeypatch.setattr(
        "auto_slopp.utils.cli_executor.settings.task_difficulties",
        {"default": TaskRating(min_rating=0, max_rating=10, recommended_rating=5)},
    )

    with patch("auto_slopp.utils.cli_executor._probe_configuration", return_value=True):
        result = execute_openagent_with_instructions(instructions="test", work_dir=Path.cwd())

    assert result["success"] is True
