"""CLI executor utilities for auto-slopp workers.

This module provides a centralized utility for executing configured CLI commands
(e.g., opencode, claude code) with consistent error handling, logging, and result formatting.
"""

import logging
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from settings.main import (
    _MAX_TIMEOUT_SECONDS,
    NO_TIMEOUT,
    CLIConfiguration,
    TaskRating,
    settings,
)

logger = logging.getLogger(__name__)
_active_cli_configuration_index = 0

_PROBE_INSTRUCTIONS = "are you working?"
# 600 seconds (10 minutes) balances catching hung tools without waiting too long.
# CLI tools like Claude Code or Codex can take minutes to cold-start, so we
# allow generous time while still detecting genuinely broken configurations.
_PROBE_TIMEOUT_SECONDS = 600

_cli_states: dict[int, dict[str, Any]] = {}


def _get_cli_state(index: int) -> dict[str, Any]:
    if index not in _cli_states:
        _cli_states[index] = {"active": True, "cooldown_until": 0.0}
    return _cli_states[index]


def _config_to_dict(config: CLIConfiguration) -> dict[str, Any]:
    """Convert a CLIConfiguration to a plain dict for probe/execution."""
    return {
        "cli_command": config.cli_command,
        "cli_args": list(config.cli_args),
        "name": config.name,
    }


def _check_startup_health(working_dir: Path) -> None:
    """Probe all CLI configurations at startup and place unhealthy ones in cooldown."""
    logger.info("Running startup health check for CLI configurations...")
    for index, config in enumerate(settings.cli_configurations):
        state = _get_cli_state(index)
        c_dict = _config_to_dict(config)
        try:
            if _probe_configuration(c_dict, working_dir, timeout=config.timeout):
                logger.info(f"CLI tool {config.name} is healthy.")
                state["active"] = True
            else:
                logger.warning(f"CLI tool {config.name} failed health check. Placing in cooldown.")
                state["active"] = False
                state["cooldown_until"] = time.time() + config.cooldown_seconds
        except (
            subprocess.TimeoutExpired,
            OSError,
        ) as e:
            logger.warning(f"CLI tool {config.name} probe raised {type(e).__name__}: {e}. Placing in cooldown.")
            state["active"] = False
            state["cooldown_until"] = time.time() + config.cooldown_seconds


def _check_cooldowns(working_dir: Path) -> None:
    now = time.time()
    for index, config in enumerate(settings.cli_configurations):
        state = _get_cli_state(index)
        if not state["active"] and now >= state["cooldown_until"]:
            logger.info(f"Checking if CLI tool {config.name} has recovered...")
            c_dict = _config_to_dict(config)
            try:
                if _probe_configuration(c_dict, working_dir, timeout=config.timeout):
                    logger.info(f"CLI tool {config.name} successfully recovered.")
                    state["active"] = True
                else:
                    logger.warning(f"CLI tool {config.name} still timing out. Resetting cooldown.")
                    state["cooldown_until"] = now + config.cooldown_seconds
            except (
                subprocess.TimeoutExpired,
                OSError,
            ) as e:
                logger.warning(f"CLI tool {config.name} probe raised {type(e).__name__}: {e}. Resetting cooldown.")
                state["cooldown_until"] = now + config.cooldown_seconds


def _choose_best_config_index(task_rating: TaskRating, working_dir: Path, task_name: str = "default") -> int:
    _check_cooldowns(working_dir)

    best_index = -1
    best_score = float("inf")

    for i, config in enumerate(settings.cli_configurations):
        state = _get_cli_state(i)
        if not state["active"]:
            continue

        if task_name in config.blacklist_tasks:
            continue

        capability = config.capability

        if capability < task_rating.min_rating:
            continue
        if capability > task_rating.max_rating:
            continue

        score = abs(capability - task_rating.recommended_rating)

        if score < best_score:
            best_score = score
            best_index = i

    return best_index


def _get_cli_configurations() -> list[dict[str, Any]]:
    """Return configured CLI configurations ordered by preference."""
    return [_config_to_dict(config) for config in settings.cli_configurations]


