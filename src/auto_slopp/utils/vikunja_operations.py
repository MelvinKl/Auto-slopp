"""Vikunja operations utilities for workers.

This module provides pure functions for common Vikunja operations
used across different workers.
"""

import json
import logging
import subprocess
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class VikunjaOperationError(Exception):
    """Exception raised when Vikunja operations fail."""

    pass


def _run_vikunja_command(
    *args: str,
    check: bool = True,
    timeout: int = 30,
    capture_output: bool = True,
) -> subprocess.CompletedProcess:
    """Run a vikunja-cli-helper command.

    Args:
        *args: Vikunja CLI command arguments
        check: Whether to raise exception on non-zero return code
        timeout: Timeout for the command in seconds
        capture_output: Whether to capture output

    Returns:
        CompletedProcess instance

    Raises:
        VikunjaOperationError: If vikunja-cli-helper command fails and check is True
    """
    cmd = ["vikunja-cli-helper", *args]
    try:
        result = subprocess.run(
            cmd,
            capture_output=capture_output,
            text=capture_output,
            check=check,
            timeout=timeout,
        )
        return result
    except subprocess.CalledProcessError as e:
        error_output = (
            (e.stderr.strip() or e.stdout.strip()) if e.stderr or e.stdout else str(e)
        )
        logger.error(
            f"Vikunja command 'vikunja-cli-helper {' '.join(args)}' failed: {error_output}"
        )
        raise VikunjaOperationError(f"Vikunja command failed: {error_output}")
    except (subprocess.TimeoutExpired, TimeoutError) as e:
        logger.error(f"Vikunja command 'vikunja-cli-helper {' '.join(args)}' timed out")
        raise VikunjaOperationError(f"Vikunja command timed out: {e}")


def find_project(project_name: str) -> Optional[Dict[str, Any]]:
    """Find a project by name or identifier.

    Args:
        project_name: Project name or identifier to search for

    Returns:
        Dictionary containing project information (id, title, identifier, etc) or None if not found.

    Raises:
        VikunjaOperationError: If command fails
    """
    try:
        result = _run_vikunja_command(
            "-find-project",
            project_name,
            check=False,
        )

        if result.returncode != 0:
            project_error = result.stderr.strip() or result.stdout.strip()
            if "project not found" in project_error.lower():
                logger.info(f"Project '{project_name}' not found")
                return None
            logger.error(f"Failed to find project '{project_name}': {project_error}")
            return None

        project_data = json.loads(result.stdout)
        return (
            project_data.get("data")
            if isinstance(project_data, dict) and "data" in project_data
            else project_data
        )

    except VikunjaOperationError as e:
        logger.error(f"Error finding project '{project_name}': {str(e)}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse project JSON for '{project_name}': {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error finding project '{project_name}': {str(e)}")
        return None


