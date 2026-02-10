"""Task processing utilities for TaskProcessorWorker.

This module provides utilities for processing text files and managing
the task processing workflow.
"""

import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

from auto_slopp.utils.file_operations import (
    cleanup_temp_file,
    find_text_files,
    read_file_content,
    rename_processed_file,
    write_temp_instruction_file,
)
from auto_slopp.utils.git_operations import commit_and_push_changes

logger = logging.getLogger(__name__)


def create_repository_result(repo_dir: Path) -> Dict[str, Any]:
    """Create a result dictionary for repository processing.

    Args:
        repo_dir: Path to the repository directory

    Returns:
        Initialized result dictionary.
    """
    return {
        "repository": repo_dir.name,
        "path": str(repo_dir),
        "success": False,
        "text_files_processed": 0,
        "openagent_executions": 0,
        "files_renamed": 0,
        "git_operations": 0,
        "processed_files": [],
        "errors": [],
    }


def create_file_result(text_file: Path) -> Dict[str, Any]:
    """Create a result dictionary for file processing.

    Args:
        text_file: Path to the text file

    Returns:
        Initialized file result dictionary.
    """
    return {
        "file": str(text_file),
        "success": False,
        "instructions": "",
        "openagent_executed": False,
        "file_renamed": False,
        "git_operations": False,
        "error": None,
    }


