"""Unified Issue Worker for processing tasks from different sources.

This worker provides a common implementation for processing tasks from
various sources (GitHub Issues, Vikunja, etc.) using the Ralph loop
for step-based execution.
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
    commit_and_push_changes,
    create_and_checkout_branch,
    get_current_branch,
    has_changes,
    push_to_remote,
)
from auto_slopp.utils.github_operations import (
    create_pull_request,
    get_pr_for_branch,
)
from auto_slopp.utils.ralph import RalphExecutor
from auto_slopp.worker import Worker
from auto_slopp.workers.task_source import Task, TaskSource
from settings.main import settings


class IssueWorker(Worker):
    """Unified worker for processing tasks from different sources using Ralph loop.

    This worker accepts a TaskSource implementation and processes tasks
    using the Ralph loop for step-based execution. It handles task lifecycle
    events (start, complete, failure, no changes) via the TaskSource interface.
    """

    def __init__(
        self,
        task_source: TaskSource,
        timeout: int | None = None,
        agent_args: Optional[List[str]] = None,
        dry_run: bool = False,
    ):
        """Initialize the IssueWorker.

        Args:
            task_source: TaskSource implementation for loading tasks from a specific source
            timeout: Timeout for CLI execution in seconds (default: from settings.slop_timeout)
            agent_args: Additional arguments to pass to the CLI tool
            dry_run: If True, skip actual CLI execution and git operations
        """
        self.task_source = task_source
        self.timeout = timeout if timeout is not None else settings.slop_timeout
        self.agent_args = agent_args or []
        self.dry_run = dry_run
        self.logger = logging.getLogger("auto_slopp.workers.IssueWorker")

        max_iterations = settings.github_issue_step_max_iterations

        self.ralph_executor = RalphExecutor(
            logger=self.logger,
            agent_args=self.agent_args,
            timeout=self.timeout,
            execute_fn=execute_with_instructions,
            has_changes_fn=has_changes,
            commit_fn=commit_and_push_changes,
            max_iterations=max_iterations,
            file_prefix=task_source.get_ralph_file_prefix(),
            task_planning_name="task_planning",
            implementation_name="implementation",
            validation_name="task_implementation_validation",
            remaining_steps_update_name="remaining_steps_update",
        )

    def run(self, repo_path: Path) -> Dict[str, Any]:
        """Execute the task processing workflow for a single repository.

        Args:
            repo_path: Path to the repository directory

        Returns:
            Dictionary containing execution results and statistics
        """
        start_time = self._get_current_time()
        self.logger.info(f"IssueWorker starting with repo_path: {repo_path}")

        if not repo_path.exists():
            return self._create_error_result(
                start_time,
                repo_path,
                f"Repository path does not exist: {repo_path}",
            )

        results = self._create_results_dict(start_time, repo_path)

        if not self._checkout_main_branch(repo_dir=repo_path):
            results["repositories_with_errors"] += 1
            results["success"] = False
            results["execution_time"] = self._get_elapsed_time(start_time)
            self._log_completion_summary(results)
            return results

        tasks = self.task_source.get_tasks(repo_path)

        if not tasks:
            self.logger.info(f"No tasks found for {repo_path.name}")
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
                results["tasks_completed"] += task_result.get("tasks_completed", 0)
            else:
                self.logger.warning(f"Failed to process task #{task.id}: {task_result.get('error', 'Unknown error')}")

        results["execution_time"] = self._get_elapsed_time(start_time)
        self._log_completion_summary(results)

        return results

    def _create_results_dict(self, start_time: float, repo_path: Path) -> Dict[str, Any]:
        """Create the initial results dictionary."""
        return {
            "worker_name": "IssueWorker",
            "execution_time": 0,
            "timestamp": start_time,
            "repo_path": str(repo_path),
            "dry_run": self.dry_run,
            "repositories_processed": 1,
            "repositories_with_errors": 0,
            "tasks_processed": 0,
            "openagent_executions": 0,
            "prs_created": 0,
            "tasks_completed": 0,
            "task_results": [],
            "success": True,
        }

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

    def _process_single_task(self, repo_dir: Path, task: Task) -> Dict[str, Any]:
        """Process a single task using Ralph loop.

        Args:
            repo_dir: Path to the repository directory
            task: The task to process

        Returns:
            Processing result for this task
        """
        self.logger.info(f"Processing task for: {repo_dir.name}")

        task_id = task.id
        task_title = task.title
        task_body = task.body

        self.logger.info(f"Processing task #{task_id}: {task_title}")

        result = {
            "repository": repo_dir.name,
            "task_id": task_id,
            "task_title": task_title,
            "success": False,
            "openagent_executed": False,
            "openagent_executions": 0,
            "task_completed": False,
            "tasks_completed": 0,
            "pr_created": False,
            "prs_created": 0,
            "error": None,
            "ralph_loops_executed": 0,
            "ralph_steps_completed": 0,
        }

        try:
            branch_name = self.task_source.get_branch_name(task)

            if self.dry_run:
                self.logger.info(f"DRY RUN: Would create branch {branch_name} and execute with Ralph loop")
                result["openagent_executed"] = True
                result["success"] = True
                return result

            self.task_source.on_task_start(task, branch_name)

            branch_created = create_and_checkout_branch(repo_dir, branch_name, base_branch="main")
            if not branch_created:
                error_msg = f"Failed to create branch {branch_name}"
                result["error"] = error_msg
                self.task_source.on_task_failure(task, error_msg)
                return result

            if settings.ralph_enabled:
                ralph_result = self.ralph_executor.execute(
                    repo_dir=repo_dir,
                    issue_number=task_id,
                    issue_title=task_title,
                    issue_body=task_body,
                    comment_texts=task.comments,
                    branch_name=branch_name,
                )
                result["ralph_loops_executed"] = ralph_result.get("loops_executed", 0)
                result["ralph_steps_completed"] = ralph_result.get("steps_completed", 0)
                result["openagent_executions"] = ralph_result.get("loops_executed", 0)

                if not ralph_result.get("success", False):
                    result["error"] = f"Ralph loop failed: {ralph_result.get('error', 'Unknown error')}"

                    if ralph_result.get("max_loops_reached", False):
                        self.logger.warning(f"Ralph loop reached max iterations for task #{task_id}")
                        self.task_source.on_max_iterations_reached(
                            task,
                            ralph_result.get("steps_completed", 0),
                            ralph_result.get("total_steps", 0),
                            ralph_result.get("error", "Unknown error"),
                        )

                    return result

                result["openagent_executed"] = True
            else:
                instructions = self._build_instructions(task_title, task_body, task.comments, branch_name=branch_name)

                openagent_result = execute_with_instructions(
                    instructions,
                    repo_dir,
                    self.agent_args,
                    self.timeout,
                    task_name="implementation",
                )
                result["openagent_executed"] = openagent_result["success"]
                if openagent_result["success"]:
                    result["openagent_executions"] = 1

                if not openagent_result["success"]:
                    cli_tool = get_active_cli_command()
                    error_msg = f"{cli_tool} execution failed: {openagent_result.get('error', 'Unknown error')}"
                    result["error"] = error_msg
                    self.task_source.on_task_failure(task, error_msg)
                    return result

            current_branch = get_current_branch(repo_dir)
            if current_branch in ("main", "master"):
                self.logger.info(f"No changes made for task #{task_id}, closing task")
                self.task_source.on_no_changes(task)

                result["task_completed"] = True
                result["tasks_completed"] = 1

                result["success"] = True
                result["no_changes"] = True
                return result

            push_success, push_message = push_to_remote(repo_dir, remote="origin", branch=current_branch)
            if not push_success:
                error_msg = f"Failed to push branch '{current_branch}': {push_message}"
                result["error"] = error_msg
                self.task_source.on_task_failure(task, error_msg)
                return result

            if settings.ralph_enabled:
                pr_body = self._generate_pr_body_from_task_file(
                    repo_dir=repo_dir,
                    task=task,
                )
            else:
                pr_body = self.task_source.get_default_pr_body(task)

            existing_pr = get_pr_for_branch(repo_dir, current_branch)
            if existing_pr and existing_pr.get("state") == "OPEN":
                result["pr_created"] = True
                result["prs_created"] = 1
                result["pr_url"] = existing_pr.get("url", "")
                self.logger.info(f"PR already exists for branch '{current_branch}': {existing_pr.get('url', 'N/A')}")
            else:
                pr_result = create_pull_request(
                    repo_dir,
                    title=f"Vikunja Task #{task.id}: {task_title}",
                    body=pr_body,
                    head=current_branch,
                    base="main",
                )

                if pr_result:
                    result["pr_created"] = True
                    result["prs_created"] = 1
                    result["pr_url"] = pr_result.get("url", "")
                    self.logger.info(f"Created PR for task #{task_id}: {pr_result.get('url', 'N/A')}")
                else:
                    existing_pr = get_pr_for_branch(repo_dir, current_branch)
                    if existing_pr:
                        result["pr_created"] = True
                        result["prs_created"] = 1
                        result["pr_url"] = existing_pr.get("url", "")
                        self.logger.info(
                            f"Using existing PR for branch '{current_branch}': {existing_pr.get('url', 'N/A')}"
                        )
                    else:
                        error_msg = "Failed to create pull request"
                        result["error"] = error_msg
                        self.task_source.on_task_failure(task, error_msg)
                        return result

            pr_url = result.get("pr_url", "")
            if not pr_url:
                error_msg = f"Task processed but no PR URL available for branch '{current_branch}'"
                result["error"] = error_msg
                self.task_source.on_task_failure(task, error_msg)
                return result

            self.task_source.on_task_complete(task, current_branch, pr_url)
            result["task_completed"] = True
            result["tasks_completed"] = 1

            result["success"] = True

        except Exception as e:
            self.logger.error(f"Error processing task #{task_id}: {str(e)}")
            result["error"] = str(e)
            self.task_source.on_task_failure(task, str(e))

        return result

    def _build_instructions(
        self,
        task_title: str,
        task_body: str,
        comments: List[str],
        branch_name: Optional[str] = None,
    ) -> str:
        """Build the instructions string from task title, body, and comments.

        Args:
            task_title: Task title
            task_body: Task body
            comments: List of comment bodies
            branch_name: Name of the branch already created for this task

        Returns:
            Complete instructions string
        """
        body_text = f"\n{task_body}" if task_body else ""
        comments_text = ""
        if comments:
            comments_text = "\nComments:\n" + "\n".join(f"- {comment}" for comment in comments if comment)

        branch_instruction = ""
        if branch_name:
            branch_instruction = (
                f"You are already on branch '{branch_name}'. "
                f"Work on this branch, implement the changes, commit them, and push.\n"
            )
        else:
            branch_instruction = (
                "Create a new branch that starts with ai/ from base origin/main "
                "if no branch or PR is linked in the issue. "
                "If there is a branch/PR linked in the issue use this branch.\n"
            )

        plan_text = """
