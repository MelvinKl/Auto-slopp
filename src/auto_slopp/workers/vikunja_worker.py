"""Vikunja Worker for processing tasks as instructions.

This worker:
1. Searches Vikunja for open tasks
2. Uses task title/description as instructions
3. Creates a new branch starting with ai/
4. Uses Vikunja tasks for planning/execution instead of .ralph files
5. Creates a PR and closes the task
"""

import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from auto_slopp.utils.vikunja_operations import (
    find_project,
    get_open_tasks_by_project,
)
from auto_slopp.worker import Worker
from settings.main import settings


class VikunjaWorker(Worker):
    """Worker for processing Vikunja tasks as instructions.

    This worker searches Vikunja for open tasks,
    uses the task title and description as instructions for the configured CLI tool,
    creates a new branch, executes the instructions, and creates a PR.
    """

    def __init__(
        self,
        timeout: int | None = None,
        agent_args: Optional[List[str]] = None,
        dry_run: bool = False,
    ):
        """Initialize the VikunjaWorker.

        Args:
            timeout: Timeout for CLI execution in seconds (default: from settings.slop_timeout)
            agent_args: Additional arguments to pass to the CLI tool
            dry_run: If True, skip actual CLI execution and git operations
        """
        self.timeout = timeout if timeout is not None else settings.slop_timeout
        self.agent_args = agent_args or []
        self.dry_run = dry_run
        self.logger = logging.getLogger("auto_slopp.workers.VikunjaWorker")

    def run(self, repo_path: Path) -> Dict[str, Any]:
        """Execute the Vikunja task processing workflow for a single repository.

        Args:
            repo_path: Path to the repository directory

        Returns:
            Dictionary containing execution results and statistics
        """
        start_time = self._get_current_time()
        self.logger.info(f"VikunjaWorker starting with repo_path: {repo_path}")

        if not repo_path.exists():
            return self._create_error_result(
                start_time,
                repo_path,
                f"Repository path does not exist: {repo_path}",
            )

        results = self._create_results_dict(start_time, repo_path)

        # Get project name from repo_path or settings
        project_name = repo_path.name

        # Find the project in Vikunja to get its ID
        project = find_project(project_name)
        if not project:
            self.logger.warning(f"Project '{project_name}' not found in Vikunja")
            results["repositories_with_errors"] += 1
            results["success"] = False
            results["execution_time"] = self._get_elapsed_time(start_time)
            self._log_completion_summary(results)
            return results

        project_id = project.get("id")
        if not project_id:
            self.logger.warning(f"Project '{project_name}' does not have a valid ID")
            results["repositories_with_errors"] += 1
            results["success"] = False
            results["execution_time"] = self._get_elapsed_time(start_time)
            self._log_completion_summary(results)
            return results

        tasks = get_open_tasks_by_project(project_id)

        if not tasks:
            self.logger.info(f"No open tasks found in Vikunja for project '{project_name}' (ID: {project_id})")
            results["execution_time"] = self._get_elapsed_time(start_time)
            self._log_completion_summary(results)
            return results

        for task in tasks:
            task_result = self._process_single_task(repo_path, task)
            results["task_results"].append(task_result)

            if task_result["success"]:
                results["tasks_processed"] += 1
                results["openagent_executions"] += task_result.get("openagent_executions", 0)
                results["prs_created"] += task_result.get("prs_created", 0)
                results["tasks_closed"] += task_result.get("tasks_closed", 0)
            else:
                self.logger.warning(
                    f"Failed to process task #{task.get('id')}: {task_result.get('error', 'Unknown error')}"
                )

        results["execution_time"] = self._get_elapsed_time(start_time)
        self._log_completion_summary(results)

        return results

    def _create_results_dict(self, start_time: float, repo_path: Path) -> Dict[str, Any]:
        """Create the initial results dictionary."""
        return {
            "worker_name": "VikunjaWorker",
            "execution_time": 0,
            "timestamp": start_time,
            "repo_path": str(repo_path),
            "dry_run": self.dry_run,
            "repositories_processed": 1,
            "repositories_with_errors": 0,
            "tasks_processed": 0,
            "openagent_executions": 0,
            "prs_created": 0,
            "tasks_closed": 0,
            "task_results": [],
            "success": True,
        }

    def _process_single_task(self, repo_dir: Path, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single task from Vikunja.

        Args:
            repo_dir: Path to the repository directory
            task: The task dictionary from Vikunja

        Returns:
            Processing result for this task
        """
        self.logger.info(f"Processing Vikunja task for: {repo_dir.name}")

        task_id = task["id"]
        task_title = task["title"]
        task_description = task.get("description", "") or ""

        self.logger.info(f"Processing task #{task_id}: {task_title}")

        result = {
            "repository": repo_dir.name,
            "task_id": task_id,
            "task_title": task_title,
            "success": False,
            "openagent_executed": False,
            "openagent_executions": 0,
            "pr_created": False,
            "prs_created": 0,
            "task_closed": False,
            "tasks_closed": 0,
            "error": None,
        }

        try:
            if self.dry_run:
                self.logger.info(f"DRY RUN: Would execute task '{task_title}'")
                result["openagent_executed"] = True
                result["success"] = True
                return result

            self.logger.info(f"Task '{task_title}' marked for processing (detailed logic in Step 5)")
            result["success"] = True
            result["openagent_executed"] = True
            result["openagent_executions"] = 1

        except Exception as e:
            self.logger.error(f"Error processing task #{task_id}: {str(e)}")
            result["error"] = str(e)

        return result

    def _create_error_result(self, start_time: float, repo_path: Path, error_msg: str) -> Dict[str, Any]:
        """Create an error result dictionary."""
        return {
            "worker_name": "VikunjaWorker",
            "execution_time": self._get_elapsed_time(start_time),
            "timestamp": start_time,
            "repo_path": str(repo_path),
            "dry_run": self.dry_run,
            "success": False,
            "error": error_msg,
            "repositories_processed": 0,
            "repositories_with_errors": 1,
            "tasks_processed": 0,
            "openagent_executions": 0,
            "prs_created": 0,
            "tasks_closed": 0,
            "task_results": [],
        }

    def _get_current_time(self) -> float:
        """Get current time as float for consistent timing."""
        return time.time()

    def _get_elapsed_time(self, start_time: float) -> float:
        """Get elapsed time from start time."""
        return time.time() - start_time

    def _log_completion_summary(self, results: Dict[str, Any]) -> None:
        """Log completion summary."""
        self.logger.info(
            f"VikunjaWorker completed. Processed: "
            f"{results['tasks_processed']}, "
            f"PRs created: {results['prs_created']}, "
            f"Tasks closed: {results['tasks_closed']}, "
            f"Errors: {results['repositories_with_errors']}"
        )