def execute_openagent_with_instructions(
    instructions: str, work_dir: Path, agent_args: list, timeout: int
) -> Dict[str, Any]:
    """Execute OpenAgent with specific instructions.

    Args:
        instructions: Text instructions to pass to OpenAgent
        work_dir: Working directory for OpenAgent execution
        agent_args: Additional arguments to pass to OpenAgent
        timeout: Timeout for OpenAgent execution in seconds

    Returns:
        Dictionary containing OpenAgent execution results
    """
    try:
        logger.info(
            f"Executing OpenAgent with instructions length: {len(instructions)}"
        )

        # Create a temporary instruction file
        instruction_file = write_temp_instruction_file(work_dir, instructions)

        try:
            # Build OpenAgent command
            cmd = ["opencode"] + ["--agent", "openagent"] + agent_args
            cmd.append(str(instruction_file))

            # Execute OpenAgent
            result = subprocess.run(
                cmd,
                cwd=work_dir,
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            logger.info(
                f"OpenAgent execution completed with return code: {result.returncode}"
            )

            return {
                "success": result.returncode == 0,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "timeout": False,
            }

        finally:
            # Clean up instruction file
            cleanup_temp_file(instruction_file)

    except subprocess.TimeoutExpired:
        logger.error(f"OpenAgent execution timed out after {timeout} seconds")
        return {
            "success": False,
            "timeout": True,
            "error": f"OpenAgent execution timed out after {timeout} seconds",
        }

    except Exception as e:
        logger.error(f"Error executing OpenAgent: {str(e)}")
        return {
            "success": False,
            "error": f"Error executing OpenAgent: {str(e)}",
        }


def process_text_file(
    text_file: Path,
    task_repo_dir: Path,
    dry_run: bool = False,
    agent_args: Optional[list] = None,
    timeout: int = 600,
    counter_start: int = 1,
) -> Dict[str, Any]:
    """Process a single text file with instructions.

    Args:
        text_file: Path to the text file
        task_repo_dir: Directory in task_repo_path for this repository
        dry_run: If True, skip actual OpenAgent execution and git operations
        agent_args: Additional arguments to pass to OpenAgent
        timeout: Timeout for OpenAgent execution in seconds
        counter_start: Starting number for 4-digit file counter

    Returns:
        Dictionary containing processing results for this file
    """
    if agent_args is None:
        agent_args = []

    result = create_file_result(text_file)

    try:
        # Read file content as instructions
        instructions = read_file_content(text_file)
        if instructions is None:
            result["error"] = "Text file is empty or unreadable"
            return result

        result["instructions"] = instructions
        logger.info(f"Loaded instructions from {text_file.name}")
        instructions = f"Create a new branch that starts with ai/ with base origin/main and implement the following:\n{instructions}\nKeep your implementation simple. Only implement what is required. Ensure that 'make test' runs successful. Check if you need to update the README.md. Push your changes and create a pull request on github."
        # Execute OpenAgent with the instructions
        if not dry_run:
            openagent_result = execute_openagent_with_instructions(
                instructions, task_repo_dir, agent_args, timeout
            )
            result["openagent_executed"] = openagent_result["success"]

            if not openagent_result["success"]:
                result["error"] = (
                    f"OpenCode execution failed: "
                    f"{openagent_result.get('error', 'Unknown error')}"
                )
                return result
        else:
            logger.info(
                f"DRY RUN: Would execute OpenAgent with instructions from {text_file.name}"
            )
            result["openagent_executed"] = True

        # Rename the file with counter and .used suffix
        new_file_path = rename_processed_file(text_file, counter_start)
        result["file_renamed"] = new_file_path is not None

        if new_file_path:
            logger.info(f"Renamed {text_file.name} to {new_file_path.name}")

        # Commit and push changes in task_repo_path
        if not dry_run:
            commit_success, push_success = commit_and_push_changes(
                task_repo_dir, f"Process instructions from {text_file.name}"
            )
            result["git_operations"] = commit_success

            if not commit_success:
                result["error"] = "Git commit/push operations failed"
                return result
        else:
            logger.info(f"DRY RUN: Would commit and push changes for {text_file.name}")
            result["git_operations"] = True

        result["success"] = True

    except Exception as e:
        logger.error(f"Error processing text file {text_file.name}: {str(e)}")
        result["error"] = str(e)

    return result


def process_repository(
    repo_dir: Path,
    task_repo_dir: Path,
    dry_run: bool = False,
    agent_args: Optional[list] = None,
    timeout: int = 600,
    counter_start: int = 1,
) -> Dict[str, Any]:
    """Process a single repository directory.

    Args:
        repo_dir: Path to the repository directory
        task_repo_dir: Directory in task_repo_path for this repository
        dry_run: If True, skip actual OpenAgent execution and git operations
        agent_args: Additional arguments to pass to OpenAgent
        timeout: Timeout for OpenAgent execution in seconds
        counter_start: Starting number for 4-digit file counter

    Returns:
        Dictionary containing processing results for this repository
    """
    from auto_slopp.utils.file_operations import ensure_directory_exists

    result = create_repository_result(repo_dir)

    try:
        # Create corresponding directory in task_repo_path
        if not ensure_directory_exists(task_repo_dir):
            result["errors"].append(f"Failed to create task directory: {task_repo_dir}")
            return result

        logger.info(f"Ensured task directory exists: {task_repo_dir}")

        # Find .txt files in the repository
        text_files = find_text_files(repo_dir)

        if not text_files:
            logger.info(f"No .txt files found in {repo_dir.name}")
            result["success"] = True
            return result

        # Process each text file
        for text_file in text_files:
            file_result = process_text_file(
                text_file, task_repo_dir, dry_run, agent_args, timeout, counter_start
            )
            result["processed_files"].append(file_result)

            if file_result["success"]:
                result["text_files_processed"] += 1
                if file_result.get("openagent_executed", False):
                    result["openagent_executions"] += 1
                if file_result.get("file_renamed", False):
                    result["files_renamed"] += 1
                if file_result.get("git_operations", False):
                    result["git_operations"] += 1
            else:
                result["errors"].append(
                    file_result.get("error", "Unknown processing error")
                )

        result["success"] = len(result["errors"]) == 0

    except Exception as e:
        logger.error(f"Error processing repository {repo_dir.name}: {str(e)}")
        result["errors"].append(str(e))

    return result
