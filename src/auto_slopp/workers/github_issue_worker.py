"""GitHub Issue Worker for processing open issues as instructions.

This worker:
1. Searches each repository for open issues on GitHub
2. Uses issue title/body as instructions
3. Creates a new branch starting with ai/
4. Creates a plan file with steps and executes them using the Ralph loop
5. Creates a PR and closes the issue
"""

import logging
import re
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
    delete_branch,
    get_current_branch,
    has_changes,
    push_to_remote,
    sanitize_branch_name,
)
from auto_slopp.utils.github_operations import (
    close_issue,
    comment_on_issue,
    create_pull_request,
    get_issue_comments,
    get_open_issues,
    get_pr_for_branch,
)
from auto_slopp.utils.ralph import (
    Plan,
    PlanParser,
    Step,
)
from auto_slopp.worker import Worker
from settings.main import settings


def extract_author_login(issue: Dict[str, Any]) -> str:
    """Extract author login from an issue dictionary.

    Args:
        issue: The issue dictionary from GitHub API

    Returns:
        Author login string or empty string if not available
    """
    author = issue.get("author", {})
    return author.get("login", "") if author else ""


def extract_label_names(issue: Dict[str, Any]) -> List[str]:
    """Extract label names from an issue dictionary.

    Args:
        issue: The issue dictionary from GitHub API

    Returns:
        List of label names
    """
    labels = issue.get("labels", [])
    return [label.get("name", "") for label in labels]


def build_branch_instruction(branch_name: Optional[str] = None) -> str:
    """Build the branch instruction prefix for CLI commands.

    Args:
        branch_name: Name of the branch already created for this issue

    Returns:
        Branch instruction string
    """
    if branch_name:
        return f"You are already on branch '{branch_name}'. Work on this branch, implement the changes, commit them, and push.\n"
    return (
        "Create a new branch that starts with ai/ from base origin/main "
        "if no branch or PR is linked in the issue. "
        "If there is a branch/PR linked in the issue use this branch.\n"
    )


def build_comments_section(comment_texts: List[str]) -> str:
    """Build the comments section for instructions.

    Args:
        comment_texts: List of comment bodies

    Returns:
        Formatted comments section or empty string
    """
    if not comment_texts:
        return ""
    return "\nComments:\n" + "\n".join(f"- {comment}" for comment in comment_texts if comment) + "\n"


def build_body_section(body: str) -> str:
    """Build the body section for instructions.

    Args:
        body: The body text

    Returns:
        Formatted body section or empty string
    """
    return f"\n{body}" if body else ""


def build_task_directive() -> str:
    """Build the standard task directive for instructions.

    Returns:
        Standard task directive string
    """
    return (
        "Focus only on completing this step. Once done, mark it as complete in your work. "
        "Keep your implementation simple. Only implement what is required. "
        "Check if there are components you can reuse. "
        "Ensure that 'make test' runs successful. Only push if ALL tests are successful. "
        "Check if you need to update the README.md."
    )