def get_active_cli_command() -> str:
    """Return the command name of the currently active CLI configuration."""
    configs = _get_cli_configurations()
    if not configs:
        return "unknown"

    index = _active_cli_configuration_index
    if index >= len(configs):
        index = 0

    return configs[index]["cli_command"]


def _build_command(
    cli_command: str,
    cli_base_args: list[str],
    agent_args: list[str],
    additional_instructions: Optional[str],
) -> list[str]:
    """Build command list from CLI configuration and invocation inputs."""
    cmd_args = list(cli_base_args) + list(agent_args)

    cmd = [cli_command] + cmd_args

    if additional_instructions:
        cmd.append(additional_instructions)

    return cmd


def _execute_command(
    cli_command: str,
    args: list[str],
    working_dir: Path,
    timeout: Optional[int],
    capture_output: bool,
    start_time: Optional[float] = None,
) -> dict[str, Any]:
    """Execute a fully built command and return standardized result data.

    Args:
        cli_command: Name of the CLI command being executed.
        args: Full command list to pass to subprocess.run.
        working_dir: Working directory for command execution.
        timeout: Timeout in seconds, or None for no timeout.
        capture_output: Whether to capture stdout/stderr.
        start_time: Optional start time for measuring execution duration.
    """
    command_start = start_time if start_time is not None else time.time()

    try:
        result = subprocess.run(
            args,
            cwd=working_dir,
            capture_output=capture_output,
            text=True,
            timeout=timeout,
        )

        execution_time = time.time() - command_start
        success = result.returncode == 0

        execution_result = {
            "success": success,
            "execution_time": execution_time,
            "timestamp": datetime.now().isoformat(),
            "working_directory": str(working_dir),
            "command": " ".join(args),
            "return_code": result.returncode,
            "timeout": False,
        }

        if capture_output:
            execution_result.update(
                {
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "stdout_lines": result.stdout.splitlines() if result.stdout else [],
                    "stderr_lines": result.stderr.splitlines() if result.stderr else [],
                }
            )

        if success:
            logger.info(f"{cli_command} completed successfully in {execution_time:.2f}s")
        else:
            logger.error(f"{cli_command} failed with return code {result.returncode} in {execution_time:.2f}s")
            if capture_output and result.stderr:
                logger.error(f"stderr: {result.stderr}")

        return execution_result

    except subprocess.TimeoutExpired:
        execution_time = time.time() - command_start
        error_msg = f"{cli_command} timed out after {timeout} seconds"
        logger.error(error_msg)

        return {
            "success": False,
            "execution_time": execution_time,
            "timestamp": datetime.now().isoformat(),
            "working_directory": str(working_dir),
            "command": " ".join(args),
            "return_code": -1,
            "timeout": True,
            "error": error_msg,
        }


def _resolve_timeout(raw_timeout: Optional[int], fallback: Optional[int] = None) -> Optional[int]:
    """Resolve a raw timeout value to an effective timeout.

    Handles the NO_TIMEOUT sentinel (-1), validates range (0 < timeout ≤ 30 days),
    and falls back to _PROBE_TIMEOUT_SECONDS when the value is invalid.

    Args:
        raw_timeout: The timeout value (None for unspecified, -1 for NO_TIMEOUT, or a positive integer).
        fallback: Default timeout in seconds to use when raw_timeout is None, non-positive,
                  or exceeds the maximum. Defaults to None; when None, falls back to
                  _PROBE_TIMEOUT_SECONDS (600s).

    Returns:
        None if raw_timeout is NO_TIMEOUT (-1), the raw_timeout value if positive and within range,
        or the fallback value (or _PROBE_TIMEOUT_SECONDS if fallback is None) otherwise.
    """
    if raw_timeout == NO_TIMEOUT:
        return None
    if raw_timeout is not None and 0 < raw_timeout <= _MAX_TIMEOUT_SECONDS:
        return raw_timeout
    return fallback if fallback is not None else _PROBE_TIMEOUT_SECONDS


