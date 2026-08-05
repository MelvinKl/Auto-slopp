"""Tests for CLI execution behavior."""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

from auto_slopp.utils.cli_executor import (
    _check_startup_health,
    _config_to_dict,
    run_cli_executor,
)
from settings.main import NO_TIMEOUT, CLIConfiguration, TaskRating


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
    success_result = MagicMock()
    success_result.returncode = 0
    success_result.stdout = "ok"
    success_result.stderr = ""
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


@patch("auto_slopp.utils.cli_executor.subprocess.run")
def test_blacklist_tasks_skips_configuration(mock_run, monkeypatch):
    """Configuration should be skipped when task_name is in blacklist_tasks."""
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "ok"
    mock_run.return_value.stderr = ""

    monkeypatch.setattr("auto_slopp.utils.cli_executor._active_cli_configuration_index", 0)
    monkeypatch.setattr(
        "auto_slopp.utils.cli_executor.settings.cli_configurations",
        [
            CLIConfiguration(
                cli_command="blacklisted-tool",
                cli_args=["run"],
                capability=8,
                blacklist_tasks=["github_issue"],
            ),
            CLIConfiguration(cli_command="fallback-tool", cli_args=["run"], capability=5),
        ],
    )
    monkeypatch.setattr(
        "auto_slopp.utils.cli_executor.settings.task_difficulties",
        {
            "github_issue": TaskRating(min_rating=5, max_rating=10, recommended_rating=7),
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
    assert called_commands[0][0] == "fallback-tool"
    assert "blacklisted-tool" not in called_commands[0]


@patch("auto_slopp.utils.cli_executor.subprocess.run")
def test_blacklist_tasks_does_not_affect_other_tasks(mock_run, monkeypatch):
    """Blacklist should only affect the specific task_name, not others."""
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "ok"
    mock_run.return_value.stderr = ""

    monkeypatch.setattr("auto_slopp.utils.cli_executor._active_cli_configuration_index", 0)
    monkeypatch.setattr("auto_slopp.utils.cli_executor._cli_states", {})
    monkeypatch.setattr(
        "auto_slopp.utils.cli_executor.settings.cli_configurations",
        [
            CLIConfiguration(
                cli_command="preferred-tool",
                cli_args=["run"],
                capability=8,
                blacklist_tasks=["github_issue"],
            ),
            CLIConfiguration(cli_command="fallback-tool", cli_args=["run"], capability=5),
        ],
    )
    monkeypatch.setattr(
        "auto_slopp.utils.cli_executor.settings.task_difficulties",
        {
            "github_issue": TaskRating(min_rating=5, max_rating=10, recommended_rating=7),
            "other_task": TaskRating(min_rating=5, max_rating=10, recommended_rating=7),
            "default": TaskRating(min_rating=0, max_rating=10, recommended_rating=5),
        },
    )

    result = run_cli_executor(
        additional_instructions="Do work",
        working_directory=Path.cwd(),
        task_name="other_task",
    )

    assert result["success"] is True
    called_commands = [call.args[0] for call in mock_run.call_args_list]
    assert called_commands[0][0] == "preferred-tool"


@patch("auto_slopp.utils.cli_executor.subprocess.run")
def test_all_configs_blacklisted_returns_error(mock_run, monkeypatch):
    """When all configurations are blacklisted for a task, an error should be returned."""
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "ok"
    mock_run.return_value.stderr = ""

    monkeypatch.setattr("auto_slopp.utils.cli_executor._active_cli_configuration_index", 0)
    monkeypatch.setattr(
        "auto_slopp.utils.cli_executor.settings.cli_configurations",
        [
            CLIConfiguration(
                cli_command="tool-1",
                cli_args=["run"],
                capability=8,
                blacklist_tasks=["github_issue"],
            ),
            CLIConfiguration(
                cli_command="tool-2",
                cli_args=["run"],
                capability=5,
                blacklist_tasks=["github_issue"],
            ),
        ],
    )
    monkeypatch.setattr(
        "auto_slopp.utils.cli_executor.settings.task_difficulties",
        {
            "github_issue": TaskRating(min_rating=5, max_rating=10, recommended_rating=7),
            "default": TaskRating(min_rating=0, max_rating=10, recommended_rating=5),
        },
    )

    result = run_cli_executor(
        additional_instructions="Do work",
        working_directory=Path.cwd(),
        task_name="github_issue",
    )

    assert result["success"] is False
    assert "no cli configuration meets" in result["error"].lower()
    assert mock_run.call_count == 0


@patch("auto_slopp.utils.cli_executor.subprocess.run")
def test_startup_health_check_marks_healthy_configs_active(mock_run, monkeypatch):
    """Startup health check should mark healthy configurations as active."""
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "ok"
    mock_run.return_value.stderr = ""

    monkeypatch.setattr("auto_slopp.utils.cli_executor._cli_states", {})
    monkeypatch.setattr(
        "auto_slopp.utils.cli_executor.settings.cli_configurations",
        [
            CLIConfiguration(cli_command="tool-1", cli_args=["run"], name="tool-1"),
            CLIConfiguration(cli_command="tool-2", cli_args=["run"], name="tool-2"),
        ],
    )

    _check_startup_health(Path.cwd())

    assert mock_run.call_count == 2
    from auto_slopp.utils.cli_executor import _cli_states

    assert _cli_states[0]["active"] is True
    assert _cli_states[1]["active"] is True


@patch("auto_slopp.utils.cli_executor.subprocess.run")
def test_startup_health_check_marks_unhealthy_configs_in_cooldown(mock_run, monkeypatch):
    """Startup health check should place unhealthy configurations in cooldown."""
    fail_result = MagicMock()
    fail_result.returncode = 1
    fail_result.stdout = ""
    fail_result.stderr = "error"
    mock_run.return_value = fail_result

    monkeypatch.setattr("auto_slopp.utils.cli_executor._cli_states", {})
    monkeypatch.setattr(
        "auto_slopp.utils.cli_executor.settings.cli_configurations",
        [
            CLIConfiguration(cli_command="tool-1", cli_args=["run"], name="tool-1", cooldown_seconds=60),
            CLIConfiguration(cli_command="tool-2", cli_args=["run"], name="tool-2", cooldown_seconds=120),
        ],
    )

    fixed_time = 1000.0
    mock_time = Mock()
    mock_time.time.return_value = fixed_time
    monkeypatch.setattr("auto_slopp.utils.cli_executor.time", mock_time)

    _check_startup_health(Path.cwd())

    assert mock_run.call_count == 2
    from auto_slopp.utils.cli_executor import _cli_states

    assert _cli_states[0]["active"] is False
    assert _cli_states[1]["active"] is False
    # Verify cooldown durations match expected values (deterministic, no wall-clock dependency)
    assert abs(_cli_states[0]["cooldown_until"] - (fixed_time + 60)) < 0.01
    assert abs(_cli_states[1]["cooldown_until"] - (fixed_time + 120)) < 0.01


@patch("auto_slopp.utils.cli_executor.subprocess.run")
def test_startup_health_check_mixed_health(mock_run, monkeypatch):
    """Startup health check should handle mixed healthy/unhealthy configurations."""
    success_result = MagicMock()
    success_result.returncode = 0
    success_result.stdout = "ok"
    success_result.stderr = ""

    fail_result = MagicMock()
    fail_result.returncode = 1
    fail_result.stdout = ""
    fail_result.stderr = "error"
    mock_run.side_effect = [success_result, fail_result]

    monkeypatch.setattr("auto_slopp.utils.cli_executor._cli_states", {})
    monkeypatch.setattr(
        "auto_slopp.utils.cli_executor.settings.cli_configurations",
        [
            CLIConfiguration(cli_command="healthy-tool", cli_args=["run"], name="healthy"),
            CLIConfiguration(cli_command="unhealthy-tool", cli_args=["run"], name="unhealthy", cooldown_seconds=60),
        ],
    )

    _check_startup_health(Path.cwd())

    assert mock_run.call_count == 2
    from auto_slopp.utils.cli_executor import _cli_states

    assert _cli_states[0]["active"] is True
    assert _cli_states[1]["active"] is False
    assert _cli_states[1]["cooldown_until"] > 0


@patch("auto_slopp.utils.cli_executor.subprocess.run")
def test_startup_health_all_healthy(mock_run, monkeypatch):
    """All probes succeed — every configuration stays active."""
    success_result = MagicMock()
    success_result.returncode = 0
    success_result.stdout = "ok"
    success_result.stderr = ""
    mock_run.return_value = success_result

    monkeypatch.setattr("auto_slopp.utils.cli_executor._cli_states", {})
    monkeypatch.setattr(
        "auto_slopp.utils.cli_executor.settings.cli_configurations",
        [
            CLIConfiguration(cli_command="a", cli_args=[], name="a"),
            CLIConfiguration(cli_command="b", cli_args=[], name="b"),
            CLIConfiguration(cli_command="c", cli_args=[], name="c"),
        ],
    )

    _check_startup_health(Path.cwd())

    assert mock_run.call_count == 3
    from auto_slopp.utils.cli_executor import _cli_states

    assert all(_cli_states[i]["active"] for i in range(3))


@patch("auto_slopp.utils.cli_executor.subprocess.run")
def test_startup_health_exception_doesnt_crash(mock_run, monkeypatch):
    """An exception in one probe must not prevent checking the others."""
    mock_run.side_effect = [FileNotFoundError("missing binary"), MagicMock(returncode=0, stdout="ok", stderr="")]

    monkeypatch.setattr("auto_slopp.utils.cli_executor._cli_states", {})
    monkeypatch.setattr(
        "auto_slopp.utils.cli_executor.settings.cli_configurations",
        [
            CLIConfiguration(cli_command="broken", cli_args=[], name="broken", cooldown_seconds=30),
            CLIConfiguration(cli_command="ok", cli_args=[], name="ok"),
        ],
    )

    _check_startup_health(Path.cwd())  # should not raise

    from auto_slopp.utils.cli_executor import _cli_states

    assert _cli_states[0]["active"] is False
    assert _cli_states[1]["active"] is True


@patch("auto_slopp.utils.cli_executor.subprocess.run")
def test_startup_health_timeout_exception(mock_run, monkeypatch):
    """TimeoutExpired in one probe is handled gracefully."""
    mock_run.side_effect = [subprocess.TimeoutExpired(cmd=["slow"], timeout=600), MagicMock(returncode=0)]

    monkeypatch.setattr("auto_slopp.utils.cli_executor._cli_states", {})
    monkeypatch.setattr(
        "auto_slopp.utils.cli_executor.settings.cli_configurations",
        [
            CLIConfiguration(cli_command="slow", cli_args=[], name="slow", cooldown_seconds=90),
            CLIConfiguration(cli_command="fast", cli_args=[], name="fast"),
        ],
    )

    _check_startup_health(Path.cwd())

    from auto_slopp.utils.cli_executor import _cli_states

    assert _cli_states[0]["active"] is False
    assert _cli_states[0]["cooldown_until"] > 0
    assert _cli_states[1]["active"] is True


@patch("auto_slopp.utils.cli_executor.subprocess.run")
def test_startup_health_cooldown_seconds_applied(mock_run, monkeypatch):
    """Each config receives its own cooldown_seconds value."""
    fixed_time = 5000.0
    mock_time = Mock()
    mock_time.time.return_value = fixed_time

    fail_a = MagicMock()
    fail_a.returncode = 1
    fail_a.stdout = ""
    fail_a.stderr = "err"
    success_b = MagicMock()
    success_b.returncode = 0
    success_b.stdout = "ok"
    success_b.stderr = ""

    mock_run.side_effect = [fail_a, success_b]

    monkeypatch.setattr("auto_slopp.utils.cli_executor.time", mock_time)
    monkeypatch.setattr("auto_slopp.utils.cli_executor._cli_states", {})
    monkeypatch.setattr(
        "auto_slopp.utils.cli_executor.settings.cli_configurations",
        [
            CLIConfiguration(cli_command="a", cli_args=[], name="a", cooldown_seconds=10),
            CLIConfiguration(cli_command="b", cli_args=[], name="b", cooldown_seconds=200),
        ],
    )

    _check_startup_health(Path.cwd())

    from auto_slopp.utils.cli_executor import _cli_states

    assert abs(_cli_states[0]["cooldown_until"] - (fixed_time + 10)) < 0.01
    # config b is healthy so no cooldown set (cooldown_until stays 0)
    assert _cli_states[1]["cooldown_until"] == 0


def test_config_to_dict():
    """_config_to_dict returns the expected keys and values."""
    cfg = CLIConfiguration(cli_command="cc", cli_args=["--x", "--y"], name="my-cc")
    d = _config_to_dict(cfg)
    assert d == {
        "cli_command": "cc",
        "cli_args": ["--x", "--y"],
        "name": "my-cc",
    }


def test_config_to_dict_mutation_safe():
    """Returning a dict must not let callers mutate the original CLIConfiguration."""
    cfg = CLIConfiguration(cli_command="cc", cli_args=["--x"], name="n")
    d = _config_to_dict(cfg)
    d["cli_args"].append("--mutated")
    assert "--mutated" not in cfg.cli_args


@patch("auto_slopp.utils.cli_executor.subprocess.run")
def test_custom_timeout_from_config(mock_run, monkeypatch):
    """A positive timeout in the config should override the caller-provided timeout."""
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "ok"
    mock_run.return_value.stderr = ""

    monkeypatch.setattr("auto_slopp.utils.cli_executor._active_cli_configuration_index", 0)
    monkeypatch.setattr("auto_slopp.utils.cli_executor._cli_states", {})
    monkeypatch.setattr(
        "auto_slopp.utils.cli_executor.settings.cli_configurations",
        [CLIConfiguration(cli_command="tool", cli_args=[], timeout=42)],
    )

    result = run_cli_executor(
        additional_instructions="Do work",
        working_directory=Path.cwd(),
        timeout=7200,
    )

    assert result["success"] is True
    # Verify the timeout passed to subprocess.run is the config's value, not the caller's
    call_kwargs = mock_run.call_args.kwargs if "args" in mock_run.call_args.kwargs else mock_run.call_args[1]
    assert call_kwargs["timeout"] == 42


@patch("auto_slopp.utils.cli_executor.subprocess.run")
def test_timeout_negative_one_means_no_timeout(mock_run, monkeypatch):
    """NO_TIMEOUT in config should result in timeout=None passed to subprocess (never timeout)."""
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "ok"
    mock_run.return_value.stderr = ""

    monkeypatch.setattr("auto_slopp.utils.cli_executor._active_cli_configuration_index", 0)
    monkeypatch.setattr("auto_slopp.utils.cli_executor._cli_states", {})
    monkeypatch.setattr(
        "auto_slopp.utils.cli_executor.settings.cli_configurations",
        [CLIConfiguration(cli_command="tool", cli_args=[], timeout=NO_TIMEOUT)],
    )

    result = run_cli_executor(
        additional_instructions="Do work",
        working_directory=Path.cwd(),
        timeout=30,
    )

    assert result["success"] is True
    call_kwargs = mock_run.call_args.kwargs if "args" in mock_run.call_args.kwargs else mock_run.call_args[1]
    assert call_kwargs["timeout"] is None


@patch("auto_slopp.utils.cli_executor.subprocess.run")
def test_default_timeout_is_never_timeout(mock_run, monkeypatch):
    """When config timeout defaults to -1, subprocess receives None (never timeout)."""
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "ok"
    mock_run.return_value.stderr = ""

    monkeypatch.setattr("auto_slopp.utils.cli_executor._active_cli_configuration_index", 0)
    monkeypatch.setattr("auto_slopp.utils.cli_executor._cli_states", {})
    monkeypatch.setattr(
        "auto_slopp.utils.cli_executor.settings.cli_configurations",
        [CLIConfiguration(cli_command="tool", cli_args=[])],  # timeout defaults to -1
    )

    result = run_cli_executor(
        additional_instructions="Do work",
        working_directory=Path.cwd(),
        timeout=1800,
    )

    assert result["success"] is True
    call_kwargs = mock_run.call_args.kwargs if "args" in mock_run.call_args.kwargs else mock_run.call_args[1]
    assert call_kwargs["timeout"] is None


@patch("auto_slopp.utils.cli_executor.subprocess.run")
def test_config_timeout_overrides_fallback(mock_run, monkeypatch):
    """Config timeout should take priority over fallback timeout when both could apply."""
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "ok"
    mock_run.return_value.stderr = ""

    monkeypatch.setattr("auto_slopp.utils.cli_executor._active_cli_configuration_index", 0)
    monkeypatch.setattr("auto_slopp.utils.cli_executor._cli_states", {})
    monkeypatch.setattr(
        "auto_slopp.utils.cli_executor.settings.cli_configurations",
        [
            CLIConfiguration(cli_command="fast-tool", cli_args=[], timeout=60),
            CLIConfiguration(cli_command="slow-tool", cli_args=[], timeout=3600),
        ],
    )

    result = run_cli_executor(
        additional_instructions="Do work",
        working_directory=Path.cwd(),
        timeout=7200,
    )

    assert result["success"] is True
    # First config (fast-tool) should be used with its own timeout of 60
    call_kwargs = mock_run.call_args.kwargs if "args" in mock_run.call_args.kwargs else mock_run.call_args[1]
    assert call_kwargs["timeout"] == 60


@patch("auto_slopp.utils.cli_executor.subprocess.run")
def test_probe_uses_config_timeout_positive(mock_run, monkeypatch):
    """Probe should use the config's positive timeout value."""
    from auto_slopp.utils.cli_executor import _probe_configuration

    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "ok"
    mock_run.return_value.stderr = ""

    config = {"cli_command": "tool", "cli_args": []}
    _probe_configuration(config, Path.cwd(), timeout=30)

    call_kwargs = mock_run.call_args.kwargs if "args" in mock_run.call_args.kwargs else mock_run.call_args[1]
    assert call_kwargs["timeout"] == 30


@patch("auto_slopp.utils.cli_executor.subprocess.run")
def test_probe_uses_config_timeout_negative_one(mock_run, monkeypatch):
    """Probe with NO_TIMEOUT should pass None to subprocess (never timeout)."""
    from auto_slopp.utils.cli_executor import _probe_configuration

    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "ok"
    mock_run.return_value.stderr = ""

    config = {"cli_command": "tool", "cli_args": []}
    _probe_configuration(config, Path.cwd(), timeout=NO_TIMEOUT)

    call_kwargs = mock_run.call_args.kwargs if "args" in mock_run.call_args.kwargs else mock_run.call_args[1]
    assert call_kwargs["timeout"] is None


@patch("auto_slopp.utils.cli_executor.subprocess.run")
def test_probe_falls_back_to_default_timeout(mock_run, monkeypatch):
    """Probe with no timeout specified should fall back to _PROBE_TIMEOUT_SECONDS."""
    from auto_slopp.utils.cli_executor import (
        _PROBE_TIMEOUT_SECONDS,
        _probe_configuration,
    )

    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "ok"
    mock_run.return_value.stderr = ""

    config = {"cli_command": "tool", "cli_args": []}
    _probe_configuration(config, Path.cwd())

    call_kwargs = mock_run.call_args.kwargs if "args" in mock_run.call_args.kwargs else mock_run.call_args[1]
    assert call_kwargs["timeout"] == _PROBE_TIMEOUT_SECONDS


@patch("auto_slopp.utils.cli_executor.subprocess.run")
def test_startup_health_uses_config_timeout(mock_run, monkeypatch):
    """Startup health check should pass config timeout to probe."""
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "ok"
    mock_run.return_value.stderr = ""

    monkeypatch.setattr("auto_slopp.utils.cli_executor._cli_states", {})
    monkeypatch.setattr(
        "auto_slopp.utils.cli_executor.settings.cli_configurations",
        [
            CLIConfiguration(cli_command="tool-1", cli_args=[], name="tool-1", timeout=30),
            CLIConfiguration(cli_command="tool-2", cli_args=[], name="tool-2", timeout=NO_TIMEOUT),
        ],
    )

    _check_startup_health(Path.cwd())

    assert mock_run.call_count == 2
    # First call should use timeout=30
    timeout_0 = mock_run.call_args_list[0].kwargs.get("timeout")
    # Second call should use timeout=None (never timeout)
    timeout_1 = mock_run.call_args_list[1].kwargs.get("timeout")
    assert timeout_0 == 30
    assert timeout_1 is None