Plan:
1. Understand the requirements by analyzing the issue title and description
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
            f"{comments_text}\n"
            f"{plan_text}\n"
            f"Keep your implementation simple. Only implement what is required. "
            f"Check if there are components you can reuse. "
            f"Ensure that 'make test' runs successful. Only push if ALL tests are successful. "
            f"Check if you need to update the README.md."
        )

    def _generate_pr_body_from_task_file(
        self,
        repo_dir: Path,
        task: Task,
    ) -> str:
        """Generate PR description from the refined task file using slopmachine."""
        task_path = self.ralph_executor._get_issue_task_path(repo_dir, task.id)
        default_body = self.task_source.get_default_pr_body(task)

        if not task_path.exists():
            return default_body

        task_content = task_path.read_text()
        instructions = self._build_pr_description_instructions(
            task=task,
            task_content=task_content,
        )

        result = execute_with_instructions(
            instructions,
            repo_dir,
            self.agent_args,
            self.timeout,
            task_name="pr_description",
        )
        if not result.get("success", False):
            return default_body

        generated_body = (result.get("stdout") or "").strip()
        if not generated_body:
            return default_body

        if f"closes #{task.id}" not in generated_body.lower():
            generated_body = f"Closes #{task.id}\n\n{generated_body}"

        return generated_body

    def _build_pr_description_instructions(
        self,
        task: Task,
        task_content: str,
    ) -> str:
        """Build instructions for generating a PR description from task steps."""
        return (
            "Generate a pull request description in markdown.\n"
            f"Task ID: {task.id}\n"
            f"Task title: {task.title}\n"
            f"Task description:\n{task.body}\n\n"
            "Use the completed steps from this task markdown as the source of truth:\n"
            "----- BEGIN TASK -----\n"
            f"{task_content}\n"
            "----- END TASK -----\n\n"
            "Requirements:\n"
            "- Include a concise summary of what changed.\n"
            "- Include completed steps that were implemented.\n"
            "- Include test verification details.\n"
            f"- Include `Closes #{task.id}` in the final PR description.\n"
            "- Return markdown only. Do not modify files.\n"
        )

    def _create_error_result(self, start_time: float, repo_path: Path, error_msg: str) -> Dict[str, Any]:
        """Create an error result dictionary."""
        return {
            "worker_name": "IssueWorker",
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
            "tasks_completed": 0,
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
        cli_tool = get_active_cli_command()
        self.logger.info(
            f"IssueWorker completed. Processed: "
            f"{results['tasks_processed']}, "
            f"{cli_tool} executions: {results['openagent_executions']}, "
            f"PRs created: {results['prs_created']}, "
            f"Tasks completed: {results['tasks_completed']}, "
            f"Errors: {results['repositories_with_errors']}"
        )