def _probe_configuration(config: dict[str, Any], working_dir: Path, timeout: Optional[int] = None) -> bool:
    """Run quick health probe for one configuration.

    Uses the provided timeout:
      - :data:`NO_TIMEOUT` (-1) means no timeout (effective timeout is ``None``).
      - A positive integer uses that value as the timeout in seconds.
      - ``None`` or any other value falls back to :data:`_PROBE_TIMEOUT_SECONDS`
        (600 seconds / 10 minutes).

    Note:
        Internal callers (:func:`_check_startup_health` and
        :func:`_check_cooldowns`) always pass a validated config timeout
        (never ``None``). The fallback to ``_PROBE_TIMEOUT_SECONDS`` is
        intentionally exposed for external callers that invoke this function
        directly without providing a timeout, allowing them to probe
        configurations with a sensible default.
    """
    cmd = _build_command(
        cli_command=config["cli_command"],
        cli_base_args=config["cli_args"],
        agent_args=[],
        additional_instructions=_PROBE_INSTRUCTIONS,
    )

    effective_timeout = _resolve_timeout(timeout)

    result = _execute_command(
        cli_command=config["cli_command"],
        args=cmd,
        working_dir=working_dir,
        timeout=effective_timeout,
        capture_output=True,
    )
    return result["success"]


