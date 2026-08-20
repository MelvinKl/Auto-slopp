"""Unified Issue Worker for processing tasks from different sources.

This worker provides a common implementation for processing tasks from
various sources (GitHub Issues, Vikunja, etc.) using the Ralph loop
for step-based execution.
"""

import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from auto_slopp.constants import UNAVAILABILITY_PATTERNS
from auto_slopp.utils.cli_executor import (
    _cli_states,
    execute_with_instructions,
    get_active_cli_command,
    run_cli_executor,
)
from auto_slopp.utils.git_operations import (
    checkout_branch_resilient,
    commit_and_push_changes,
    create_and_checkout_branch,
    delete_branch,
    ensure_ralph_in_gitignore,
    get_commits_ahead_of_branch,
    get_current_branch,
    has_changes,
    push_to_remote,
)
from auto_slopp.utils.github_operations import (
    create_pull_request,
    get_pr_files,
    get_pr_for_branch,
    remove_label_from_issue,
    submit_pr_review,
)
from auto_slopp.utils.linking import ensure_issue_link_in_pr_body
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

    # Shared source of truth for LLM unavailability detection.
    UNAVAILABILITY_PATTERNS: tuple[str, ...] = UNAVAILABILITY_PATTERNS

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

            if task_result.get("skipped"):
                results["tasks_skipped"] += 1
                self.logger.info(f"Task #{task.id} skipped: {task_result.get('skip_reason', 'Unknown')}")
            elif task_result["success"]:
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
            "tasks_skipped": 0,
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

    def _is_llm_unavailable(self, error_msg: str) -> bool:
        """Check if the error indicates LLM unavailability.

        Uses specific patterns to avoid false positives from unrelated errors.

        Args:
            error_msg: The error message to check

        Returns:
            True if the error indicates LLM is unavailable, False otherwise
        """
        error_lower = error_msg.lower()
        error_indicates_unavailable = any(pattern in error_lower for pattern in self.UNAVAILABILITY_PATTERNS)
        # Also check if all CLI configurations are inactive (in cooldown) and cooldown hasn't expired
        all_clis_inactive = False
        cli_configs = settings.cli_configurations
        if cli_configs and _cli_states:
            now = time.time()
            num_configs = len(cli_configs)
            if num_configs > 0:
                all_clis_inactive = True
                for i in range(num_configs):
                    state = _cli_states.get(i, {"active": True, "cooldown_until": 0.0})
                    # CLI is available if active, or if inactive but cooldown has expired
                    if state.get("active", True) or now >= state.get("cooldown_until", 0.0):
                        all_clis_inactive = False
                        break

        return error_indicates_unavailable or all_clis_inactive

    def _is_permanent_error(self, error_msg: str) -> bool:
        """Check if the error indicates a permanent configuration/setup issue.

        These errors require human intervention and should not be retried automatically.

        Args:
            error_msg: The error message to check

        Returns:
            True if the error indicates a permanent issue, False otherwise
        """
        error_lower = error_msg.lower()
        permanent_indicators = (
            "no cli configuration" in error_lower
            or "no active cli" in error_lower
            or "permission denied" in error_lower
            or "authentication failed" in error_lower
            or "unauthorized" in error_lower
            or "access denied" in error_lower
            or "forbidden" in error_lower
            or "invalid token" in error_lower
            or "token expired" in error_lower
            or "not configured" in error_lower
            or "configuration error" in error_lower
            or "missing configuration" in error_lower
        )
        return permanent_indicators

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
                error_msg = f"Failed to create branch '{branch_name}' for task #{task_id}"
                self.logger.error(error_msg)
                result["error"] = error_msg
                self.task_source.on_task_failure(task, error_msg)
                return result

            # Ensure .ralph is in .gitignore before Ralph execution
            if not ensure_ralph_in_gitignore(repo_dir):
                self.logger.warning(
                    f"Failed to ensure .ralph in .gitignore for {repo_dir.name}; "
                    f"generated .ralph files may be committed to the repository"
                )

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
                    ralph_error = f"Ralph loop failed: {ralph_result.get('error', 'Unknown error')}"
                    result["error"] = ralph_error

                    if ralph_result.get("max_loops_reached", False):
                        # Distinguish between genuine iteration exhaustion and
                        # LLM unavailability during the loop. The latter should
                        # trigger a skip (retry later), not a permanent failure.
                        if self.ralph_executor._is_llm_unavailable():
                            self.logger.warning(
                                f"Ralph loop hit max iterations but LLM was unavailable "
                                f"during execution – skipping task #{task_id} for retry"
                            )
                            self.task_source.on_skip(
                                task,
                                ralph_result.get("error", "LLM unavailable during Ralph loop"),
                            )
                            result["success"] = True
                            result["skipped"] = True
                            result["skip_reason"] = ralph_result.get("error", "LLM unavailable during Ralph loop")
                        else:
                            self.logger.warning(f"Ralph loop reached max iterations for task #{task_id}")
                            self.task_source.on_max_iterations_reached(
                                task,
                                ralph_result.get("steps_completed", 0),
                                ralph_result.get("total_steps", 0),
                                ralph_result.get("error", "Unknown error"),
                            )
                    elif self._is_llm_unavailable(ralph_error):
                        self.logger.warning(f"LLM unavailable, skipping task #{task_id}")
                        self.task_source.on_skip(task, ralph_error)
                        result["success"] = True
                        result["skipped"] = True
                        result["skip_reason"] = ralph_error
                        return result
                    elif self._is_permanent_error(ralph_error):
                        self.logger.error(f"Permanent error detected for task #{task_id}: {ralph_error}")
                        self.task_source.on_task_failure(task, ralph_error)
                    else:
                        # Non-max-loops-reached Ralph failure – check for LLM
                        # unavailability before falling back to permanent failure.
                        if self._is_llm_unavailable(ralph_error):
                            self.logger.warning(
                                f"Ralph loop failed but LLM appears unavailable "
                                f"(refinement/parse phase) – skipping task #{task_id} for retry"
                            )
                            self.task_source.on_skip(task, ralph_error)
                            result["success"] = True
                            result["skipped"] = True
                            result["skip_reason"] = ralph_error
                        elif self._is_permanent_error(ralph_error):
                            self.logger.error(f"Permanent error detected for task #{task_id}: {ralph_error}")
                            self.task_source.on_task_failure(task, ralph_error)
                        else:
                            self.logger.error(f"Ralph loop failed for task #{task_id}: {ralph_error}")
                            self.task_source.on_task_failure(task, ralph_error)

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
                    if has_changes(repo_dir):
                        self.logger.info(f"Committing changes after execution for task #{task_id}")
                        commit_and_push_changes(
                            repo_dir,
                            f"Task #{task_id}: commit changes after execution",
                            push_if_remote=False,
                        )

                if not openagent_result["success"]:
                    cli_tool = get_active_cli_command()
                    error_msg = f"{cli_tool} execution failed: {openagent_result.get('error', 'Unknown error')}"
                    result["error"] = error_msg
                    if self._is_llm_unavailable(error_msg):
                        self.logger.warning(f"LLM unavailable, skipping task #{task_id}")
                        self.task_source.on_skip(task, error_msg)
                        result["success"] = True
                        result["skipped"] = True
                        result["skip_reason"] = error_msg
                        return result
                    elif self._is_permanent_error(error_msg):
                        self.logger.error(f"Permanent error detected for task #{task_id}: {error_msg}")
                        self.task_source.on_task_failure(task, error_msg)
                    else:
                        self.task_source.on_task_failure(task, error_msg)
                    return result

            current_branch = get_current_branch(repo_dir)
            if current_branch in ("main", "master"):
                if self._is_llm_unavailable(""):
                    self.logger.warning(f"LLM unavailable, skipping task #{task_id}")
                    self.task_source.on_skip(task, "LLM unavailable - no changes made")
                    result["success"] = True
                    result["skipped"] = True
                    result["skip_reason"] = "LLM unavailable - no changes made"
                    return result

                self.logger.info(f"No changes made for task #{task_id}, closing task")
                self.task_source.on_no_changes(task)

                result["task_completed"] = True
                result["tasks_completed"] = 1

                result["success"] = True
                result["no_changes"] = True
                return result

            # Check if there are any commits ahead of main (regardless of uncommitted changes).
            # This is the authoritative check: if the branch has commits ahead of main, work was done
            # and we should proceed to push/create PR. Only uncommitted changes are checked below
            # to ensure everything is committed before proceeding.
            ahead_count = get_commits_ahead_of_branch(repo_dir, base_branch="main")
            if ahead_count == 0:
                if self._is_llm_unavailable(""):
                    self.logger.warning(f"LLM unavailable, skipping task #{task_id}")
                    self.task_source.on_skip(task, "LLM unavailable - no changes made")
                    result["success"] = True
                    result["skipped"] = True
                    result["skip_reason"] = "LLM unavailable - no commits ahead"
                    return result

                self.logger.info(f"No commits ahead of main for task #{task_id}, closing issue")
                # Clean up the branch since no work was done
                try:
                    checkout_branch_resilient(repo_dir=repo_dir, branch="main", fetch_first=False, timeout=10)
                    delete_branch(repo_dir, current_branch)
                except Exception as e:
                    self.logger.warning(f"Failed to clean up branch {current_branch}: {e}")
                self.task_source.on_no_changes(task)
                result["task_completed"] = True
                result["tasks_completed"] = 1
                result["success"] = True
                result["no_changes"] = True
                return result

            # There are commits ahead of main - commit any remaining uncommitted changes and push
            changes_present = has_changes(repo_dir)
            if changes_present:
                self.logger.info(f"Committing outstanding changes before push for task #{task_id}")
                commit_success, _ = commit_and_push_changes(
                    repo_dir, f"Task #{task_id}: commit outstanding changes before push", push_if_remote=False
                )
                if not commit_success:
                    error_msg = f"Failed to commit outstanding changes for task #{task_id}"
                    self.logger.error(error_msg)
                    result["error"] = error_msg
                    self.task_source.on_task_failure(task, error_msg)
                    return result

            push_success, push_message = push_to_remote(repo_dir, remote="origin", branch=current_branch)
            if not push_success:
                error_msg = f"Failed to push branch '{current_branch}' for task #{task_id}: {push_message}"
                self.logger.error(error_msg)
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
                    title=self.task_source.get_pr_title(task),
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
                    error_msg = f"Failed to create pull request for task #{task_id} on branch '{current_branch}'"
                    self.logger.error(error_msg)
                    result["error"] = error_msg
                    self.task_source.on_task_failure(task, error_msg)
                    return result

            pr_url = result.get("pr_url", "")
            if not pr_url:
                error_msg = f"Task #{task_id} processed but no PR URL available for branch '{current_branch}'"
                self.logger.error(error_msg)
                result["error"] = error_msg
                self.task_source.on_task_failure(task, error_msg)
                return result

            # Check if we should skip the PR review (e.g., in dry run mode)
            if self.dry_run:
                self.logger.info(f"DRY RUN: Would perform PR review for PR {pr_url}")
                self.task_source.on_task_complete(task, current_branch, pr_url)
                result["task_completed"] = True
                result["tasks_completed"] = 1
                result["success"] = True
                return result

            # PR Review Loop: Review PR, fix issues, and re-review until clean
            # This loop counts towards the overall iterations for the issue
            max_pr_review_iterations = getattr(settings, "github_issue_pr_review_max_iterations", 5)
            if not isinstance(max_pr_review_iterations, int):
                max_pr_review_iterations = 5
            pr_review_iteration = 0
            pr_number = int(pr_url.split("/")[-1])

            while pr_review_iteration < max_pr_review_iterations:
                pr_review_iteration += 1
                self.logger.info(
                    f"PR review iteration {pr_review_iteration}/{max_pr_review_iterations} for PR #{pr_number}"
                )

                # Perform PR review to check for findings
                has_findings, review_comments, finding_lines = self._review_pull_request(
                    repo_dir, pr_url, task.title, task.body
                )

                # Submit the review to the PR itself (NOT to the GitHub issue)
                try:
                    pr_review_success = submit_pr_review(repo_dir, pr_number, review_comments, event="COMMENT")
                    if pr_review_success:
                        self.logger.info(f"Submitted PR review to PR #{pr_number}")
                    else:
                        self.logger.warning(f"Failed to submit PR review to PR #{pr_number}")
                except Exception as e:
                    self.logger.warning(f"Failed to submit PR review: {e}")

                if not has_findings:
                    # No findings (only praise/questions) - proceed with normal completion
                    self.logger.info(
                        f"PR review completed with no actionable findings for task #{task_id} "
                        f"after {pr_review_iteration} iteration(s)"
                    )
                    self.task_source.on_task_complete(task, current_branch, pr_url)
                    # Remove the automatic work label to prevent re-processing
                    label_removed = remove_label_from_issue(
                        repo_dir, task.id, settings.github_issue_worker_required_label
                    )
                    if label_removed:
                        self.logger.info(f"Removed automatic work label from issue #{task.id}")
                    else:
                        self.logger.warning(f"Failed to remove automatic work label from issue #{task.id}")

                    result["task_completed"] = True
                    result["tasks_completed"] = 1
                    result["success"] = True
                    result["label_removed"] = True
                    result["pr_review_iterations"] = pr_review_iteration
                    return result

                # Findings found - fix them by calling CLI tool with the PR review results
                self.logger.info(f"PR review found {len(finding_lines)} issue(s) requiring fixes for task #{task_id}")

                # Build instructions for the CLI tool to fix the PR review issues
                fix_instructions = self._build_pr_fix_instructions(
                    pr_number=pr_number,
                    pr_url=pr_url,
                    finding_lines=finding_lines,
                )

                # Execute CLI to fix the issues found in PR review
                fix_result = run_cli_executor(
                    additional_instructions=fix_instructions,
                    working_directory=repo_dir,
                    timeout=self.timeout,
                    capture_output=True,
                    task_name="pr_review_fix",
                )

                if not fix_result.get("success", False):
                    self.logger.error(
                        f"Failed to fix PR review issues for task #{task_id}: "
                        f"{fix_result.get('error', 'Unknown error')}"
                    )
                    # Mark as successful but not completed - issue stays open for next task iteration
                    result["task_completed"] = False
                    result["tasks_completed"] = 0
                    result["success"] = True
                    result["pr_review_done"] = True
                    result["pr_review_iterations"] = pr_review_iteration
                    return result

                # Commit and push the fixes
                if has_changes(repo_dir):
                    commit_success, _ = commit_and_push_changes(
                        repo_dir,
                        f"Task #{task_id}: fix PR review issues (iteration {pr_review_iteration})",
                        push_if_remote=False,
                    )
                    if not commit_success:
                        self.logger.error(f"Failed to commit PR review fixes for task #{task_id}")
                        result["task_completed"] = False
                        result["tasks_completed"] = 0
                        result["success"] = True
                        result["pr_review_done"] = True
                        result["pr_review_iterations"] = pr_review_iteration
                        return result

                    # Push the fixes to the PR branch
                    push_success, push_message = push_to_remote(repo_dir, remote="origin", branch=current_branch)
                    if not push_success:
                        self.logger.error(f"Failed to push PR review fixes for task #{task_id}: {push_message}")
                        result["task_completed"] = False
                        result["tasks_completed"] = 0
                        result["success"] = True
                        result["pr_review_done"] = True
                        result["pr_review_iterations"] = pr_review_iteration
                        return result

                # Continue loop to re-review the PR
                self.logger.info(f"PR review fixes applied, re-reviewing PR #{pr_number}")

            # Max PR review iterations reached
            self.logger.warning(f"PR review reached max iterations ({max_pr_review_iterations}) for task #{task_id}")
            # Mark as successful but not completed - issue stays open for next task iteration
            result["task_completed"] = False
            result["tasks_completed"] = 0
            result["success"] = True
            result["pr_review_done"] = True
            result["pr_review_iterations"] = pr_review_iteration

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
            f"Ensure that 'make test' runs successful. Push after you are done. "
            f"Check if you need to update the README.md and any documentation in docs/ if it exists."
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

        return ensure_issue_link_in_pr_body(generated_body, task.id)

    def _build_review_instructions(self, title: str, body: str, diff: str) -> str:
        """Build instructions for the CLI tool to review a PR.

        Args:
            title: PR title
            body: PR body description
            diff: PR diff content

        Returns:
            Instructions string for the CLI tool.
        """
        body_section = f"\n{body}" if body else ""
        min_comments = settings.pr_review_worker_min_comments
        max_comments = settings.pr_review_worker_max_comments

        return (
            f"You are a code review assistant. Review the following pull request:\n"
            f"Title: {title}\n"
            f"Description:{body_section}\n\n"
            f"Diff:\n{diff}\n\n"
            f"Provide a review using conventional comments format. "
            f"Generate between {min_comments} and {max_comments} comments. "
            f"Each comment should be on a new line and start with one of the following:\n"
            f"- 'suggestion:' for suggesting improvements\n"
            f"- 'issue:' for pointing out problems\n"
            f"- 'nit:' for nitpicky comments\n"
            f"- 'question:' for asking questions\n"
            f"- 'praise:' for positive feedback\n"
            f"- 'chore:' for chores or maintenance suggestions\n"
            f"Only output the comments, one per line, without any additional text or explanation."
        )

    def _build_pr_fix_instructions(
        self,
        pr_number: int,
        pr_url: str,
        finding_lines: List[str],
    ) -> str:
        """Build instructions for the CLI tool to fix PR review issues.

        Args:
            pr_number: Pull request number
            pr_url: URL of the pull request
            finding_lines: List of finding lines from the PR review (issue:, suggestion:, nit:, chore:)

        Returns:
            Instructions string for the CLI tool to fix the issues.
        """
        findings_text = "\n".join(f"- {line}" for line in finding_lines)

        return (
            f"Fix the issues found during the PR review for PR #{pr_number} ({pr_url}).\n\n"
            f"The PR review found the following issues that need to be fixed:\n\n"
            f"{findings_text}\n\n"
            f"Please fix ALL of these issues in the code. Make the necessary changes to the codebase, "
            f"commit them with a clear commit message, and push to the current branch.\n\n"
            f"After fixing, ensure that 'make lint' and 'make test' both pass successfully."
        )

    def _review_pull_request(self, repo_dir: Path, pr_url: str, title: str, body: str) -> tuple[bool, str, List[str]]:
        """Review a pull request and check for actionable findings.

        Args:
            repo_dir: Path to the repository directory
            pr_url: URL of the pull request to review
            title: Title of the pull request
            body: Body/description of the pull request

        Returns:
            Tuple of (has_findings, comment_string, finding_lines) where:
            - has_findings: bool, True if actionable findings were found
            - comment_string: string to post as a review comment on the PR
            - finding_lines: list of strings, each line that is a finding (issue:, suggestion:, nit:, chore:)
        """
        try:
            # Extract PR number from URL
            # PR URL format: https://github.com/owner/repo/pull/123
            pr_number = int(pr_url.split("/")[-1])
        except (ValueError, IndexError):  # fmt: skip
            self.logger.error(f"Could not extract PR number from URL: {pr_url}")
            return False, "Failed to extract PR number from URL.", []

        # Get the PR diff/files
        try:
            diff = get_pr_files(repo_dir, pr_number)
        except Exception as e:
            self.logger.error(f"Failed to get files for PR #{pr_number}: {str(e)}")
            return False, f"Failed to get PR diff: {str(e)}", []

        # Check if diff is empty
        if not diff.strip():
            self.logger.warning(f"No changes found in PR #{pr_number} to review")
            return False, "No changes found in the pull request to review.", []

        # Prepare instructions for the CLI tool to review the PR
        instructions = self._build_review_instructions(title, body, diff)

        # Run the CLI tool to generate review comments
        review_result = run_cli_executor(
            additional_instructions=instructions,
            working_directory=repo_dir,
            timeout=self.timeout,
            capture_output=True,
            task_name="pr_review",
        )

        if not review_result.get("success", False):
            error_msg = f"CLI tool failed to review PR #{pr_number}: " f"{review_result.get('error', 'Unknown error')}"
            self.logger.error(error_msg)
            return [], error_msg

        # Extract the review comments from the stdout
        review_output = (review_result.get("stdout") or "").strip()
        if not review_output:
            self.logger.warning(f"No review output generated for PR #{pr_number}")
            return [], "No review feedback was generated."

        # Parse the review output to check for actionable findings
        # Findings are comments that start with 'issue:', 'suggestion:', 'nit:', or 'chore:'
        # (excluding 'question:' and 'praise:' as per requirements)
        finding_prefixes = ("issue:", "suggestion:", "nit:", "chore:")
        lines = [line.strip() for line in review_output.split("\n") if line.strip()]
        finding_lines = [line for line in lines if any(line.lower().startswith(p) for p in finding_prefixes)]

        if finding_lines:
            # Format the findings for the PR review comment
            findings_text = "\n".join(finding_lines)
            comment_string = f"PR review found the following issues that need attention:\n\n{findings_text}"
        else:
            # No actionable findings (only praise/questions or no valid comments)
            comment_string = (
                "PR review completed - no actionable issues found (only praise/questions or minor comments)."
            )

        has_findings = len(finding_lines) > 0
        return has_findings, comment_string, finding_lines

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
            f"Skipped: {results['tasks_skipped']}, "
            f"{cli_tool} executions: {results['openagent_executions']}, "
            f"PRs created: {results['prs_created']}, "
            f"Tasks completed: {results['tasks_completed']}, "
            f"Errors: {results['repositories_with_errors']}"
        )
