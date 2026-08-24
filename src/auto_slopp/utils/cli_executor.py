"""CLI executor utilities for auto-slopp workers.

This module provides a centralized utility for executing configured CLI commands
(e.g., opencode, claude code) with consistent error handling, logging, and result formatting.
"""

import logging
import subprocess
import time
from collections import OrderedDict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from settings.main import (
    MAX_TIMEOUT_SECONDS,
    NO_TIMEOUT,
    CLIConfiguration,
    TaskRating,
    settings,
)

logger = logging.getLogger(__name__)
_active_cli_configuration_index = 0

# Out-of-range timeout values already logged at warning level; subsequent
# resolutions of the same value log at debug only. OrderedDict is used so
# _warn_once_tracked can maintain deterministic LRU eviction order (a plain
# set's pop() would evict an arbitrary, unspecified element).
_warned_out_of_range_timeouts: "OrderedDict[Any, bool]" = OrderedDict()

# Log level for out-of-range timeout warnings. Configured via the
# Settings.cli_executor_timeout_warn_level field (environment variable
# AUTO_SLOPP_CLI_EXECUTOR_TIMEOUT_WARN_LEVEL).
# Defaults to WARNING; set to DEBUG to reduce log volume in production.
# Resolved on first use (and cached thereafter), so the setting may be
# changed after import but before the first call to _get_timeout_warn_level.
_TIMEOUT_WARN_LOG_LEVEL: Optional[int] = None


def _get_timeout_warn_level() -> int:
    """Resolve the out-of-range timeout warning log level (cached after first use)."""
    global _TIMEOUT_WARN_LOG_LEVEL
    # No lock around the lazy init: concurrent first-use callers may both
    # compute the level, but the write is idempotent so the race is benign.
    if _TIMEOUT_WARN_LOG_LEVEL is None:
        warn_level = settings.cli_executor_timeout_warn_level
        level = logging.WARNING
        if warn_level:
            # Validate against an explicit set of allowed level names rather
            # than getattr(logging, ...), which would also accept non-level
            # attributes such as NOTSET or module internals. FATAL is the
            # standard logging alias for CRITICAL and is accepted as such.
            if warn_level.upper() in _VALID_WARN_LEVELS:
                level = getattr(logging, warn_level.upper())
            else:
                logger.warning(
                    "Invalid cli_executor_timeout_warn_level value: %r. "
                    "Valid values: DEBUG, INFO, WARNING, ERROR, CRITICAL (FATAL accepted as an alias for CRITICAL). "
                    "Using WARNING.",
                    warn_level,
                )
        _TIMEOUT_WARN_LOG_LEVEL = level
    return _TIMEOUT_WARN_LOG_LEVEL


_PROBE_INSTRUCTIONS = "are you working?"
# 600 seconds (10 minutes) balances catching hung tools without waiting too long.
# CLI tools like Claude Code or Codex can take minutes to cold-start, so we
# allow generous time while still detecting genuinely broken configurations.
_PROBE_TIMEOUT_SECONDS = 600

_cli_states: Dict[int, Dict[str, Any]] = {}


def _get_cli_state(index: int) -> Dict[str, Any]:
    if index not in _cli_states:
        _cli_states[index] = {"active": True, "cooldown_until": 0.0}
    return _cli_states[index]


def _config_to_dict(config: CLIConfiguration) -> Dict[str, Any]:
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
            FileNotFoundError,
            PermissionError,
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
                FileNotFoundError,
                PermissionError,
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


def _get_cli_configurations() -> List[Dict[str, Any]]:
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
    cli_base_args: List[str],
    agent_args: List[str],
    additional_instructions: Optional[str],
) -> List[str]:
    """Build command list from CLI configuration and invocation inputs."""
    cmd_args = list(cli_base_args) + list(agent_args)

    cmd = [cli_command] + cmd_args

    if additional_instructions:
        cmd.append(additional_instructions)

    return cmd


def _execute_command(
    cli_command: str,
    args: List[str],
    working_dir: Path,
    timeout: Optional[int],
    capture_output: bool,
    start_time: Optional[float] = None,
) -> Dict[str, Any]:
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


