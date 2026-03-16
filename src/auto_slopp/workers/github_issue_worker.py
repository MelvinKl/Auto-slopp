"""GitHub Issue Worker for processing open issues as instructions.

This worker:
1. Searches each repository for open issues on GitHub
2. Uses issue title/body as instructions
3. Creates a new branch starting with ai/
4. Creates a plan file with steps and executes them using the Ralph loop
5. Creates a PR and closes the issue
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
    delete_branch,
    get_current_branch,
    has_changes,
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
    PlanWriter,
    RalphLoop,
    Step,
    create_default_plan_steps,
)
from auto_slopp.worker import Worker
from settings.main import settings


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
        author = issue.get("author", {})
        author_login = author.get("login", "") if author else ""
        if author_login in ("renovate[bot]", "renovate"):
            return True

        labels = issue.get("labels", [])
        label_names = [label.get("name", "") for label in labels]
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

        labels = issue.get("labels", [])
        label_names = [label.get("name", "") for label in labels]
        label_names_lower = [label.lower() for label in label_names]

        has_required_label = required_label.lower() in label_names_lower
        author = issue.get("author", {})
        author_login = author.get("login", "") if author else ""
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

        issue_author_login = issue.get("author", {}).get("login", "") if issue.get("author") else ""
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
        """Execute issue processing using Ralph loop.

        Args:
            repo_dir: Path to the repository directory
            issue_number: Issue number
            issue_title: Issue title
            issue_body: Issue body
            comment_texts: List of comment texts
            branch_name: Branch name

        Returns:
            Result dictionary from Ralph loop execution
        """
        plan_path = repo_dir / ".ralph" / f"issue-{issue_number}-plan.md"

        plan = self._create_issue_plan(
            plan_path=plan_path,
            issue_title=issue_title,
            issue_body=issue_body,
            comment_texts=comment_texts,
            branch_name=branch_name,
        )

        def step_executor(step: Step, current_plan: Plan) -> Dict[str, Any]:
            return self._execute_step(
                step=step,
                plan=current_plan,
                repo_dir=repo_dir,
                issue_title=issue_title,
                issue_body=issue_body,
                comment_texts=comment_texts,
                branch_name=branch_name,
            )

        ralph_loop = RalphLoop(
            plan_path=plan_path,
            max_loops=settings.ralph_max_loops,
            step_executor=step_executor,
        )
        ralph_loop.plan = plan

        return ralph_loop.run()

    def _create_issue_plan(
        self,
        plan_path: Path,
        issue_title: str,
        issue_body: str,
        comment_texts: List[str],
        branch_name: str,
    ) -> Plan:
        """Create a plan file for the issue.

        Args:
            plan_path: Path to save the plan file
            issue_title: Issue title
            issue_body: Issue body
            comment_texts: List of comment texts
            branch_name: Branch name

        Returns:
            Created Plan object
        """
        description = f"Branch: {branch_name}\n\n{issue_body}"
        if comment_texts:
            description += "\n\nComments:\n" + "\n".join(f"- {c}" for c in comment_texts if c)

        steps = create_default_plan_steps()

        plan = Plan(
            title=f"Issue Plan: {issue_title}",
            description=description
            + "\nEnsure that you save the result of each step in a file in .ralph directory. Check there for relevant files before each step and load them.\n",
            steps=[Step(number=i + 1, description=desc, is_closed=False) for i, desc in enumerate(steps)],
        )

        PlanWriter.write_file(plan, plan_path)
        self.logger.info(f"Created plan file: {plan_path}")

        return plan

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
        body_text = f"\n{issue_body}" if issue_body else ""
        comments_text = ""
        if comment_texts:
            comments_text = "\nComments:\n" + "\n".join(f"- {comment}" for comment in comment_texts if comment)

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
            Progress information string
        """
        lines = []
        for step in plan.steps:
            status = "✓" if step.is_closed else "○"
            lines.append(f"{status} Step {step.number}: {step.description}")
        return "\n".join(lines)

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
        body_text = f"\n{issue_body}" if issue_body else ""
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
            f"Title: {issue_title}\n"
            f"Description:{body_text}\n"
            f"{comments_text}\n"
            f"{plan_text}\n"
            f"Keep your implementation simple. Only implement what is required. "
            f"Check if there are components you can reuse. "
            f"Ensure that 'make test' runs successful. Only push if ALL tests are successful. "
            f"Check if you need to update the README.md."
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
