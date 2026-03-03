"""CLI executor utilities for auto-slopp workers.

This module provides a centralized utility for executing configured CLI commands
(e.g., opencode, claude code) with consistent error handling, logging, and result formatting.
"""

import logging
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from settings.main import settings

logger = logging.getLogger(__name__)
_active_cli_configuration_index = 0
_PROBE_INSTRUCTIONS = "are you working?"
_PROBE_TIMEOUT_SECONDS = 10


CODEX_SUBCOMMANDS = {
    "exec",
    "review",
    "login",
    "logout",
    "mcp",
    "mcp-server",
    "app-server",
    "completion",
    "sandbox",
    "debug",
    "apply",
    "resume",
    "fork",
    "cloud",
    "features",
    "help",
}


def _codex_has_subcommand(args: List[str]) -> bool:
    """Return True when codex arguments already include a subcommand."""
    for arg in args:
        if arg.startswith("-"):
            continue
        return arg in CODEX_SUBCOMMANDS
    return False


def _get_cli_configurations() -> List[Dict[str, Any]]:
    """Return configured CLI configurations ordered by preference."""
    configs = getattr(settings, "cli_configurations", None)
    if configs:
        return [
            {
                "cli_command": config.cli_command,
                "cli_args": list(config.cli_args),
            }
            for config in configs
        ]

    return [
        {
            "cli_command": settings.cli_command,
            "cli_args": list(settings.cli_args),
        }
    ]


def _build_command(
    cli_command: str,
    cli_base_args: List[str],
    agent_args: List[str],
    additional_instructions: Optional[str],
) -> List[str]:
    """Build command list from CLI configuration and invocation inputs."""
    cmd_args = list(cli_base_args) + list(agent_args)

    # Codex defaults to interactive mode unless a subcommand is supplied.
    # In automation this runs without a TTY, so route to non-interactive exec by default.
    if cli_command == "codex" and not _codex_has_subcommand(cmd_args):
        cmd_args = ["exec"] + cmd_args

    cmd = [cli_command] + cmd_args

    if additional_instructions:
        cmd.append(additional_instructions)

    return cmd


def _execute_command(
    cli_command: str,
    cmd: List[str],
    working_dir: Path,
    timeout: int,
    capture_output: bool,
    start_time: Optional[float] = None,
) -> Dict[str, Any]:
    """Execute a fully built command and return standardized result data."""
    command_start = start_time if start_time is not None else time.time()

    try:
        result = subprocess.run(
            cmd,
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
            "command": " ".join(cmd),
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
            "command": " ".join(cmd),
            "return_code": -1,
            "timeout": True,
            "error": error_msg,
        }


def _probe_configuration(config: Dict[str, Any], working_dir: Path) -> bool:
    """Run quick health probe for one configuration."""
    cmd = _build_command(
        cli_command=config["cli_command"],
        cli_base_args=config["cli_args"],
        agent_args=[],
        additional_instructions=_PROBE_INSTRUCTIONS,
    )
    result = _execute_command(
        cli_command=config["cli_command"],
        cmd=cmd,
        working_dir=working_dir,
        timeout=_PROBE_TIMEOUT_SECONDS,
        capture_output=True,
    )
    return result["success"]


def _rebalance_active_configuration(configs: List[Dict[str, Any]], working_dir: Path) -> None:
    """Probe all configurations concurrently and switch to the best available."""
    global _active_cli_configuration_index

    with ThreadPoolExecutor(max_workers=len(configs)) as executor:
        futures = [executor.submit(_probe_configuration, config, working_dir) for config in configs]
        probe_results = [future.result() for future in futures]

    for index, healthy in enumerate(probe_results):
        if healthy:
            if index != _active_cli_configuration_index:
                logger.info(
                    f"Switching active CLI configuration from index {_active_cli_configuration_index} to {index}"
                )
            _active_cli_configuration_index = index
            return


def rebalance_configurations(working_dir: Optional[Path] = None) -> None:
    """Public interface to trigger health-probe and rebalance active configuration.

    This should be called after worker execution to ensure the most preferred
    healthy configuration is selected for the next task.
    """
    cli_configurations = _get_cli_configurations()
    if _active_cli_configuration_index != 0 and len(cli_configurations) > 1:
        _rebalance_active_configuration(
            configs=cli_configurations,
            working_dir=working_dir or Path.cwd(),
        )