def create_project(
    project_name: str, project_identifier: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Create a new project.

    Args:
        project_name: Name for the new project
        project_identifier: Optional identifier for the project (defaults to project_name)

    Returns:
        Dictionary containing project information or None if failed.
    """
    if project_identifier is None:
        project_identifier = project_name.lower().replace(" ", "-")

    try:
        cmd_args = [
            "-create-project",
            project_name,
            "-project-identifier",
            project_identifier,
        ]
        result = _run_vikunja_command(*cmd_args, check=False)

        if result.returncode != 0:
            error_output = result.stderr.strip() or result.stdout.strip()
            logger.error(f"Failed to create project '{project_name}': {error_output}")
            return None

        project_data = json.loads(result.stdout)
        return (
            project_data.get("data")
            if isinstance(project_data, dict) and "data" in project_data
            else project_data
        )

    except VikunjaOperationError as e:
        logger.error(f"Error creating project '{project_name}': {str(e)}")
        return None
    except json.JSONDecodeError as e:
        logger.error(
            f"Failed to parse create project JSON for '{project_name}': {str(e)}"
        )
        return None
    except Exception as e:
        logger.error(f"Unexpected error creating project '{project_name}': {str(e)}")
        return None


def find_or_create_project(
    project_name: str, project_identifier: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Find an existing project or create a new one if not found.

    Args:
        project_name: Project name or identifier to search for/create
        project_identifier: Optional identifier for the new project (defaults to project_name)

    Returns:
        Dictionary containing project information or None if failed.
    """
    project = find_project(project_name)
    if project is not None:
        return project

    logger.info(f"Project '{project_name}' not found, creating new project")
    return create_project(project_name, project_identifier)


def create_task(
    project_id: int,
    title: str,
    description: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Create a new task in a project.

    Args:
        project_id: ID of the project to create the task in
        title: Title for the new task
        description: Optional description for the task

    Returns:
        Dictionary containing task information or None if failed.
    """
    try:
        cmd_args = [
            "-create-task",
            str(project_id),
            "-task-title",
            title,
        ]
        if description:
            cmd_args.extend(["-task-description", description])

        result = _run_vikunja_command(*cmd_args, check=False)

        if result.returncode != 0:
            error_output = result.stderr.strip() or result.stdout.strip()
            logger.error(
                f"Failed to create task '{title}' in project {project_id}: {error_output}"
            )
            return None

        task_data = json.loads(result.stdout)
        return (
            task_data.get("data")
            if isinstance(task_data, dict) and "data" in task_data
            else task_data
        )

    except VikunjaOperationError as e:
        logger.error(f"Error creating task '{title}' in project {project_id}: {str(e)}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse create task JSON for '{title}': {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error creating task '{title}': {str(e)}")
        return None


def get_tasks(
    task_filter: Optional[str] = None,
    sort_by: Optional[str] = None,
    order_by: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Get list of tasks from Vikunja.

    Args:
        task_filter: Optional filter string (e.g., "done=false", "assignee_id=1")
        sort_by: Optional sort field (e.g., "id", "title", "priority")
        order_by: Optional order direction ("asc" or "desc")

    Returns:
        List of dictionaries containing task information.

    Raises:
        VikunjaOperationError: If command fails
    """
    try:
        cmd_args = ["-list-tasks"]
        if task_filter:
            cmd_args.extend(["-task-filter", task_filter])
        if sort_by:
            cmd_args.extend(["-task-sort-by", sort_by])
        if order_by:
            cmd_args.extend(["-task-order-by", order_by])

        result = _run_vikunja_command(*cmd_args, check=False)

        if result.returncode != 0:
            error_output = result.stderr.strip() or result.stdout.strip()
            logger.error(f"Failed to list tasks: {error_output}")
            return []

        data = json.loads(result.stdout)
        tasks = (
            data.get("data", [])
            if isinstance(data, dict) and "data" in data
            else (data if isinstance(data, list) else [])
        )
        return tasks

    except VikunjaOperationError as e:
        logger.error(f"Error listing tasks: {str(e)}")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse task list JSON: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error listing tasks: {str(e)}")
        return []


def get_task_details(task_id: int) -> Optional[Dict[str, Any]]:
    """Get detailed information about a specific task.

    Args:
        task_id: ID of the task to retrieve

    Returns:
        Dictionary containing task details or None if not found.
    """
    try:
        tasks = get_tasks(task_filter=f"id={task_id}")
        if not tasks:
            return None

        for task in tasks:
            if task.get("id") == task_id:
                return task

        return None

    except Exception as e:
        logger.error(f"Error getting task details for ID {task_id}: {str(e)}")
        return None


def update_task_status(task_id: int, status: str) -> bool:
    """Update the status of a task.

    Args:
        task_id: ID of the task to update
        status: New status value (e.g., "done", "in_progress", "closed")

    Returns:
        True if successful, False otherwise.
    """
    try:
        result = _run_vikunja_command(
            "-update-task-id",
            str(task_id),
            "-task-status",
            status,
            check=False,
        )
        return result.returncode == 0

    except VikunjaOperationError as e:
        logger.error(f"Error updating status for task {task_id}: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error updating status for task {task_id}: {str(e)}")
        return False


def comment_on_task(task_id: int, comment: str) -> bool:
    """Add a comment to a task.

    Args:
        task_id: ID of the task to comment on
        comment: Comment text to add

    Returns:
        True if successful, False otherwise.
    """
    try:
        result = _run_vikunja_command(
            "-comment-task-id",
            str(task_id),
            "-comment-text",
            comment,
            check=False,
        )
        return result.returncode == 0

    except VikunjaOperationError as e:
        logger.error(f"Error commenting on task {task_id}: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error commenting on task {task_id}: {str(e)}")
        return False


def create_subtask(
    parent_task_id: int, title: str, description: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Create a subtask for a parent task.

    Args:
        parent_task_id: ID of the parent task
        title: Title for the new subtask
        description: Optional description for the subtask

    Returns:
        Dictionary containing subtask information or None if failed.
    """
    try:
        cmd_args = ["-create-subtask", str(parent_task_id), "-subtask-title", title]
        if description:
            cmd_args.extend(["-subtask-description", description])

        result = _run_vikunja_command(*cmd_args, check=False)

        if result.returncode != 0:
            error_output = result.stderr.strip() or result.stdout.strip()
            logger.error(
                f"Failed to create subtask for task {parent_task_id}: {error_output}"
            )
            return None

        subtask_data = json.loads(result.stdout)
        return (
            subtask_data.get("data")
            if isinstance(subtask_data, dict) and "data" in subtask_data
            else subtask_data
        )

    except VikunjaOperationError as e:
        logger.error(f"Error creating subtask for task {parent_task_id}: {str(e)}")
        return None
    except json.JSONDecodeError as e:
        logger.error(
            f"Failed to parse create subtask JSON for task {parent_task_id}: {str(e)}"
        )
        return None
    except Exception as e:
        logger.error(
            f"Unexpected error creating subtask for task {parent_task_id}: {str(e)}"
        )
        return None


def analyze_task(task_id: int) -> Optional[List[Dict[str, Any]]]:
    """Analyze a task and generate subtasks using AI.

    Args:
        task_id: ID of the task to analyze

    Returns:
        List of created subtask dictionaries or None if failed.
    """
    try:
        result = _run_vikunja_command(
            "-analyze-task",
            str(task_id),
            check=False,
        )

        if result.returncode != 0:
            error_output = result.stderr.strip() or result.stdout.strip()
            logger.error(f"Failed to analyze task {task_id}: {error_output}")
            return None

        data = json.loads(result.stdout)
        subtasks = (
            data.get("data", [])
            if isinstance(data, dict) and "data" in data
            else (data if isinstance(data, list) else [])
        )
        return subtasks

    except VikunjaOperationError as e:
        logger.error(f"Error analyzing task {task_id}: {str(e)}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse analyze task JSON for task {task_id}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error analyzing task {task_id}: {str(e)}")
        return None


def check_task_dependencies(task_id: int) -> List[Dict[str, Any]]:
    """Check dependencies for a task.

    Args:
        task_id: ID of the task to check dependencies for

    Returns:
        List of dependency task information.
    """
    try:
        result = _run_vikunja_command(
            "-check-deps",
            str(task_id),
            check=False,
        )

        if result.returncode != 0:
            error_output = result.stderr.strip() or result.stdout.strip()
            logger.warning(
                f"Failed to check dependencies for task {task_id}: {error_output}"
            )
            return []

        data = json.loads(result.stdout)
        dependencies = (
            data.get("data", [])
            if isinstance(data, dict) and "data" in data
            else (data if isinstance(data, list) else [])
        )
        return dependencies

    except VikunjaOperationError as e:
        logger.error(f"Error checking dependencies for task {task_id}: {str(e)}")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse dependencies JSON for task {task_id}: {str(e)}")
        return []
    except Exception as e:
        logger.error(
            f"Unexpected error checking dependencies for task {task_id}: {str(e)}"
        )
        return []


def verify_blocking_closed(task_id: int) -> bool:
    """Verify if all blocking dependencies for a task are closed.

    Args:
        task_id: ID of the task to verify

    Returns:
        True if all blocking tasks are closed, False otherwise.
    """
    try:
        result = _run_vikunja_command(
            "-verify-blocking-closed",
            str(task_id),
            check=False,
        )

        if result.returncode != 0:
            error_output = result.stderr.strip() or result.stdout.strip()
            logger.warning(
                f"Failed to verify blocking tasks for task {task_id}: {error_output}"
            )
            return False

        data = json.loads(result.stdout)

        if isinstance(data, dict):
            if data.get("error"):
                return False
            return data.get("all_blocking_closed", False)

        return False

    except VikunjaOperationError as e:
        logger.error(f"Error verifying blocking tasks for task {task_id}: {str(e)}")
        return False
    except json.JSONDecodeError as e:
        logger.error(
            f"Failed to parse verify blocking JSON for task {task_id}: {str(e)}"
        )
        return False
    except Exception as e:
        logger.error(
            f"Unexpected error verifying blocking tasks for task {task_id}: {str(e)}"
        )
        return False


def get_open_tasks_by_project(project_id: int) -> List[Dict[str, Any]]:
    """Get open tasks for a specific project.

    Args:
        project_id: ID of the project to get tasks for

    Returns:
        List of open task dictionaries for the project.
    """
    return get_tasks(task_filter=f"project_id={project_id},done=false")


def get_task_by_identifier(identifier: str) -> Optional[Dict[str, Any]]:
    """Get a task by its identifier.

    Args:
        identifier: Task identifier (e.g., "T5-1")

    Returns:
        Dictionary containing task information or None if not found.
    """
    try:
        tasks = get_tasks()
        if not tasks:
            return None

        for task in tasks:
            if task.get("identifier") == identifier:
                return task

        return None

    except Exception as e:
        logger.error(f"Error getting task by identifier '{identifier}': {str(e)}")
        return None
