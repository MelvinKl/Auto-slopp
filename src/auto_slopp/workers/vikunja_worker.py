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

from auto_slopp.utils.cli_executor import (
    execute_with_instructions,
    get_active_cli_command,
)
from auto_slopp.utils.git_operations import (
    checkout_branch_resilient,
    create_and_checkout_branch,
    get_current_branch,
    push_to_remote,
    sanitize_branch_name,
)
from auto_slopp.utils.vikunja_operations import (
    comment_on_task,
    find_or_create_project,
    get_open_tasks_by_project,
    update_task_status,
    verify_blocking_closed,
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

        if not self._checkout_main_branch(repo_dir=repo_path):
            results["errors"].append(f"Failed to checkout main branch for {repo_path.name}")
            results["success"] = False
            results["execution_time"] = self._get_elapsed_time(start_time)
            self._log_completion_summary(results)
            return results

        # Get project name from repo_path or settings
        project_name = repo_path.name

        # Find or create the project in Vikunja to get its ID
        project = find_or_create_project(project_name)
        if not project:
            self.logger.error(f"Failed to find or create Vikunja project: {project_name}")
            results["errors"].append(f"Failed to find or create Vikunja project: {project_name}")
            results["success"] = False
            results["execution_time"] = self._get_elapsed_time(start_time)
            self._log_completion_summary(results)
            return results

        project_id = project.get("id")
        if not project_id:
            self.logger.error(f"Project missing ID: {project}")
            results["errors"].append(f"Project missing ID: {project}")
            results["success"] = False
            results["execution_time"] = self._get_elapsed_time(start_time)
            self._log_completion_summary(results)
            return results

        self.logger.info(f"Using Vikunja project: {project.get('title')} (ID: {project_id})")

        tasks = get_open_tasks_by_project(project_id)

        if not tasks:
            self.logger.info(f"No open tasks found in Vikunja for project '{project_name}' (ID: {project_id})")
            results["execution_time"] = self._get_elapsed_time(start_time)
            self._log_completion_summary(results)
            return results

        tasks = self._filter_tasks_by_tag(tasks, settings.github_issue_worker_required_label)

        tasks = sorted(tasks, key=lambda t: t.get("priority", 0), reverse=True)

        for task in tasks:
            task_result = self._process_single_task(repo_path, task)
            results["task_results"].append(task_result)

            if task_result["success"]:
                results["tasks_processed"] += 1
                results["openagent_executions"] += task_result.get("openagent_executions", 0)
                results["tasks_completed"] += task_result.get("tasks_completed", 0)
            else:
                self.logger.warning(
                    f"Failed to process task #{task.get('id')}: {task_result.get('error', 'Unknown error')}"
                )

        results["execution_time"] = self._get_elapsed_time(start_time)
        self._log_completion_summary(results)

        return results

    def _checkout_main_branch(self, repo_dir: Path) -> bool:
        """Checkout the main branch and pull latest changes.

        Args:
            repo_dir: Path to the repository directory

        Returns:
            True if successful, False otherwise
        """
        if not self.dry_run:
            pull_success = checkout_branch_resilient(
                repo_dir=repo_dir,
                branch="main",
                fetch_first=True,
                timeout=60,
            )
            if not pull_success:
                self.logger.warning(f"Failed to pull latest changes from {repo_dir.name}")
                return False
        return True

    def _create_results_dict(self, start_time: float, repo_path: Path) -> Dict[str, Any]:
        """Create the initial results dictionary."""
        return {
            "worker_name": "VikunjaWorker",
            "execution_time": 0,
            "timestamp": start_time,
            "repo_path": str(repo_path),
            "dry_run": self.dry_run,
            "tasks_processed": 0,
            "openagent_executions": 0,
            "tasks_completed": 0,
            "task_results": [],
            "success": True,
            "errors": [],
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
            "task_closed": False,
            "tasks_closed": 0,
            "task_failed": False,
            "error": None,
        }

        try:
            branch_name = f"ai/task-{task_id}-{sanitize_branch_name(task_title[:30].lower())}"

            update_task_status(task_id, "in_progress")

            start_comment = (
                f"🚀 **Worker Started Processing**\n\n"
                f"Branch: {branch_name}\n\n"
                f"The worker has started processing this task."
            )
            comment_on_task(task_id, start_comment)

            if self.dry_run:
                self.logger.info(f"DRY RUN: Would create branch {branch_name} and execute instructions")
                result["openagent_executed"] = True
                result["success"] = True
                return result

            branch_created = create_and_checkout_branch(repo_dir, branch_name, base_branch="main")
            if not branch_created:
                result["error"] = f"Failed to create branch {branch_name}"

                failure_comment = (
                    f"⚠️ **Task Failed: Branch Creation Error**\n\n"
                    f"Failed to create branch '{branch_name}'.\n\n"
                    f"**Task:** {task_title}\n\n"
                    f"The system could not create a working branch for this task.\n\n"
                    f"This task will not be processed again automatically."
                )
                comment_success = comment_on_task(task_id, failure_comment)
                result["task_commented"] = comment_success

                update_task_status(task_id, "failed")
                result["task_failed"] = True

                return result

            instructions = self._build_instructions(task_title, task_description, branch_name=branch_name)

            openagent_result = execute_with_instructions(
                instructions,
                repo_dir,
                self.agent_args,
                self.timeout,
                task_name="vikunja_task",
            )
            result["openagent_executed"] = openagent_result["success"]
            if openagent_result["success"]:
                result["openagent_executions"] = 1

            if not openagent_result["success"]:
                cli_tool = get_active_cli_command()
                error_msg = f"{cli_tool} execution failed: {openagent_result.get('error', 'Unknown error')}"
                result["error"] = error_msg

                failure_comment = (
                    f"⚠️ **Task Failed: CLI Execution Error**\n\n"
                    f"The {cli_tool} CLI tool failed to execute the task.\n\n"
                    f"**Error:** {openagent_result.get('error', 'Unknown error')}\n\n"
                    f"Branch: {branch_name}\n\n"
                    f"This task will not be processed again automatically."
                )
                comment_success = comment_on_task(task_id, failure_comment)
                result["task_commented"] = comment_success

                update_task_status(task_id, "failed")
                result["task_failed"] = True

                return result

            current_branch = get_current_branch(repo_dir)
            if current_branch in ("main", "master"):
                self.logger.info(f"No changes made for task {task_id}, closing task with comment")

                no_changes_comment = (
                    f"✅ **Task Completed: No Changes Required**\n\n"
                    f"The task has been reviewed and no modifications were needed.\n\n"
                    f"**Task:** {task_title}\n\n"
                    f"After analyzing the requirements and exploring the codebase, "
                    f"the task was determined to be already complete or not applicable."
                )
                comment_success = comment_on_task(task_id, no_changes_comment)
                result["task_commented"] = comment_success

                status_success = update_task_status(task_id, "done")
                result["task_completed"] = status_success
                result["tasks_completed"] = 1 if status_success else 0

                result["success"] = True
                result["no_changes"] = True
                return result

            push_success, push_message = push_to_remote(repo_dir, remote="origin", branch=current_branch)
            if not push_success:
                result["error"] = f"Failed to push branch '{current_branch}': {push_message}"

                failure_comment = (
                    f"⚠️ **Task Failed: Push Error**\n\n"
                    f"Failed to push branch '{current_branch}' to remote.\n\n"
                    f"**Error:** {push_message}\n\n"
                    f"Local changes have been committed but could not be pushed.\n\n"
                    f"This task will not be processed again automatically."
                )
                comment_success = comment_on_task(task_id, failure_comment)
                result["task_commented"] = comment_success

                update_task_status(task_id, "failed")
                result["task_failed"] = True

                return result

            status_success = update_task_status(task_id, "done")
            result["task_completed"] = status_success
            result["tasks_completed"] = 1 if status_success else 0

            if status_success:
                success_comment = (
                    f"✅ **Task Completed Successfully**\n\n"
                    f"**Task:** {task_title}\n\n"
                    f"The task has been implemented and pushed to branch `{current_branch}`.\n\n"
                    f"**Branch:** {current_branch}\n\n"
                    f"Changes have been committed and pushed. The task is ready for review."
                )
                comment_success = comment_on_task(task_id, success_comment)
                result["task_commented"] = comment_success
                if not comment_success:
                    self.logger.warning(f"Failed to add comment to task {task_id}")
            else:
                self.logger.warning(f"Failed to update status for task {task_id}")

            result["success"] = True

        except Exception as e:
            self.logger.error(f"Error processing task {task_id}: {str(e)}")
            result["error"] = str(e)

            exception_comment = (
                f"⚠️ **Task Failed: Unexpected Error**\n\n"
                f"An unexpected error occurred while processing the task.\n\n"
                f"**Error:** {str(e)}\n\n"
                f"**Task:** {task_title}\n\n"
                f"This task will not be processed again automatically."
            )
            comment_success = comment_on_task(task_id, exception_comment)
            result["task_commented"] = comment_success

            update_task_status(task_id, "failed")
            result["task_failed"] = True

        return result

    def _build_instructions(
        self,
        task_title: str,
        task_description: str,
        branch_name: Optional[str] = None,
    ) -> str:
        """Build the instructions string from task title and description.

        Args:
            task_title: Task title
            task_description: Task description
            branch_name: Name of the branch already created for this task

        Returns:
            Complete instructions string
        """
        body_text = f"\n{task_description}" if task_description else ""

        branch_instruction = ""
        if branch_name:
            branch_instruction = (
                f"You are already on branch '{branch_name}'. "
                f"Work on this branch, implement the changes, commit them, and push.\n"
            )
        else:
            branch_instruction = (
                "Create a new branch that starts with ai/ from base origin/main. "
                "Work on this branch, implement the changes, commit them, and push.\n"
            )

        plan_text = """
Plan:
1. Understand the requirements by analyzing the task title and description
2. Explore the codebase to understand the current implementation
3. Identify components that can be reused
4. Design a solution that is simple and focused
5. Write or update tests for the changes
6. Implement the solution
7. Run 'make lint' to ensure code quality
8. Run 'make test' to verify all tests pass
9. Commit the changes with a clear commit message
10. Push the changes to the remote branch
"""

        return (
            f"{branch_instruction}"
            f"Implement the following:\n"
            f"Title: {task_title}\n"
            f"Description:{body_text}\n"
            f"{plan_text}\n"
            f"Keep your implementation simple. Only implement what is required. "
            f"Check if there are components you can reuse. "
            f"Ensure that 'make test' runs successful. Only push if ALL tests are successful. "
            f"Check if you need to update the README.md."
        )

    def _create_error_result(self, start_time: float, repo_path: Path, error_msg: str) -> Dict[str, Any]:
        """Create an error result dictionary."""
        return {
            "worker_name": "VikunjaWorker",
            "execution_time": self._get_elapsed_time(start_time),
            "timestamp": start_time,
            "repo_path": str(repo_path),
            "dry_run": self.dry_run,
            "success": False,
            "tasks_processed": 0,
            "openagent_executions": 0,
            "tasks_completed": 0,
            "task_results": [],
            "errors": [error_msg],
        }

    def _get_current_time(self) -> float:
        """Get current time as float for consistent timing."""
        return time.time()

    def _get_elapsed_time(self, start_time: float) -> float:
        """Get elapsed time from start time."""
        return time.time() - start_time

    def _filter_tasks_by_tag(self, tasks: List[Dict[str, Any]], tag_name: str) -> List[Dict[str, Any]]:
        """Filter tasks to only those whose labels contain a label with a matching title.

        Args:
            tasks: List of task dictionaries from Vikunja
            tag_name: Tag title to filter by (case-insensitive)

        Returns:
            List of tasks that have the specified tag
        """
        tag_lower = tag_name.lower()
        filtered = []
        for task in tasks:
            labels = task.get("labels") or []
            label_titles = [label.get("title", "").lower() for label in labels]
            if tag_lower in label_titles:
                filtered.append(task)
            else:
                self.logger.info(f"Skipping task #{task.get('id')} '{task.get('title')}': missing tag '{tag_name}'")
        return filtered

    def _has_no_open_dependencies(self, task_id: int) -> bool:
        """Check if a task has no open dependencies.

        Args:
            task_id: The Vikunja task ID

        Returns:
            True if all blocking tasks are closed (or there are none), False otherwise
        """
        try:
            return verify_blocking_closed(task_id)
        except Exception as e:
            self.logger.warning(f"Failed to verify blocking tasks for task {task_id}: {e}")
            return False

    def _log_completion_summary(self, results: Dict[str, Any]) -> None:
        """Log completion summary."""
        cli_tool = get_active_cli_command()
        self.logger.info(
            f"VikunjaWorker completed. Processed: "
            f"{results['tasks_processed']}, "
            f"{cli_tool} executions: {results['openagent_executions']}, "
            f"Tasks completed: {results['tasks_completed']}, "
            f"Errors: {len(results.get('errors', []))}"
        )