def run_cli_executor(
    additional_instructions: Optional[str] = None,
    working_directory: Optional[Path] = None,
    timeout: int = 7200,
    agent_args: Optional[List[str]] = None,
    capture_output: bool = True,
) -> Dict[str, Any]:
    """Execute the configured CLI command with the specified parameters.

    This centralized utility handles CLI execution with consistent
    error handling, logging, and result formatting across all workers.

    Args:
        additional_instructions: Additional instructions to pass to the CLI
        working_directory: Directory where the CLI should be executed
        timeout: Command execution timeout in seconds (default: 7200)
        agent_args: Additional arguments to pass to the CLI
        capture_output: Whether to capture stdout/stderr (default: True)

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

    logger.info(f"Executing with instructions: {additional_instructions if additional_instructions else 'None'}...")
    logger.info(f"Working directory: {working_dir}")
    logger.info(f"Timeout: {timeout}s")
    logger.info(f"Agent args: {agent_args}")

    if _active_cli_configuration_index >= len(cli_configurations):
        _active_cli_configuration_index = 0

    final_result: Optional[Dict[str, Any]] = None
    for config_index in range(_active_cli_configuration_index, len(cli_configurations)):
        config = cli_configurations[config_index]
        cli_command = config["cli_command"]
        cmd = _build_command(
            cli_command=cli_command,
            cli_base_args=config["cli_args"],
            agent_args=agent_args,
            additional_instructions=additional_instructions,
        )

        logger.info(f"Using CLI configuration index: {config_index} ({cli_command})")
        result = _execute_command(
            cli_command=cli_command,
            cmd=cmd,
            working_dir=working_dir,
            timeout=timeout,
            capture_output=capture_output,
            start_time=start_time,
        )
        final_result = result

        if result["timeout"] and config_index + 1 < len(cli_configurations):
            logger.warning(f"Timeout on configuration index {config_index}, trying next configuration")
            continue

        _active_cli_configuration_index = config_index
        break

    if final_result is None:
        final_result = {
            "success": False,
            "execution_time": time.time() - start_time,
            "timestamp": datetime.now().isoformat(),
            "working_directory": str(working_dir),
            "command": "",
            "return_code": -1,
            "timeout": False,
            "error": "No CLI configurations available",
        }

    if _active_cli_configuration_index != 0 and len(cli_configurations) > 1:
        _rebalance_active_configuration(configs=cli_configurations, working_dir=working_dir)

    return final_result


def execute_with_instructions(
    instructions: str,
    work_dir: Path,
    agent_args: Optional[List[str]] = None,
    timeout: int = 7200,
) -> Dict[str, Any]:
    """Execute CLI with specific instructions.

    Args:
        instructions: The instructions to pass to the CLI
        work_dir: Working directory for command execution
        agent_args: Additional arguments to pass to the CLI
        timeout: Command execution timeout in seconds

    Returns:
        Dictionary containing execution results.
    """
    return run_cli_executor(
        additional_instructions=instructions,
        working_directory=work_dir,
        agent_args=agent_args,
        timeout=timeout,
    )


def run_opencode(
    additional_instructions: Optional[str] = None,
    working_directory: Optional[Path] = None,
    timeout: int = 7200,
    agent_args: Optional[List[str]] = None,
    capture_output: bool = True,
) -> Dict[str, Any]:
    """Backward-compatible wrapper for run_cli_executor.

    This function is deprecated and will be removed in a future version.
    Use run_cli_executor instead.

    Args:
        additional_instructions: Additional instructions to pass to the CLI
        working_directory: Directory where the CLI should be executed
        timeout: Command execution timeout in seconds (default: 7200)
        agent_args: Additional arguments to pass to the CLI
        capture_output: Whether to capture stdout/stderr (default: True)

    Returns:
        Dictionary containing execution results.
    """
    logger.warning("run_opencode is deprecated, use run_cli_executor instead")
    return run_cli_executor(
        additional_instructions=additional_instructions,
        working_directory=working_directory,
        timeout=timeout,
        agent_args=agent_args,
        capture_output=capture_output,
    )


def execute_openagent_with_instructions(
    instructions: str,
    work_dir: Path,
    agent_args: Optional[List[str]] = None,
    timeout: int = 7200,
) -> Dict[str, Any]:
    """Backward-compatible wrapper for execute_with_instructions.

    This function is deprecated and will be removed in a future version.
    Use execute_with_instructions instead.

    Args:
        instructions: The instructions to pass to the CLI
        work_dir: Working directory for command execution
        agent_args: Additional arguments to pass to the CLI
        timeout: Command execution timeout in seconds

    Returns:
        Dictionary containing execution results.
    """
    logger.warning("execute_openagent_with_instructions is deprecated, use execute_with_instructions instead")
    return execute_with_instructions(
        instructions=instructions,
        work_dir=work_dir,
        agent_args=agent_args,
        timeout=timeout,
    )
