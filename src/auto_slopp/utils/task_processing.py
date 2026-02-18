"""Task processing utilities for TaskProcessorWorker.

This module provides utilities for processing text files and managing
the task processing workflow.
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from auto_slopp.utils.file_operations import (
    find_text_files,
    read_file_content,
    rename_processed_file,
)
from auto_slopp.utils.git_operations import commit_and_push_changes, get_current_branch
from auto_slopp.utils.github_operations import create_pull_request
from auto_slopp.utils.slop_machine import (
    execute_openagent_with_instructions,
    run_slop_machine,
)

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


def process_text_file(
    text_file: Path,
    task_repo_dir: Path,
    repo_dir: Path,
    dry_run: bool = False,
    agent_args: Optional[list] = None,
    timeout: int = 7200,
    counter_start: int = 1,
) -> Dict[str, Any]:
    """Process a single text file with instructions.

    Args:
        text_file: Path to the text file (in task_repo_dir)
        task_repo_dir: Directory in task_repo_path for this repository
        repo_dir: Directory where OpenCode should execute the instructions
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
        instructions = f"Create a new branch that starts with ai/ from base origin/main and implement the following:\n{instructions}\nKeep your implementation simple. Only implement what is required. Check if there are components you can reuse. Ensure that 'make test' runs successful. Only push if ALL tests are successful. Check if you need to update the README.md. Push your changes and create a pull request on github."
        # Execute OpenAgent with the instructions
        if not dry_run:
            openagent_result = execute_openagent_with_instructions(instructions, repo_dir, agent_args, timeout)
            result["openagent_executed"] = openagent_result["success"]

            if not openagent_result["success"]:
                result["error"] = f"OpenCode execution failed: {openagent_result.get('error', 'Unknown error')}"
                return result

            current_branch = get_current_branch(repo_dir)
            logger.info(f"Current branch after OpenCode execution: {current_branch}")

            push_branch_result = run_slop_machine(
                additional_instructions=f"git push -u origin {current_branch}",
                working_directory=repo_dir,
                timeout=60,
                capture_output=True,
            )

            if not push_branch_result["success"]:
                logger.warning(
                    f"Failed to push branch {current_branch}: {push_branch_result.get('error', 'Unknown error')}"
                )

            pr_result = create_pull_request(
                repo_dir=repo_dir,
                title=f"AI: {text_file.stem}",
                body=f"Automated changes from processing {text_file.name}",
                head=current_branch,
                base="main",
            )

            if pr_result:
                logger.info(f"Created PR #{pr_result.get('number')}: {pr_result.get('url')}")
                result["pr_created"] = True
                result["pr_url"] = pr_result.get("url")
            else:
                logger.warning("Failed to create pull request")
                result["pr_created"] = False
        else:
            logger.info(f"DRY RUN: Would execute OpenAgent with instructions from {text_file.name}")
            result["openagent_executed"] = True

        # Rename the file with counter and .used suffix
        new_file_path = rename_processed_file(text_file, counter_start)
        result["file_renamed"] = new_file_path is not None

        if new_file_path:
            logger.info(f"Renamed {text_file.name} to {new_file_path.name}")

        # Commit and push changes in task_repo_path
        if not dry_run:
            # Commit the changes and push to remote
            commit_success, push_success = commit_and_push_changes(
                task_repo_dir,
                f"Process instruction file: {text_file.name}",
                push_if_remote=True,
            )

            if not commit_success:
                result["error"] = "Git commit operations failed"
                return result

            if push_success is False:
                result["error"] = "Git push operations failed"
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
    timeout: int = 7200,
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

        # Find .txt files in the task repository (not the original repo)
        text_files = find_text_files(task_repo_dir)

        if not text_files:
            logger.info(f"No .txt files found in {task_repo_dir.name} (task repository)")
            result["success"] = True
            return result

        # Note: Git pull is now handled in TaskProcessorWorker before calling process_repository
        # This ensures we pull latest changes from task repository before processing

        # Only process ONE file per repository per iteration to ensure fair share
        if text_files:
            text_file = text_files[0]  # Process oldest file first
            file_result = process_text_file(
                text_file,
                task_repo_dir,
                repo_dir,
                dry_run,
                agent_args,
                timeout,
                counter_start,
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
                result["errors"].append(file_result.get("error", "Unknown processing error"))

        result["success"] = len(result["errors"]) == 0

        # Push the changes to remote
        if not dry_run and result["success"]:
            push_result = run_slop_machine(
                additional_instructions="git push origin main",
                working_directory=repo_dir,
                timeout=60,
                capture_output=True,
            )
            if push_result["success"]:
                logger.info(f"Successfully pushed changes from {repo_dir.name}")
            else:
                logger.warning(
                    f"Failed to push changes from {repo_dir.name}: {push_result.get('error', 'Unknown error')}"
                )
    except Exception as e:
        logger.error(f"Error processing repository {repo_dir.name}: {str(e)}")
        result["errors"].append(str(e))

    return result