def build_plan_text() -> str:
    """Build the standard plan text for instructions.

    Returns:
        Standard plan text
    """
    return """
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


class GitHubIssueWorker(Worker):
    """Worker for processing GitHub issues as instructions.

    This worker searches each repository for open issues on GitHub,
    uses the issue title and body as instructions for the configured CLI tool,
    creates a new branch, executes the instructions, and creates a PR.
    """

    def __init__(
        self,
        timeout: int | None = None,
        agent_args: Optional[List[str]] = None,
        dry_run: bool = False,
    ):
        """Initialize the GitHubIssueWorker.

        Args:
            timeout: Timeout for CLI execution in seconds (default: from settings.slop_timeout)
            agent_args: Additional arguments to pass to the CLI tool
            dry_run: If True, skip actual CLI execution and git operations
        """
        self.timeout = timeout if timeout is not None else settings.slop_timeout
        self.agent_args = agent_args or []
        self.dry_run = dry_run
        self.logger = logging.getLogger("auto_slopp.workers.GitHubIssueWorker")

    def run(self, repo_path: Path) -> Dict[str, Any]:
        """Execute the GitHub issue processing workflow for a single repository.

        Args:
            repo_path: Path to the repository directory

        Returns:
            Dictionary containing execution results and statistics
        """
        start_time = self._get_current_time()
        self.logger.info(f"GitHubIssueWorker starting with repo_path: {repo_path}")

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

        issues = get_open_issues(repo_path)

        if not issues:
            self.logger.info(f"No open issues found in {repo_path.name}")
            results["execution_time"] = self._get_elapsed_time(start_time)
            self._log_completion_summary(results)
            return results

        issues = self._filter_renovate_issues(issues)
        issues = self._filter_by_label_and_creator(issues)

        for issue in issues:
            issue_result = self._process_single_issue(repo_path, issue)
            results["issue_results"].append(issue_result)

            if issue_result["success"]:
                results["issues_processed"] += 1
                results["openagent_executions"] += issue_result.get("openagent_executions", 0)
                results["prs_created"] += issue_result.get("prs_created", 0)
                results["issues_closed"] += issue_result.get("issues_closed", 0)
            else:
                self.logger.warning(
                    f"Failed to process issue #{issue.get('number')}: {issue_result.get('error', 'Unknown error')}"
                )

        results["execution_time"] = self._get_elapsed_time(start_time)
        self._log_completion_summary(results)

        return results

    def _create_results_dict(self, start_time: float, repo_path: Path) -> Dict[str, Any]:
        """Create the initial results dictionary."""
        return {
            "worker_name": "GitHubIssueWorker",
            "execution_time": 0,
            "timestamp": start_time,
            "repo_path": str(repo_path),
            "dry_run": self.dry_run,
            "repositories_processed": 1,
            "repositories_with_errors": 0,
            "issues_processed": 0,
            "openagent_executions": 0,
            "prs_created": 0,
            "issues_closed": 0,
            "issue_results": [],
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

    def _is_renovate_issue(self, issue: Dict[str, Any]) -> bool:
        """Check if an issue is created by Renovate.

        Args:
            issue: The issue dictionary from GitHub API

        Returns:
            True if the issue is from Renovate, False otherwise
        """
        author_login = extract_author_login(issue)
        if author_login in ("renovate[bot]", "renovate"):
            return True

        label_names = extract_label_names(issue)
        if "renovate" in label_names:
            return True

        return False

    def _filter_renovate_issues(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter out issues created by Renovate.

        Args:
            issues: List of issue dictionaries

        Returns:
            List of issues with renovate issues removed
        """
        filtered = []
        for issue in issues:
            if self._is_renovate_issue(issue):
                self.logger.info(f"Skipping renovate issue #{issue.get('number')}: {issue.get('title')}")
            else:
                filtered.append(issue)
        return filtered

    def _should_process_issue(self, issue: Dict[str, Any]) -> bool:
        """Check if an issue should be processed based on label and creator.

        Args:
            issue: The issue dictionary from GitHub API

        Returns:
            True if the issue should be processed, False otherwise
        """
        required_label = settings.github_issue_worker_required_label
        allowed_creator = settings.github_issue_worker_allowed_creator

        label_names = extract_label_names(issue)
        label_names_lower = [label.lower() for label in label_names]

        has_required_label = required_label.lower() in label_names_lower
        author_login = extract_author_login(issue)
        is_allowed_creator = author_login == allowed_creator

        return has_required_label and is_allowed_creator

    def _filter_by_label_and_creator(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter issues based on required label and allowed creator.

        Args:
            issues: List of issue dictionaries

        Returns:
            List of issues that have the required label or are created by the allowed creator
        """
        filtered = []
        for issue in issues:
            if self._should_process_issue(issue):
                filtered.append(issue)
            else:
                self.logger.info(
                    f"Skipping issue #{issue.get('number')} '{issue.get('title')}': "
                    f"missing label '{settings.github_issue_worker_required_label}' "
                    f"and not created by '{settings.github_issue_worker_allowed_creator}'"
                )
        return filtered

    def _process_single_issue(self, repo_dir: Path, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single issue from the repository using Ralph loop.

        Args:
            repo_dir: Path to the repository directory
            issue: The issue dictionary from GitHub API

        Returns:
            Processing result for this issue
        """
        self.logger.info(f"Processing GitHub issue for: {repo_dir.name}")

        issue_number = issue["number"]
        issue_title = issue["title"]
        issue_body = issue.get("body", "") or ""

        self.logger.info(f"Processing issue #{issue_number}: {issue_title}")

        issue_author_login = extract_author_login(issue)
        comments = get_issue_comments(repo_dir, issue_number)
        comment_texts = [
            comment.get("body", "") or "" for comment in comments if comment.get("author") == issue_author_login
        ]

        result = {
            "repository": repo_dir.name,
            "issue_number": issue_number,
            "issue_title": issue_title,
            "success": False,
            "openagent_executed": False,
            "openagent_executions": 0,
            "pr_created": False,
            "prs_created": 0,
            "issue_closed": False,
            "issues_closed": 0,
            "error": None,
            "ralph_loops_executed": 0,
            "ralph_steps_completed": 0,
        }

        try:
            branch_name = f"ai/issue-{issue_number}-{sanitize_branch_name(issue_title[:30].lower())}"

            if self.dry_run:
                self.logger.info(f"DRY RUN: Would create branch {branch_name} and execute with Ralph loop")
                result["openagent_executed"] = True
                result["success"] = True
                return result

            branch_created = create_and_checkout_branch(repo_dir, branch_name, base_branch="main")
            if not branch_created:
                result["error"] = f"Failed to create branch {branch_name}"
                return result

            if settings.ralph_enabled:
                ralph_result = self._execute_with_ralph_loop(
                    repo_dir=repo_dir,
                    issue_number=issue_number,
                    issue_title=issue_title,
                    issue_body=issue_body,
                    comment_texts=comment_texts,
                    branch_name=branch_name,
                )
                result["ralph_loops_executed"] = ralph_result.get("loops_executed", 0)
                result["ralph_steps_completed"] = ralph_result.get("steps_completed", 0)
                result["openagent_executions"] = ralph_result.get("loops_executed", 0)

                if not ralph_result.get("success", False):
                    result["error"] = f"Ralph loop failed: {ralph_result.get('error', 'Unknown error')}"
                    return result

                result["openagent_executed"] = True
            else:
                instructions = self._build_instructions(issue_title, issue_body, comment_texts, branch_name=branch_name)

                openagent_result = execute_with_instructions(
                    instructions,
                    repo_dir,
                    self.agent_args,
                    self.timeout,
                    task_name="github_issue",
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
                self.logger.info(f"No changes made for issue #{issue_number}, closing issue with comment")

                no_changes_comment = (
                    "No changes required for this issue. The task has been reviewed and no modifications are needed."
                )
                comment_success = comment_on_issue(repo_dir, issue_number, no_changes_comment)
                result["issue_commented"] = comment_success

                close_success = close_issue(repo_dir, issue_number)
                result["issue_closed"] = close_success
                result["issues_closed"] = 1 if close_success else 0

                delete_branch(repo_dir, branch_name)

                result["success"] = True
                result["no_changes"] = True
                return result

            if settings.ralph_enabled:
                push_success, push_message = push_to_remote(repo_dir, remote="origin", branch=current_branch)
                if not push_success:
                    result["error"] = f"Failed to push branch '{current_branch}': {push_message}"
                    return result

                pr_body = self._generate_pr_body_from_task_file(
                    repo_dir=repo_dir,
                    issue_number=issue_number,
                    issue_title=issue_title,
                    issue_body=issue_body,
                )
            else:
                pr_body = f"Closes #{issue_number}\n\n{issue_body}"

            existing_pr = get_pr_for_branch(repo_dir, current_branch)
            if existing_pr and existing_pr.get("state") == "OPEN":
                result["pr_created"] = True
                result["pr_url"] = existing_pr.get("url", "")
                self.logger.info(f"PR already exists for branch '{current_branch}': {existing_pr.get('url', 'N/A')}")
            else:
                pr_result = create_pull_request(
                    repo_dir,
                    title=issue_title,
                    body=pr_body,
                    head=current_branch,
                    base="main",
                )

                if pr_result:
                    result["pr_created"] = True
                    result["pr_url"] = pr_result.get("url", "")
                    self.logger.info(f"Created PR for issue #{issue_number}: {pr_result.get('url', 'N/A')}")
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

            close_success = close_issue(repo_dir, issue_number)
            result["issue_closed"] = close_success

            if close_success:
                pr_url = result.get("pr_url", "")
                comment = f"Completed by PR: {pr_url}"
                comment_success = comment_on_issue(repo_dir, issue_number, comment)
                result["issue_commented"] = comment_success
                if not comment_success:
                    self.logger.warning(f"Failed to add comment to issue #{issue_number}")
            else:
                self.logger.warning(f"Failed to close issue #{issue_number}")

            result["success"] = True

        except Exception as e:
            self.logger.error(f"Error processing issue #{issue_number}: {str(e)}")
            result["error"] = str(e)

        return result

    def _execute_with_ralph_loop(
        self,
        repo_dir: Path,
        issue_number: int,
        issue_title: str,
        issue_body: str,
        comment_texts: List[str],
        branch_name: str,
    ) -> Dict[str, Any]:
        """Execute issue processing using refined task execution in .ralph/github-<issue>.md."""
        task_path = self._get_issue_task_path(repo_dir, issue_number)
        self._create_issue_task_file(
            task_path=task_path,
            issue_number=issue_number,
            issue_title=issue_title,
            issue_body=issue_body,
            comment_texts=comment_texts,
            branch_name=branch_name,
        )

        refinement_result = self._refine_issue_task_file(
            repo_dir=repo_dir,
            task_path=task_path,
            issue_title=issue_title,
            issue_body=issue_body,
            comment_texts=comment_texts,
            branch_name=branch_name,
        )
        if not refinement_result.get("success", False):
            return {
                "success": False,
                "error": refinement_result.get("error", "Failed to refine issue task"),
                "loops_executed": 1,
                "steps_completed": 0,
                "task_path": str(task_path),
            }

        self._ensure_last_step_is_make_test(task_path)

        execution_result = self._run_refined_task_loop(
            repo_dir=repo_dir,
            task_path=task_path,
            issue_title=issue_title,
            issue_body=issue_body,
            comment_texts=comment_texts,
            branch_name=branch_name,
        )
        execution_result["task_path"] = str(task_path)
        return execution_result

    def _get_issue_task_path(self, repo_dir: Path, issue_number: int) -> Path:
        """Get the canonical task file path for a GitHub issue."""
        return repo_dir / ".ralph" / f"github-{issue_number}.md"

    def _create_issue_task_file(
        self,
        task_path: Path,
        issue_number: int,
        issue_title: str,
        issue_body: str,
        comment_texts: List[str],
        branch_name: str,
    ) -> None:
        """Create the initial GitHub issue task file in .ralph."""
        comments_text = ""
        if comment_texts:
            comments_text = "Comments:\n" + "\n".join(f"- {comment}" for comment in comment_texts if comment) + "\n\n"

        content = (
            f"# GitHub Issue Task: {issue_title}\n\n"
            f"Issue Number: {issue_number}\n"
            f"Branch: {branch_name}\n\n"
            f"## Required Task\n\n"
            f"{issue_body}\n\n"
            f"{comments_text}"
            "## Steps\n\n"
            "- [ ] 1. Analyze the required implementation changes for this issue.\n"
            "  - Acceptance Criteria:\n"
            "    - The affected files and expected behavior are clearly identified.\n"
            "- [ ] 2. Implement the required code changes.\n"
            "  - Acceptance Criteria:\n"
            "    - Code changes are applied in the correct files.\n"
            "- [ ] 3. Update or add tests for the implementation.\n"
            "  - Acceptance Criteria:\n"
            "    - Tests cover the implemented behavior.\n"
            "- [ ] 4. Run `make test` and confirm it succeeds.\n"
            "  - Acceptance Criteria:\n"
            "    - `make test` exits successfully.\n"
        )

        task_path.parent.mkdir(parents=True, exist_ok=True)
        task_path.write_text(content)
        self.logger.info(f"Created issue task file: {task_path}")

    def _refine_issue_task_file(
        self,
        repo_dir: Path,
        task_path: Path,
        issue_title: str,
        issue_body: str,
        comment_texts: List[str],
        branch_name: str,
    ) -> Dict[str, Any]:
        """Ask slopmachine to refine the task into concrete steps with acceptance criteria."""
        instructions = self._build_refinement_instructions(
            task_path=task_path,
            issue_title=issue_title,
            issue_body=issue_body,
            comment_texts=comment_texts,
            branch_name=branch_name,
        )
        result = execute_with_instructions(
            instructions,
            repo_dir,
            self.agent_args,
            self.timeout,
            task_name="github_issue",
        )

        if not result.get("success", False):
            return {
                "success": False,
                "error": result.get("error", "Task refinement failed"),
            }

        try:
            refined_plan = PlanParser.parse_file(task_path)
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to parse refined task file: {str(e)}",
            }

        if not refined_plan.steps:
            return {
                "success": False,
                "error": "Refined task file does not contain any executable steps",
            }

        return {"success": True}

    def _ensure_last_step_is_make_test(self, task_path: Path) -> None:
        """Ensure the last task step always verifies that make test succeeds."""
        try:
            plan = PlanParser.parse_file(task_path)
        except Exception:
            return

        if not plan.steps:
            return

        last_step = plan.steps[-1]
        if "make test" in last_step.description.lower():
            return

        next_step_number = last_step.number + 1
        append_content = (
            f"\n- [ ] {next_step_number}. Run `make test` and confirm it succeeds.\n"
            "  - Acceptance Criteria:\n"
            "    - `make test` exits successfully.\n"
        )
        with task_path.open("a") as task_file:
            task_file.write(append_content)

    def _run_refined_task_loop(
        self,
        repo_dir: Path,
        task_path: Path,
        issue_title: str,
        issue_body: str,
        comment_texts: List[str],
        branch_name: str,
    ) -> Dict[str, Any]:
        """Iterate through task steps, implementing and validating acceptance criteria."""
        max_iterations = settings.github_issue_step_max_iterations
        result: Dict[str, Any] = {
            "success": False,
            "loops_executed": 0,
            "steps_completed": 0,
            "max_loops_reached": False,
        }

        for iteration in range(1, max_iterations + 1):
            try:
                plan = PlanParser.parse_file(task_path)
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to parse task file during iteration: {str(e)}",
                    "loops_executed": iteration,
                    "steps_completed": result["steps_completed"],
                    "max_loops_reached": False,
                }

            next_step = plan.get_next_open_step()
            if not next_step:
                result["success"] = True
                result["loops_executed"] = iteration - 1
                result["steps_completed"] = len([step for step in plan.steps if step.is_closed])
                return result

            step_result = self._execute_step(
                step=next_step,
                plan=plan,
                repo_dir=repo_dir,
                issue_title=issue_title,
                issue_body=issue_body,
                comment_texts=comment_texts,
                branch_name=branch_name,
            )
            if not step_result.get("success", False):
                result["last_error"] = step_result.get("error", "Step implementation failed")
                result["loops_executed"] = iteration
                continue

            acceptance_result = self._execute_step_acceptance_check(
                repo_dir=repo_dir,
                task_path=task_path,
                step=next_step,
                issue_title=issue_title,
                issue_body=issue_body,
                branch_name=branch_name,
            )
            if not acceptance_result.get("success", False):
                result["last_error"] = acceptance_result.get("error", "Acceptance criteria check failed")
                result["loops_executed"] = iteration
                continue

            if not self._step_is_closed(task_path, next_step.number):
                self._mark_step_completed_in_file(task_path, next_step.number)

            if not self._step_is_closed(task_path, next_step.number):
                result["last_error"] = f"Step {next_step.number} is still open after acceptance check"
                result["loops_executed"] = iteration
                continue

            remaining_steps_update_result = self._update_remaining_steps(
                repo_dir=repo_dir,
                task_path=task_path,
                step=next_step,
                issue_title=issue_title,
                issue_body=issue_body,
                branch_name=branch_name,
            )
            if not remaining_steps_update_result.get("success", False):
                self.logger.warning(
                    "Failed to update remaining steps after step completion: "
                    f"{remaining_steps_update_result.get('error', 'Unknown error')}"
                )

            repo_has_changes = False
            try:
                repo_has_changes = has_changes(repo_dir)
            except Exception as e:
                self.logger.warning(f"Could not determine git changes for step commit: {str(e)}")

            if repo_has_changes:
                commit_message = f"Complete issue step {next_step.number}: {next_step.description}"
                commit_success, _ = commit_and_push_changes(
                    repo_dir=repo_dir,
                    commit_message=commit_message,
                    push_if_remote=False,
                )
                if not commit_success:
                    return {
                        "success": False,
                        "error": f"Failed to commit changes for step {next_step.number}",
                        "loops_executed": iteration,
                        "steps_completed": result["steps_completed"],
                        "max_loops_reached": False,
                    }

            try:
                updated_plan = PlanParser.parse_file(task_path)
                result["steps_completed"] = len([step for step in updated_plan.steps if step.is_closed])
            except Exception:
                pass

            result["loops_executed"] = iteration

        result["max_loops_reached"] = True
        result["error"] = f"Maximum iterations ({max_iterations}) reached before all steps completed"
        return result

    def _execute_step(
        self,
        step: Step,
        plan: Plan,
        repo_dir: Path,
        issue_title: str,
        issue_body: str,
        comment_texts: List[str],
        branch_name: str,
    ) -> Dict[str, Any]:
        """Execute a single step from the plan.

        Args:
            step: Step to execute
            plan: Current plan
            repo_dir: Repository directory
            issue_title: Issue title
            issue_body: Issue body
            comment_texts: Comment texts
            branch_name: Branch name

        Returns:
            Execution result dictionary
        """
        step_instructions = self._build_step_instructions(
            step=step,
            plan=plan,
            issue_title=issue_title,
            issue_body=issue_body,
            comment_texts=comment_texts,
            branch_name=branch_name,
        )

        self.logger.info(f"Executing step {step.number}: {step.description}")

        result = execute_with_instructions(
            step_instructions,
            repo_dir,
            self.agent_args,
            self.timeout,
            task_name="github_issue",
        )

        if result.get("success", False):
            self.logger.info(f"Step {step.number} completed successfully")
        else:
            self.logger.warning(f"Step {step.number} failed: {result.get('error', 'Unknown error')}")

        return result

    def _execute_step_acceptance_check(
        self,
        repo_dir: Path,
        task_path: Path,
        step: Step,
        issue_title: str,
        issue_body: str,
        branch_name: str,
    ) -> Dict[str, Any]:
        """Run acceptance criteria validation for a step."""
        instructions = self._build_acceptance_check_instructions(
            task_path=task_path,
            step=step,
            issue_title=issue_title,
            issue_body=issue_body,
            branch_name=branch_name,
        )
        result = execute_with_instructions(
            instructions,
            repo_dir,
            self.agent_args,
            self.timeout,
            task_name="github_issue",
        )

        if not result.get("success", False):
            return {
                "success": False,
                "error": result.get("error", "Acceptance criteria check command failed"),
            }

        stdout_lower = (result.get("stdout") or "").lower()
        if "acceptance_status: fail" in stdout_lower or "acceptance status: fail" in stdout_lower:
            return {
                "success": False,
                "error": "Acceptance criteria were not fulfilled",
            }

        return {"success": True}

    def _update_remaining_steps(
        self,
        repo_dir: Path,
        task_path: Path,
        step: Step,
        issue_title: str,
        issue_body: str,
        branch_name: str,
    ) -> Dict[str, Any]:
        """Update future steps with details learned from a completed step."""
        instructions = self._build_remaining_steps_update_instructions(
            task_path=task_path,
            step=step,
            issue_title=issue_title,
            issue_body=issue_body,
            branch_name=branch_name,
        )
        result = execute_with_instructions(
            instructions,
            repo_dir,
            self.agent_args,
            self.timeout,
            task_name="github_issue",
        )
        if not result.get("success", False):
            return {
                "success": False,
                "error": result.get("error", "Failed to update remaining steps"),
            }

        return {"success": True}

    def _build_step_instructions(
        self,
        step: Step,
        plan: Plan,
        issue_title: str,
        issue_body: str,
        comment_texts: List[str],
        branch_name: str,
    ) -> str:
        """Build instructions for a single step.

        Args:
            step: Step to build instructions for
            plan: Current plan
            issue_title: Issue title
            issue_body: Issue body
            comment_texts: Comment texts
            branch_name: Branch name

        Returns:
            Instructions string for the step
        """
        body_text = build_body_section(issue_body)
        comments_text = build_comments_section(comment_texts)
        progress_info = self._build_progress_info(plan)

        return (
            f"You are already on branch '{branch_name}'. "
            f"Work on this branch, implement the changes, commit them, and push.\n"
            f"Implement the following:\n"
            f"Title: {issue_title}\n"
            f"Description:{body_text}\n"
            f"{comments_text}\n\n"
            f"Current Progress:\n{progress_info}\n\n"
            f"Your current task is Step {step.number}: {step.description}\n\n"
            f"{build_task_directive()}"
        )

    def _build_progress_info(self, plan: Plan) -> str:
        """Build progress information string.

        Args:
            plan: Current plan

        Returns:
            Progress information string
        """
        lines = []
        for step in plan.steps:
            status = "✓" if step.is_closed else "○"
            lines.append(f"{status} Step {step.number}: {step.description}")
        return "\n".join(lines)

    def _build_refinement_instructions(
        self,
        task_path: Path,
        issue_title: str,
        issue_body: str,
        comment_texts: List[str],
        branch_name: str,
    ) -> str:
        """Build instructions for refining the issue task file."""
        comments_text = build_comments_section(comment_texts)

        return (
            f"You are already on branch '{branch_name}'. "
            f"Refine the GitHub issue task file at '{task_path}'.\n"
            f"Issue title: {issue_title}\n"
            f"Issue description:\n{issue_body}\n"
            f"{comments_text}\n\n"
            "Rewrite the file into concrete implementation steps with explicit acceptance criteria.\n"
            "Requirements for the file format:\n"
            "- Keep a section named '## Steps'.\n"
            "- Each step must use this exact format: '- [ ] <number>. <step description>'.\n"
            "- Every step must include acceptance criteria directly below it as bullets.\n"
            "- Keep step numbering sequential and stable.\n"
            "- The last step must always verify that `make test` succeeds.\n"
            "- Do not commit, do not push, and do not create a PR.\n"
        )

    def _build_acceptance_check_instructions(
        self,
        task_path: Path,
        step: Step,
        issue_title: str,
        issue_body: str,
        branch_name: str,
    ) -> str:
        """Build instructions for acceptance criteria checks."""
        step_block = self._extract_step_block(task_path, step.number)
        return (
            f"You are already on branch '{branch_name}'. "
            f"Check acceptance criteria for Step {step.number} in '{task_path}'.\n"
            f"Issue title: {issue_title}\n"
            f"Issue description:\n{issue_body}\n\n"
            f"Step details:\n{step_block}\n\n"
            "Validate that all acceptance criteria are fulfilled.\n"
            "If all criteria are fulfilled, mark the step as completed in the task file.\n"
            "If criteria are not fulfilled, keep the step open.\n"
            "Do not commit, do not push, and do not create a PR.\n"
            "At the end, output exactly one line: ACCEPTANCE_STATUS: pass or ACCEPTANCE_STATUS: fail"
        )

    def _build_remaining_steps_update_instructions(
        self,
        task_path: Path,
        step: Step,
        issue_title: str,
        issue_body: str,
        branch_name: str,
    ) -> str:
        """Build instructions for updating remaining steps after a successful step."""
        step_block = self._extract_step_block(task_path, step.number)
        return (
            f"You are already on branch '{branch_name}'. "
            f"Update remaining open steps in '{task_path}' after completion of Step {step.number}.\n"
            f"Issue title: {issue_title}\n"
            f"Issue description:\n{issue_body}\n\n"
            f"Completed step details:\n{step_block}\n\n"
            "Update only unchecked steps to include concrete details learned from the completed step.\n"
            "Do not alter numbering, and do not modify completed steps.\n"
            "Do not commit, do not push, and do not create a PR."
        )

    def _extract_step_block(self, task_path: Path, step_number: int) -> str:
        """Extract a step block (step line plus child lines) from the task markdown file."""
        content = task_path.read_text()
        lines = content.splitlines()
        step_pattern = re.compile(r"^\s*-\s\[[ x]\]\s*\d+\.\s+")
        target_pattern = re.compile(rf"^\s*-\s\[[ x]\]\s*{step_number}\.\s+")

        start_idx: Optional[int] = None
        end_idx = len(lines)

        for idx, line in enumerate(lines):
            if target_pattern.match(line):
                start_idx = idx
                break

        if start_idx is None:
            return f"- [ ] {step_number}. {self._find_step_description(task_path, step_number)}"

        for idx in range(start_idx + 1, len(lines)):
            if step_pattern.match(lines[idx]):
                end_idx = idx
                break

        return "\n".join(lines[start_idx:end_idx]).strip()

    def _find_step_description(self, task_path: Path, step_number: int) -> str:
        """Fallback helper to retrieve the step description for a given step number."""
        try:
            plan = PlanParser.parse_file(task_path)
        except Exception:
            return "Unknown step"
        for step in plan.steps:
            if step.number == step_number:
                return step.description
        return "Unknown step"

    def _step_is_closed(self, task_path: Path, step_number: int) -> bool:
        """Check whether a step is marked as completed in the task file."""
        try:
            plan = PlanParser.parse_file(task_path)
        except Exception:
            return False
        for step in plan.steps:
            if step.number == step_number:
                return step.is_closed
        return False

    def _mark_step_completed_in_file(self, task_path: Path, step_number: int) -> None:
        """Mark a step as completed directly in markdown without rewriting the full file."""
        content = task_path.read_text()
        pattern = re.compile(rf"^(\s*-\s)\[\s\](\s*{step_number}\.\s+)", re.MULTILINE)
        updated_content, replacements = pattern.subn(r"\1[x]\2", content, count=1)
        if replacements > 0:
            task_path.write_text(updated_content)

    def _build_instructions(
        self,
        issue_title: str,
        issue_body: str,
        comments: Optional[List[str]] = None,
        branch_name: Optional[str] = None,
    ) -> str:
        """Build the instructions string from issue title, body, and comments.

        Args:
            issue_title: Issue title
            issue_body: Issue body
            comments: List of comment bodies
            branch_name: Name of the branch already created for this issue

        Returns:
            Complete instructions string
        """
        body_text = build_body_section(issue_body)
        comments_text = build_comments_section(comments) if comments else ""
        branch_instruction = build_branch_instruction(branch_name)

        return (
            f"{branch_instruction}"
            f"Implement the following:\n"
            f"Title: {issue_title}\n"
            f"Description:{body_text}\n"
            f"{comments_text}"
            f"{build_plan_text()}\n"
            f"{build_task_directive()}"
        )

    def _generate_pr_body_from_task_file(
        self,
        repo_dir: Path,
        issue_number: int,
        issue_title: str,
        issue_body: str,
    ) -> str:
        """Generate PR description from the refined GitHub task file using slopmachine."""
        task_path = self._get_issue_task_path(repo_dir, issue_number)
        default_body = f"Closes #{issue_number}\n\n{issue_body}"

        if not task_path.exists():
            return default_body

        task_content = task_path.read_text()
        instructions = self._build_pr_description_instructions(
            issue_number=issue_number,
            issue_title=issue_title,
            issue_body=issue_body,
            task_content=task_content,
        )

        result = execute_with_instructions(
            instructions,
            repo_dir,
            self.agent_args,
            self.timeout,
            task_name="github_issue",
        )
        if not result.get("success", False):
            return default_body

        generated_body = (result.get("stdout") or "").strip()
        if not generated_body:
            return default_body

        if f"closes #{issue_number}" not in generated_body.lower():
            generated_body = f"Closes #{issue_number}\n\n{generated_body}"

        return generated_body

    def _build_pr_description_instructions(
        self,
        issue_number: int,
        issue_title: str,
        issue_body: str,
        task_content: str,
    ) -> str:
        """Build instructions for generating a PR description from task steps."""
        return (
            "Generate a pull request description in markdown.\n"
            f"Issue number: {issue_number}\n"
            f"Issue title: {issue_title}\n"
            f"Issue description:\n{issue_body}\n\n"
            "Use the completed steps from this task markdown as the source of truth:\n"
            "----- BEGIN TASK -----\n"
            f"{task_content}\n"
            "----- END TASK -----\n\n"
            "Requirements:\n"
            "- Include a concise summary of what changed.\n"
            "- Include completed steps that were implemented.\n"
            "- Include test verification details.\n"
            f"- Include `Closes #{issue_number}` in the final PR description.\n"
            "- Return markdown only. Do not modify files.\n"
        )

    def _create_error_result(self, start_time: float, repo_path: Path, error_msg: str) -> Dict[str, Any]:
        """Create an error result dictionary."""
        return {
            "worker_name": "GitHubIssueWorker",
            "execution_time": self._get_elapsed_time(start_time),
            "timestamp": start_time,
            "repo_path": str(repo_path),
            "dry_run": self.dry_run,
            "success": False,
            "error": error_msg,
            "repositories_processed": 0,
            "repositories_with_errors": 1,
            "issues_processed": 0,
            "openagent_executions": 0,
            "prs_created": 0,
            "issues_closed": 0,
            "issue_results": [],
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
            f"GitHubIssueWorker completed. Processed: "
            f"{results['issues_processed']}, "
            f"{cli_tool} executions: {results['openagent_executions']}, "
            f"PRs created: {results['prs_created']}, "
            f"Issues closed: {results['issues_closed']}, "
            f"Errors: {results['repositories_with_errors']}"
        )