# Allowed level names for the out-of-range timeout warning level
# (Settings.cli_executor_timeout_warn_level). FATAL is the standard
# logging alias for CRITICAL and is accepted as such.
_VALID_WARN_LEVELS: frozenset = frozenset({"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "FATAL"})

# Upper bound on distinct values remembered by _warn_once_tracked.
# When the bound is hit, the least-recently-seen value is evicted and, if it
# reappears, it warns once more (see README note on out-of-range warnings).
_MAX_TRACKED_WARN_VALUES = 1024


def _warn_once_tracked(
    tracked: "OrderedDict[Any, bool]",
    value: Any,
    level: int,
    fmt: str,
    *args: Any,
) -> None:
    """Log ``fmt % args`` at ``level`` once per distinct ``value``.

    ``tracked`` must be an :class:`collections.OrderedDict` used as an LRU
    cache: seeing a value moves it to the end, and when the bound
    :data:`_MAX_TRACKED_WARN_VALUES` is exceeded the least-recently-seen
    value is evicted first, so "warn once" semantics are deterministic even
    with a churning stream of misconfigured values.

    Values already present in ``tracked`` are logged at debug level with an
    "(already warned)" suffix; new values are added to ``tracked``.

    Unhashable values (e.g., a list or dict ``timeout`` from a hand-edited
    JSON config) are tracked by ``repr(value)`` so they are still warned
    about and discarded gracefully instead of raising ``TypeError``.
    """
    try:
        key: Any = value
        hash(key)
    except TypeError:
        # Unhashable values cannot serve as dict keys; fall back to their
        # repr (stable for equal values) so "warn once" still applies.
        key = repr(value)
    # No lock around the check-then-add: under concurrent first-use of the
    # same value, two callers may both miss it in ``tracked`` and both log
    # the warning (a harmless duplicate, unlike the idempotent lazy init in
    # _get_timeout_warn_level).
    if key in tracked:
        # LRU bookkeeping: refresh recency so this value survives eviction.
        tracked.move_to_end(key)
        logger.log(logging.DEBUG, fmt + " (already warned)", *args)
    else:
        tracked[key] = True
        # Keep the tracked cache bounded so frequently-varying misconfigured
        # values cannot grow it without limit for the process lifetime.
        # Evicted values simply warn again if they reappear.
        while len(tracked) > _MAX_TRACKED_WARN_VALUES:
            # Evict the least-recently-seen value (deterministic, unlike
            # set.pop() which removes an arbitrary element).
            tracked.popitem(last=False)
        logger.log(level, fmt, *args)


def _resolve_timeout(raw_timeout: Optional[Any]) -> Optional[int]:
    """Resolve a raw timeout value to an effective timeout.

    Handles the NO_TIMEOUT sentinel (-1), treats non-integer or out-of-range
    values as invalid (valid range: 0 < timeout ≤ MAX_TIMEOUT_SECONDS, ~1 year),
    and resolves None (unspecified) or invalid values to _PROBE_TIMEOUT_SECONDS.

    Note:
        The parameter is intentionally typed ``Optional[Any]`` rather than
        ``Optional[int]``: callers (or a hand-edited JSON config) may pass
        non-integer values such as ``str``, ``float``, ``bool``, ``list``, or
        ``dict``; those are deliberately accepted here, diagnosed with a
        warning, and resolved to :data:`_PROBE_TIMEOUT_SECONDS`.

    Args:
        raw_timeout: The timeout value (None for unspecified, -1 for NO_TIMEOUT, a positive integer,
        or any other value that will be diagnosed and discarded).

    Returns:
        None if raw_timeout is NO_TIMEOUT (-1), the raw_timeout value if positive and within range,
        or _PROBE_TIMEOUT_SECONDS otherwise.
    """
    # bool is a subclass of int, but True/False are not valid timeouts; treat
    # them as non-integer (without this, True would silently pass as 1 second).
    is_int = isinstance(raw_timeout, int) and not isinstance(raw_timeout, bool)
    if raw_timeout == NO_TIMEOUT and is_int:
        return None
    if is_int and 0 < raw_timeout <= MAX_TIMEOUT_SECONDS:
        return raw_timeout
    if raw_timeout is not None:
        # raw_timeout was present but invalid (non-integer or out of range);
        # log the discarded value so configuration mistakes are diagnosable.
        # Distinguish non-integer, non-positive, and above-maximum values to make
        # misconfiguration diagnosis faster (mirrors the Pydantic validator).
        if not is_int:
            problem = f"non-integer value ({raw_timeout!r})"
        elif raw_timeout <= 0:
            problem = f"non-positive value ({raw_timeout})"
        else:
            problem = f"value above the maximum ({MAX_TIMEOUT_SECONDS} seconds)"
        # Warn once per distinct value; repeated resolutions of the same
        # misconfigured value (e.g., probe/failover loops) log at debug only.
        _warn_once_tracked(
            _warned_out_of_range_timeouts,
            raw_timeout,
            _get_timeout_warn_level(),
            "Discarding out-of-range timeout %r (%s; valid range: 0 < timeout <= %d seconds); " "using %r instead",
            raw_timeout,
            problem,
            MAX_TIMEOUT_SECONDS,
            _PROBE_TIMEOUT_SECONDS,
        )
    return _PROBE_TIMEOUT_SECONDS


def _probe_configuration(config: Dict[str, Any], working_dir: Path, timeout: Optional[int] = None) -> bool:
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


def run_cli_executor(
    additional_instructions: Optional[str] = None,
    working_directory: Optional[Path] = None,
    timeout: Optional[int] = None,
    agent_args: Optional[List[str]] = None,
    capture_output: bool = True,
    task_name: str = "default",
) -> Dict[str, Any]:
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
        - stdout_lines: List[str] (optional) - Stdout as lines if capture_output=True
        - stderr_lines: List[str] (optional) - Stderr as lines if capture_output=True
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

    final_result: Optional[Dict[str, Any]] = None
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
    agent_args: Optional[List[str]] = None,
    timeout: Optional[int] = None,
    task_name: str = "default",
) -> Dict[str, Any]:
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
