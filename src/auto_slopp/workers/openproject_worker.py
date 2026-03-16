"""OpenProject Worker for processing tasks from OpenProject.

This worker:
1. For each GitHub repository, finds matching OpenProject project by name
2. Creates project if it doesn't exist (configurable)
3. Searches for open tasks assigned to configured user
4. Creates subtasks for the first open task
5. Creates a new branch linked to the task
6. Executes subtasks using the Ralph loop
7. Commits changes and pushes branch
8. Creates PR in GitHub
9. Adds comment to OpenProject task and sets status to in progress
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
    sanitize_branch_name,
)
from auto_slopp.utils.github_operations import create_pull_request, get_pr_for_branch
from auto_slopp.utils.openproject_operations import (
    add_comment_to_work_package,
    create_project,
    create_subtask,
    get_open_work_packages,
    get_project_by_identifier,
    get_project_by_name,
    set_work_package_status,
)
from auto_slopp.utils.ralph import Plan, PlanParser, PlanWriter, RalphLoop, Step
from auto_slopp.worker import Worker
from settings.main import settings


class OpenProjectWorker(Worker):
    """Worker for processing OpenProject tasks.

    This worker matches GitHub repositories to OpenProject projects by name,
    processes open tasks assigned to a configured user, creates subtasks,
    executes them, and creates PRs.
    """

    def __init__(
        self,
        timeout: int | None = None,
        agent_args: Optional[List[str]] = None,
        dry_run: bool = False,
    ):
        """Initialize the OpenProjectWorker.

        Args:
            timeout: Timeout for CLI execution in seconds (default: from settings.slop_timeout)
            agent_args: Additional arguments to pass to the CLI tool
            dry_run: If True, skip actual CLI execution and git operations
        """
        self.timeout = timeout if timeout is not None else settings.slop_timeout
        self.agent_args = agent_args or []
        self.dry_run = dry_run
        self.logger = logging.getLogger("auto_slopp.workers.OpenProjectWorker")

    def run(self, repo_path: Path) -> Dict[str, Any]:
        """Execute the OpenProject task processing workflow for a single repository.

        Args:
            repo_path: Path to the repository directory

        Returns:
            Dictionary containing execution results and statistics
        """
        start_time = self._get_current_time()
        self.logger.info(f"OpenProjectWorker starting with repo_path: {repo_path}")

        if not self._is_configured():
            return self._create_error_result(
                start_time,
                repo_path,
                "OpenProject worker is not configured. Set openproject_url and openproject_api_token.",
            )

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

        project = self._get_or_create_project(repo_path.name)
        if not project:
            self.logger.warning(f"Could not find or create project for {repo_path.name}")
            results["execution_time"] = self._get_elapsed_time(start_time)
            self._log_completion_summary(results)
            return results

        project_id = project.get("id")
        if not project_id:
            results["execution_time"] = self._get_elapsed_time(start_time)
            self._log_completion_summary(results)
            return results

        tasks = get_open_work_packages(
            project_id=project_id,
            assigned_to_user_id=settings.openproject_assigned_user_id,
        )

        if not tasks:
            self.logger.info(f"No open tasks found in project {repo_path.name}")
            results["execution_time"] = self._get_elapsed_time(start_time)
            self._log_completion_summary(results)
            return results

        for task in tasks[:1]:
            task_result = self._process_single_task(repo_path, task, project_id)
            results["task_results"].append(task_result)

            if task_result["success"]:
                results["tasks_processed"] += 1
                results["openagent_executions"] += task_result.get("openagent_executions", 0)
                results["prs_created"] += task_result.get("prs_created", 0)
                results["tasks_updated"] += task_result.get("tasks_updated", 0)
            else:
                self.logger.warning(
                    f"Failed to process task #{task.get('id')}: {task_result.get('error', 'Unknown error')}"
                )

        results["execution_time"] = self._get_elapsed_time(start_time)
        self._log_completion_summary(results)

        return results

    def _is_configured(self) -> bool:
        """Check if OpenProject is properly configured.

        Returns:
            True if configured, False otherwise.
        """
        return bool(settings.openproject_url and settings.openproject_api_token)

    def _get_or_create_project(self, repo_name: str) -> Optional[Dict[str, Any]]:
        """Get or create OpenProject project matching repo name.

        Args:
            repo_name: Name of the repository (used as project identifier)

        Returns:
            Project dictionary or None if failed.
        """
        identifier = settings.openproject_project_prefix + repo_name.lower().replace("-", "_")

        project = get_project_by_identifier(identifier)
        if project:
            return project

        project = get_project_by_name(repo_name)
        if project:
            return project

        if settings.openproject_create_projects:
            self.logger.info(f"Creating OpenProject project for {repo_name}")
            project = create_project(
                name=repo_name,
                identifier=identifier,
                description=f"Auto-created project for repository {repo_name}",
            )
            return project

        self.logger.info(f"Project not found for {repo_name} and auto-creation is disabled")
        return None

    def _create_results_dict(self, start_time: float, repo_path: Path) -> Dict[str, Any]:
        """Create the initial results dictionary."""
        return {
            "worker_name": "OpenProjectWorker",
            "execution_time": 0,
            "timestamp": start_time,
            "repo_path": str(repo_path),
            "dry_run": self.dry_run,
            "repositories_processed": 1,
            "repositories_with_errors": 0,
            "tasks_processed": 0,
            "openagent_executions": 0,
            "prs_created": 0,
            "tasks_updated": 0,
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

    def _process_single_task(
        self,
        repo_dir: Path,
        task: Dict[str, Any],
        project_id: int,
    ) -> Dict[str, Any]:
        """Process a single task from OpenProject.

        Args:
            repo_dir: Path to the repository directory
            task: The task dictionary from OpenProject API
            project_id: OpenProject project ID

        Returns:
            Processing result for this task
        """
        self.logger.info(f"Processing OpenProject task for: {repo_dir.name}")

        raw_task_id = task.get("id")
        if raw_task_id is None:
            return {
                "repository": repo_dir.name,
                "task_id": None,
                "task_subject": task.get("subject", "Unknown"),
                "success": False,
                "error": "Task has no ID",
                "openagent_executed": False,
                "openagent_executions": 0,
                "pr_created": False,
                "prs_created": 0,
                "task_updated": False,
                "tasks_updated": 0,
                "ralph_loops_executed": 0,
                "ralph_steps_completed": 0,
                "subtasks_created": 0,
            }

        task_id: int = raw_task_id
        task_subject = task.get("subject", "Untitled Task")
        task_description = ""
        if task.get("description"):
            task_description = task.get("description", {}).get("raw", "")

        self.logger.info(f"Processing task #{task_id}: {task_subject}")

        result = {
            "repository": repo_dir.name,
            "task_id": task_id,
            "task_subject": task_subject,
            "success": False,
            "openagent_executed": False,
            "openagent_executions": 0,
            "pr_created": False,
            "prs_created": 0,
            "task_updated": False,
            "tasks_updated": 0,
            "error": None,
            "ralph_loops_executed": 0,
            "ralph_steps_completed": 0,
            "subtasks_created": 0,
        }

        try:
            branch_name = f"ai/op-{task_id}-{sanitize_branch_name(task_subject[:30].lower())}"

            if self.dry_run:
                self.logger.info(f"DRY RUN: Would create branch {branch_name} and execute with Ralph loop")
                result["openagent_executed"] = True
                result["success"] = True
                return result

            subtasks = self._create_subtasks_for_task(
                task=task,
                repo_dir=repo_dir,
                project_id=project_id,
            )
            result["subtasks_created"] = len(subtasks)

            branch_created = create_and_checkout_branch(repo_dir, branch_name, base_branch="main")
            if not branch_created:
                result["error"] = f"Failed to create branch {branch_name}"
                return result

            if settings.ralph_enabled and subtasks:
                ralph_result = self._execute_with_ralph_loop(
                    repo_dir=repo_dir,
                    task=task,
                    subtasks=subtasks,
                    branch_name=branch_name,
                    project_id=project_id,
                )
                result["ralph_loops_executed"] = ralph_result.get("loops_executed", 0)
                result["ralph_steps_completed"] = ralph_result.get("steps_completed", 0)
                result["openagent_executions"] = ralph_result.get("loops_executed", 0)

                if not ralph_result.get("success", False):
                    result["error"] = f"Ralph loop failed: {ralph_result.get('error', 'Unknown error')}"
                    return result

                result["openagent_executed"] = True
            else:
                instructions = self._build_instructions(
                    task_subject=task_subject,
                    task_description=task_description,
                    branch_name=branch_name,
                )

                openagent_result = execute_with_instructions(
                    instructions,
                    repo_dir,
                    self.agent_args,
                    self.timeout,
                    task_name="openproject_task",
                )
                result["openagent_executed"] = openagent_result["success"]
                if openagent_result["success"]:
                    result["openagent_executions"] = 1

                if not openagent_result["success"]:
                    cli_tool = get_active_cli_command()
                    result["error"] = f"{cli_tool} execution failed: {openagent_result.get('error', 'Unknown error')}"
                    return result

            current_branch = get_current_branch(repo_dir)
            if current_branch in ("main", "master"):
                self.logger.info(f"No changes made for task #{task_id}, updating task with comment")

                no_changes_comment = (
                    "No changes required for this task. The task has been reviewed and no modifications are needed."
                )
                comment_success = add_comment_to_work_package(task_id, no_changes_comment)
                result["task_commented"] = comment_success

                result["task_updated"] = True
                result["tasks_updated"] = 1

                result["success"] = True
                result["no_changes"] = True
                return result

            pr_body = f"OpenProject Task: #{task_id}\n\n{task_description}"

            existing_pr = get_pr_for_branch(repo_dir, current_branch)
            if existing_pr and existing_pr.get("state") == "OPEN":
                result["pr_created"] = True
                result["pr_url"] = existing_pr.get("url", "")
                self.logger.info(f"PR already exists for branch '{current_branch}': {existing_pr.get('url', 'N/A')}")
            else:
                pr_result = create_pull_request(
                    repo_dir,
                    title=task_subject,
                    body=pr_body,
                    head=current_branch,
                    base="main",
                )

                if pr_result:
                    result["pr_created"] = True
                    result["pr_url"] = pr_result.get("url", "")
                    self.logger.info(f"Created PR for task #{task_id}: {pr_result.get('url', 'N/A')}")
                else:
                    existing_pr = get_pr_for_branch(repo_dir, current_branch)
                    if existing_pr:
                        result["pr_created"] = True
                        result["pr_url"] = existing_pr.get("url", "")
                        self.logger.info(
                            f"Using existing PR for branch '{current_branch}': {existing_pr.get('url', 'N/A')}"
                        )
                    else:
                        result["error"] = "Failed to create pull request"
                        return result

            lock_version = task.get("lockVersion", 1)
            status_updated = set_work_package_status(
                work_package_id=task_id,
                lock_version=lock_version,
                status_id=settings.openproject_in_progress_status_id,
            )
            result["task_status_updated"] = status_updated

            pr_url = result.get("pr_url", "")
            comment = f"Work completed by PR: {pr_url}\n\nThe task has been processed and is now in progress."
            comment_success = add_comment_to_work_package(task_id, comment)
            result["task_commented"] = comment_success

            if status_updated or comment_success:
                result["task_updated"] = True
                result["tasks_updated"] = 1

            result["success"] = True

        except Exception as e:
            self.logger.error(f"Error processing task #{task_id}: {str(e)}")
            result["error"] = str(e)

        return result

    def _create_subtasks_for_task(
        self,
        task: Dict[str, Any],
        repo_dir: Path,
        project_id: int,
    ) -> List[Dict[str, Any]]:
        """Create subtasks for a parent task using CLI analysis.

        Args:
            task: Parent task dictionary
            repo_dir: Repository directory path
            project_id: OpenProject project ID

        Returns:
            List of created subtask dictionaries.
        """
        task_id: int = task.get("id", 0)
        if task_id == 0:
            self.logger.warning("Task has no ID, cannot create subtasks")
            return []

        task_subject = task.get("subject", "")
        task_description = ""
        if task.get("description"):
            task_description = task.get("description", {}).get("raw", "")

        subtask_descriptions = self._analyze_and_generate_subtasks(
            task_subject=task_subject,
            task_description=task_description,
            repo_dir=repo_dir,
        )

        created_subtasks = []
        for i, subtask_desc in enumerate(subtask_descriptions, 1):
            subtask = create_subtask(
                parent_work_package_id=task_id,
                project_id=project_id,
                subject=f"Subtask {i}: {subtask_desc[:50]}",
                description=subtask_desc,
            )
            if subtask:
                created_subtasks.append(subtask)
                self.logger.info(f"Created subtask: {subtask.get('subject')}")

        return created_subtasks

    def _analyze_and_generate_subtasks(
        self,
        task_subject: str,
        task_description: str,
        repo_dir: Path,
    ) -> List[str]:
        """Analyze task and generate subtask descriptions using CLI.

        Args:
            task_subject: Task subject/title
            task_description: Task description
            repo_dir: Repository directory for context

        Returns:
            List of subtask descriptions.
        """
        default_subtasks = self._get_default_subtasks(task_subject)

        analysis_instructions = f"""Analyze this OpenProject task and generate 3-7 specific subtasks:

Task Subject: {task_subject}
Task Description: {task_description}

Generate subtasks that:
1. Are specific and actionable
2. Include mention of reusable components from the codebase
3. Follow the standard development workflow
4. Can be executed sequentially

Format: Return ONLY a numbered list of subtask descriptions, one per line.
Example:
1. Analyze the existing implementation
2. Identify reusable components
3. Implement the core functionality
4. Write tests
5. Update documentation

If you cannot analyze the task, return the default subtasks."""

        try:
            result = execute_with_instructions(
                instructions=analysis_instructions,
                work_dir=repo_dir,
                agent_args=self.agent_args,
                timeout=300,
                task_name="openproject_subtask_generation",
            )

            if result.get("success") and result.get("stdout"):
                subtasks = self._parse_subtasks_from_output(result["stdout"])
                if subtasks:
                    return subtasks
        except Exception as e:
            self.logger.warning(f"Failed to generate subtasks via CLI: {e}")

        return default_subtasks

    def _parse_subtasks_from_output(self, output: str) -> List[str]:
        """Parse subtask descriptions from CLI output.

        Args:
            output: Raw CLI output

        Returns:
            List of subtask descriptions.
        """
        subtasks = []
        for line in output.strip().split("\n"):
            line = line.strip()
            if not line:
                continue

            if line[0].isdigit() and "." in line:
                parts = line.split(".", 1)
                if len(parts) > 1:
                    subtask = parts[1].strip()
                    if subtask:
                        subtasks.append(subtask)

            elif line.startswith("- "):
                subtask = line[2:].strip()
                if subtask:
                    subtasks.append(subtask)

        return subtasks if subtasks else []

    def _get_default_subtasks(self, task_subject: str) -> List[str]:
        """Get default subtask descriptions based on task subject.

        Args:
            task_subject: Task subject for context

        Returns:
            List of default subtask descriptions.
        """
        return [
            "Understand the requirements and analyze the task description",
            "Explore the codebase to understand the current implementation",
            "Identify components that can be reused",
            "Design a solution that is simple and focused",
            "Write or update tests for the changes",
            "Implement the solution",
            "Run tests and lint checks, commit and push changes",
        ]

    def _execute_with_ralph_loop(
        self,
        repo_dir: Path,
        task: Dict[str, Any],
        subtasks: List[Dict[str, Any]],
        branch_name: str,
        project_id: int,
    ) -> Dict[str, Any]:
        """Execute task processing using Ralph loop with subtasks as steps.

        Args:
            repo_dir: Path to the repository directory
            task: Parent task dictionary
            subtasks: List of subtask dictionaries
            branch_name: Branch name
            project_id: OpenProject project ID

        Returns:
            Result dictionary from Ralph loop execution.
        """
        task_id = task.get("id")
        plan_path = repo_dir / ".ralph" / f"op-task-{task_id}-plan.md"

        plan = self._create_task_plan(
            plan_path=plan_path,
            task=task,
            subtasks=subtasks,
            branch_name=branch_name,
        )

        def step_executor(step: Step, current_plan: Plan) -> Dict[str, Any]:
            return self._execute_step(
                step=step,
                plan=current_plan,
                repo_dir=repo_dir,
                task=task,
                branch_name=branch_name,
            )

        ralph_loop = RalphLoop(
            plan_path=plan_path,
            max_loops=settings.ralph_max_loops,
            step_executor=step_executor,
        )
        ralph_loop.plan = plan

        return ralph_loop.run()

    def _create_task_plan(
        self,
        plan_path: Path,
        task: Dict[str, Any],
        subtasks: List[Dict[str, Any]],
        branch_name: str,
    ) -> Plan:
        """Create a plan file for the task based on subtasks.

        Args:
            plan_path: Path to save the plan file
            task: Parent task dictionary
            subtasks: List of subtask dictionaries
            branch_name: Branch name

        Returns:
            Created Plan object.
        """
        task_subject = task.get("subject", "Untitled Task")
        task_description = ""
        if task.get("description"):
            task_description = task.get("description", {}).get("raw", "")

        description = f"Branch: {branch_name}\n\n{task_description}"

        step_descriptions = []
        for subtask in subtasks:
            subject = subtask.get("subject", "")
            desc = subtask.get("description", {}).get("raw", "")
            step_descriptions.append(f"{subject}: {desc}" if desc else subject)

        steps = [Step(number=i + 1, description=desc, is_closed=False) for i, desc in enumerate(step_descriptions)]

        plan = Plan(
            title=f"OpenProject Task Plan: {task_subject}",
            description=description,
            steps=steps,
        )

        PlanWriter.write_file(plan, plan_path)
        self.logger.info(f"Created plan file: {plan_path}")

        return plan

    def _execute_step(
        self,
        step: Step,
        plan: Plan,
        repo_dir: Path,
        task: Dict[str, Any],
        branch_name: str,
    ) -> Dict[str, Any]:
        """Execute a single step from the plan.

        Args:
            step: Step to execute
            plan: Current plan
            repo_dir: Repository directory
            task: Parent task dictionary
            branch_name: Branch name

        Returns:
            Execution result dictionary.
        """
        step_instructions = self._build_step_instructions(
            step=step,
            plan=plan,
            task=task,
            branch_name=branch_name,
        )

        self.logger.info(f"Executing step {step.number}: {step.description}")

        result = execute_with_instructions(
            step_instructions,
            repo_dir,
            self.agent_args,
            self.timeout,
            task_name="openproject_task",
        )

        if result.get("success", False):
            self.logger.info(f"Step {step.number} completed successfully")
        else:
            self.logger.warning(f"Step {step.number} failed: {result.get('error', 'Unknown error')}")

        return result

    def _build_step_instructions(
        self,
        step: Step,
        plan: Plan,
        task: Dict[str, Any],
        branch_name: str,
    ) -> str:
        """Build instructions for a single step.

        Args:
            step: Step to build instructions for
            plan: Current plan
            task: Parent task dictionary
            branch_name: Branch name

        Returns:
            Instructions string for the step.
        """
        task_subject = task.get("subject", "")
        task_description = ""
        if task.get("description"):
            task_description = task.get("description", {}).get("raw", "")

        body_text = f"\n{task_description}" if task_description else ""
        progress_info = self._build_progress_info(plan)

        return (
            f"You are already on branch '{branch_name}'. "
            f"Work on this branch, implement the changes, commit them, and push.\n"
            f"Implement the following:\n"
            f"Title: {task_subject}\n"
            f"Description:{body_text}\n\n"
            f"Current Progress:\n{progress_info}\n\n"
            f"Your current task is Step {step.number}: {step.description}\n\n"
            f"Focus only on completing this step. Once done, mark it as complete in your work. "
            f"Keep your implementation simple. Only implement what is required. "
            f"Check if there are components you can reuse. "
            f"Ensure that 'make test' runs successful. Only push if ALL tests are successful. "
            f"Check if you need to update the README.md."
        )

    def _build_progress_info(self, plan: Plan) -> str:
        """Build progress information string.

        Args:
            plan: Current plan

        Returns:
            Progress information string.
        """
        lines = []
        for step in plan.steps:
            status = "✓" if step.is_closed else "○"
            lines.append(f"{status} Step {step.number}: {step.description}")
        return "\n".join(lines)

    def _build_instructions(
        self,
        task_subject: str,
        task_description: str,
        branch_name: Optional[str] = None,
    ) -> str:
        """Build the instructions string from task subject and description.

        Args:
            task_subject: Task subject/title
            task_description: Task description
            branch_name: Name of the branch already created for this task

        Returns:
            Complete instructions string.
        """
        body_text = f"\n{task_description}" if task_description else ""

        branch_instruction = ""
        if branch_name:
            branch_instruction = (
                f"You are already on branch '{branch_name}'. "
                f"Work on this branch, implement the changes, commit them, and push.\n"
            )
        else:
            branch_instruction = "Create a new branch that starts with ai/ from base origin/main.\n"

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
            f"Title: {task_subject}\n"
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
            "worker_name": "OpenProjectWorker",
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
            "tasks_updated": 0,
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
            f"OpenProjectWorker completed. Processed: "
            f"{results['tasks_processed']}, "
            f"{cli_tool} executions: {results['openagent_executions']}, "
            f"PRs created: {results['prs_created']}, "
            f"Tasks updated: {results['tasks_updated']}, "
            f"Errors: {results['repositories_with_errors']}"
        )
