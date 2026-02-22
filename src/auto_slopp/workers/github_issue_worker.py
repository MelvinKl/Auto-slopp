"""GitHub Issue Worker for processing open issues as instructions.

This worker:
1. Searches each repository for open issues on GitHub
2. Uses issue title/body as instructions (similar to TaskProcessorWorker)
3. Creates a new branch starting with ai/
4. Executes instructions using OpenCode
5. Creates a PR and closes the issue
"""

import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from auto_slopp.utils.git_operations import (
    checkout_branch_resilient,
    commit_and_push_changes,
)
from auto_slopp.utils.github_operations import (
    close_issue,
    comment_on_issue,
    comment_on_pr,
    create_pull_request,
    get_issue_comments,
    get_open_issues,
)
from auto_slopp.utils.opencode import execute_openagent_with_instructions
from auto_slopp.worker import Worker


class GitHubIssueWorker(Worker):
    """Worker for processing GitHub issues as instructions.

    This worker searches each repository for open issues on GitHub,
    uses the issue title and body as instructions for OpenCode,
    creates a new branch, executes the instructions, and creates a PR.
    """

    def __init__(
        self,
        timeout: int = 7200,
        agent_args: Optional[List[str]] = None,
        dry_run: bool = False,
    ):
        """Initialize the GitHubIssueWorker.

        Args:
            timeout: Timeout for OpenCode execution in seconds
            agent_args: Additional arguments to pass to OpenCode
            dry_run: If True, skip actual OpenCode execution and git operations
        """
        self.timeout = timeout
        self.agent_args = agent_args or []
        self.dry_run = dry_run
        self.logger = logging.getLogger("auto_slopp.workers.GitHubIssueWorker")

    def run(self, repo_path: Path, task_path: Path) -> Dict[str, Any]:
        """Execute the GitHub issue processing workflow for a single repository.

        Args:
            repo_path: Path to the repository directory
            task_path: Path to the task directory (unused but kept for signature)

        Returns:
            Dictionary containing execution results and statistics
        """
        start_time = self._get_current_time()
        self.logger.info(f"GitHubIssueWorker starting with repo_path: {repo_path}")

        if not repo_path.exists():
            return self._create_error_result(
                start_time,
                repo_path,
                task_path,
                f"Repository path does not exist: {repo_path}",
            )

        results = self._create_results_dict(start_time, repo_path, task_path)

        issue_result = self._process_single_issue(repo_path)
        results["issue_results"].append(issue_result)

        if issue_result.get("no_issues", False):
            pass  # No issues to process
        elif issue_result["success"]:
            results["issues_processed"] += 1
            results["openagent_executions"] += issue_result.get("openagent_executions", 0)
            results["prs_created"] += issue_result.get("prs_created", 0)
            results["issues_closed"] += issue_result.get("issues_closed", 0)
        else:
            results["repositories_with_errors"] += 1
            results["success"] = False

        results["execution_time"] = self._get_elapsed_time(start_time)
        self._log_completion_summary(results)

        return results

    def _create_results_dict(self, start_time: float, repo_path: Path, task_path: Path) -> Dict[str, Any]:
        """Create the initial results dictionary."""
        return {
            "worker_name": "GitHubIssueWorker",
            "execution_time": 0,
            "timestamp": start_time,
            "repo_path": str(repo_path),
            "task_path": str(task_path),
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

    def _process_single_issue(self, repo_dir: Path) -> Dict[str, Any]:
        """Process a single issue from the repository.

        Args:
            repo_dir: Path to the repository directory

        Returns:
            Processing result for this issue
        """
        self.logger.info(f"Processing GitHub issues for: {repo_dir.name}")

        if not self.dry_run:
            pull_success = checkout_branch_resilient(
                repo_dir=repo_dir,
                branch="main",
                fetch_first=True,
                timeout=60,
            )
            if not pull_success:
                self.logger.warning(f"Failed to pull latest changes from {repo_dir.name}")

        issues = get_open_issues(repo_dir)

        if not issues:
            self.logger.info(f"No open issues found in {repo_dir.name}")
            return {
                "repository": repo_dir.name,
                "success": True,
                "no_issues": True,
            }

        issue = issues[0]
        issue_number = issue["number"]
        issue_title = issue["title"]
        issue_body = issue.get("body", "") or ""

        self.logger.info(f"Processing issue #{issue_number}: {issue_title}")

        comments = get_issue_comments(repo_dir, issue_number)
        comment_texts = [comment.get("body", "") or "" for comment in comments]

        result = {
            "repository": repo_dir.name,
            "issue_number": issue_number,
            "issue_title": issue_title,
            "success": False,
            "openagent_executed": False,
            "pr_created": False,
            "issue_closed": False,
            "error": None,
        }

        try:
            instructions = self._build_instructions(issue_title, issue_body, comment_texts)
            branch_name = f"ai/issue-{issue_number}-{issue_title[:30].replace(' ', '-').lower()}"

            if self.dry_run:
                self.logger.info(f"DRY RUN: Would create branch {branch_name} and execute instructions")
                result["openagent_executed"] = True
                result["success"] = True
                return result

            openagent_result = execute_openagent_with_instructions(
                instructions, repo_dir, self.agent_args, self.timeout
            )
            result["openagent_executed"] = openagent_result["success"]

            if not openagent_result["success"]:
                result["error"] = f"OpenCode execution failed: {openagent_result.get('error', 'Unknown error')}"
                return result

            pr_body = f"Closes #{issue_number}\n\n{issue_body}"
            pr_result = create_pull_request(
                repo_dir,
                title=issue_title,
                body=pr_body,
                head=branch_name,
                base="main",
            )

            if pr_result:
                result["pr_created"] = True
                result["pr_url"] = pr_result.get("url", "")
                result["pr_number"] = pr_result.get("number")
                self.logger.info(f"Created PR for issue #{issue_number}: {pr_result.get('url', 'N/A')}")
            else:
                result["error"] = "Failed to create pull request"
                return result

            pr_url = pr_result.get("url", "")
            pr_number = pr_result.get("number")
            issue_comment = f"Completed by PR: {pr_url}"
            comment_success = comment_on_issue(repo_dir, issue_number, issue_comment)
            result["issue_commented"] = comment_success
            if not comment_success:
                self.logger.warning(f"Failed to add comment to issue #{issue_number}")

            close_success = close_issue(repo_dir, issue_number)
            result["issue_closed"] = close_success

            if close_success:
                pr_comment = f"Resolves #{issue_number}"
                pr_comment_success = comment_on_pr(repo_dir, pr_number, pr_comment)
                result["pr_commented"] = pr_comment_success
                if not pr_comment_success:
                    self.logger.warning(f"Failed to add comment to PR #{pr_number}")
            else:
                self.logger.warning(f"Failed to close issue #{issue_number}")

            result["success"] = True

        except Exception as e:
            self.logger.error(f"Error processing issue #{issue_number}: {str(e)}")
            result["error"] = str(e)

        return result

    def _build_instructions(self, issue_title: str, issue_body: str, comments: Optional[List[str]] = None) -> str:
        """Build the instructions string from issue title, body, and comments.

        Args:
            issue_title: Issue title
            issue_body: Issue body
            comments: List of comment bodies

        Returns:
            Complete instructions string
        """
        body_text = f"\n{issue_body}" if issue_body else ""
        comments_text = ""
        if comments:
            comments_text = "\nComments:\n" + "\n".join(f"- {comment}" for comment in comments if comment)
        return (
            f"Create a new branch that starts with ai/ from base origin/main and implement the following:\n"
            f"Title: {issue_title}\n"
            f"Description:{body_text}\n"
            f"{comments_text}\n"
            f"Keep your implementation simple. Only implement what is required. Check if there are components you can reuse. "
            f"Ensure that 'make test' runs successful. Only push if ALL tests are successful. "
            f"Check if you need to update the README.md. Push your changes and create a pull request on github."
        )

    def _create_error_result(
        self, start_time: float, repo_path: Path, task_path: Path, error_msg: str
    ) -> Dict[str, Any]:
        """Create an error result dictionary."""
        return {
            "worker_name": "GitHubIssueWorker",
            "execution_time": self._get_elapsed_time(start_time),
            "timestamp": start_time,
            "repo_path": str(repo_path),
            "task_path": str(task_path),
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
        self.logger.info(
            f"GitHubIssueWorker completed. Processed: "
            f"{results['issues_processed']}, "
            f"OpenCode executions: {results['openagent_executions']}, "
            f"PRs created: {results['prs_created']}, "
            f"Issues closed: {results['issues_closed']}, "
            f"Errors: {results['repositories_with_errors']}"
        )