# noqa: C901 -- run_cli_executor: long orchestrator; splitting deferred (issue #419)
def run_cli_executor(  # noqa: C901 -- long orchestrator; splitting deferred (issue #419)
    additional_instructions: Optional[str] = None,
    working_directory: Optional[Path] = None,
    timeout: Optional[int] = None,
    agent_args: Optional[list[str]] = None,
    capture_output: bool = True,
    task_name: str = "default",
) -> dict[str, Any]:
    """Execute the configured CLI command with the specified parameters.

    This centralized utility handles CLI execution with consistent
    error handling, logging, and result formatting across all workers.

    Args:
        additional_instructions: Additional instructions to pass to the CLI
        working_directory: Directory where the CLI should be executed
        timeout: Command execution timeout in seconds (default: None = per-config timeout).
                 Use ``NO_TIMEOUT`` (-1) to disable timeout entirely.
        agent_args: Additional arguments to pass to the CLI
        capture_output: Whether to capture stdout/stderr (default: True)
        task_name: Name of the task type for difficulty matching (default: "default")

    Returns:
        Dictionary containing execution results with the following keys:
        - success: bool - Whether execution succeeded
        - execution_time: float - Time taken in seconds
        - timestamp: str - ISO format timestamp
        - working_directory: str - Directory where command was executed
        - command: str - Full command that was executed
        - return_code: int - Process return code
        - timeout: bool - Whether execution timed out
        - stdout: str (optional) - Captured stdout if capture_output=True
        - stderr: str (optional) - Captured stderr if capture_output=True
        - stdout_lines: list[str] (optional) - Stdout as lines if capture_output=True
        - stderr_lines: list[str] (optional) - Stderr as lines if capture_output=True
        - error: str (optional) - Error message if execution failed

    Examples:
        Basic usage:
        ```python
        result = run_cli_executor(
            additional_instructions="Fix the failing tests",
            working_directory=Path("/path/to/repo"),
            timeout=1800
        )
        ```

        With custom agent arguments:
        ```python
        result = run_cli_executor(
            additional_instructions="Implement new feature",
            working_directory=Path("/path/to/repo"),
            agent_args=["--verbose", "--debug"],
            timeout=3600
        )
        ```

        Without output capture (for interactive commands):
        ```python
        result = run_cli_executor(
            additional_instructions="Run interactive setup",
            working_directory=Path("/path/to/repo"),
            capture_output=False
        )
        ```
    """
    global _active_cli_configuration_index

    start_time = time.time()
    agent_args = agent_args or []
    working_dir = working_directory or Path.cwd()
    cli_configurations = _get_cli_configurations()

    resolved = _resolve_timeout(timeout)
    if resolved is None and timeout == NO_TIMEOUT:
        timeout_display = "disabled (NO_TIMEOUT)"
    elif resolved is None:
        timeout_display = "disabled (no timeout)"
    else:
        timeout_display = f"{resolved}s"

    logger.info(f"Executing with instructions: {additional_instructions if additional_instructions else 'None'}...")
    logger.info(f"Working directory: {working_dir}")
    logger.info(f"Timeout: {timeout_display}")
    logger.info(f"Agent args: {agent_args}")

    task_rating = settings.task_difficulties.get(task_name, settings.task_difficulties["default"])

    final_result: Optional[dict[str, Any]] = None
    tried_indices = set()

    while True:
        config_index = _choose_best_config_index(task_rating, working_dir, task_name)

        if config_index == -1:
            available_capabilities = [cfg.capability for cfg in settings.cli_configurations]
            logger.error(
                f"No CLI configuration meets min_rating={task_rating.min_rating} for task '{task_name}'. "
                f"Available configurations have capabilities: {available_capabilities}"
            )
            break

        state = _get_cli_state(config_index)

        if config_index in tried_indices or not state["active"]:
            break

        config = cli_configurations[config_index]
        selected_capability = settings.cli_configurations[config_index].capability
        if selected_capability < task_rating.min_rating:
            logger.error(
                f"Selected CLI configuration {config['name']} has capability={selected_capability}, "
                f"which is below min_rating={task_rating.min_rating} for task '{task_name}'. "
                f"This should not happen - selecting next configuration."
            )
            tried_indices.add(config_index)
            continue

        tried_indices.add(config_index)
        cli_command = config["cli_command"]
        cmd = _build_command(
            cli_command=cli_command,
            cli_base_args=config["cli_args"],
            agent_args=agent_args,
            additional_instructions=additional_instructions,
        )

        logger.info(f"Using CLI configuration: {config['name']} for task {task_name}")

        # Use per-config timeout: NO_TIMEOUT means never timeout, positive value overrides caller timeout
        _cfg = settings.cli_configurations[config_index]
        config_timeout = _resolve_timeout(_cfg.timeout)

        result = _execute_command(
            cli_command=cli_command,
            args=cmd,
            working_dir=working_dir,
            timeout=config_timeout,
            capture_output=capture_output,
            start_time=start_time,
        )
        final_result = result

        if not result.get("success", False):
            logger.warning(f"Error on configuration {config['name']}, placing in cooldown")
            state["active"] = False
            state["cooldown_until"] = time.time() + settings.cli_configurations[config_index].cooldown_seconds
            continue

        _active_cli_configuration_index = config_index
        break

    if final_result is None:
        available_capabilities = [cfg.capability for cfg in settings.cli_configurations]
        error_msg = (
            f"No CLI configuration meets min_rating={task_rating.min_rating} for task '{task_name}'. "
            f"Available configurations have capabilities: {available_capabilities}"
        )
        logger.error(error_msg)
        final_result = {
            "success": False,
            "execution_time": time.time() - start_time,
            "timestamp": datetime.now().isoformat(),
            "working_directory": str(working_dir),
            "command": "",
            "return_code": -1,
            "timeout": False,
            "error": error_msg,
        }

    return final_result


def execute_with_instructions(
    instructions: str,
    work_dir: Path,
    agent_args: Optional[list[str]] = None,
    timeout: Optional[int] = None,
    task_name: str = "default",
) -> dict[str, Any]:
    """Execute CLI with specific instructions.

    Args:
        instructions: The instructions to pass to the CLI
        work_dir: Working directory for command execution
        agent_args: Additional arguments to pass to the CLI
        timeout: Command execution timeout in seconds (default: None). Use ``NO_TIMEOUT`` (-1) to disable timeout.
        task_name: Name of the task type for difficulty matching

    Returns:
        Dictionary containing execution results.
    """
    return run_cli_executor(
        additional_instructions=instructions,
        working_directory=work_dir,
        agent_args=agent_args,
        timeout=timeout,
        task_name=task_name,
    )
