"""CLI executor utilities for auto-slopp workers.

This module provides a centralized utility for executing configured CLI commands
(e.g., opencode, claude code) with consistent error handling, logging, and result formatting.
"""

import logging
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from settings.main import settings

logger = logging.getLogger(__name__)


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
    start_time = time.time()

    agent_args = agent_args or []
    working_dir = working_directory or Path.cwd()

    cli_command = settings.cli_command
    cli_base_args = settings.cli_args

    logger.info(
        f"Executing {cli_command} with instructions: {additional_instructions if additional_instructions else 'None'}..."
    )
    logger.info(f"Working directory: {working_dir}")
    logger.info(f"Timeout: {timeout}s")
    logger.info(f"Agent args: {agent_args}")

    cmd = [cli_command] + cli_base_args + agent_args

    if additional_instructions:
        cmd.append(additional_instructions)

    try:
        result = subprocess.run(
            cmd,
            cwd=working_dir,
            capture_output=capture_output,
            text=True,
            timeout=timeout,
        )

        execution_time = time.time() - start_time
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
        execution_time = time.time() - start_time
        error_msg = f"{cli_command} timed out after {timeout} seconds"
        logger.error(error_msg)

        return {
            "success": False,
            "execution_time": execution_time,
            "timestamp": datetime.now().isoformat(),
            "working_directory": str(working_dir),
            "command": " ".join(cmd),
            "return_code": -1,
            "timeout": False,
            "error": error_msg,
        }


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
