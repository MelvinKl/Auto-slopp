"""GitHub task source for loading GitHub issues as tasks.

This module provides a TaskSource implementation that loads tasks from
GitHub Issues, following the same patterns used by GitHubIssueWorker.
"""

import logging
from pathlib import Path
from typing import List

from auto_slopp.utils.git_operations import sanitize_branch_name
from auto_slopp.utils.github_operations import (
    close_issue,
    comment_on_issue,
    get_issue_comments,
    get_open_issues,
    remove_label_from_issue,
)
from auto_slopp.workers.task_source import Task, TaskSource
from settings.main import settings

logger = logging.getLogger(__name__)


class GitHubTaskSource(TaskSource):
    """Task source that loads tasks from GitHub Issues."""

    def get_tasks(self, repo_path: Path) -> List[Task]:
        """Fetch and filter tasks from GitHub Issues.

        Args:
            repo_path: Path to the repository directory

        Returns:
            List of normalized Task objects ready for processing
        """
        issues = get_open_issues(repo_path)

        if not issues:
            return []

        issues = self._filter_renovate_issues(issues)
        issues = self._filter_by_label_and_creator(issues)
        issues = sorted(issues, key=lambda i: i.get("number", 0))

        tasks = []
        for issue in issues:
            issue_number = issue["number"]
            issue_title = issue["title"]
            issue_body = issue.get("body", "") or ""

            issue_author_login = issue.get("author", {}).get("login", "") if issue.get("author") else ""
            comments = get_issue_comments(repo_path, issue_number)
            comment_texts = [
                comment.get("body", "") or "" for comment in comments if comment.get("author") == issue_author_login
            ]

            task = Task(
                id=issue_number,
                title=issue_title,
                body=issue_body,
                comments=comment_texts,
                raw={"_repo_path": repo_path, **issue},
            )
            tasks.append(task)

        return tasks

    def get_branch_name(self, task: Task) -> str:
        """Generate the branch name for a GitHub issue task.

        Args:
            task: The task to generate a branch name for

        Returns:
            Branch name string (e.g., 'ai/issue-42-fix-bug')
        """
        sanitized_title = sanitize_branch_name(task.title[:30].lower())
        return f"ai/issue-{task.id}-{sanitized_title}"

    def get_ralph_file_prefix(self) -> str:
        """Return the prefix for ralph task files.

        Returns:
            Prefix string 'github'
        """
        return "github"

    def get_task_difficulty_name(self) -> str:
        """Return the task difficulty name for CLI executor mapping.

        Returns:
            Task name string 'github_issue' matching settings.task_difficulties keys
        """
        return "github_issue"

    def get_default_pr_body(self, task: Task) -> str:
        """Generate the default PR body for a GitHub issue.

        Args:
            task: The task to generate a PR body for

        Returns:
            PR body string in markdown
        """
        return f"Closes #{task.id}\n\n{task.body}"

    def on_task_start(self, task: Task, branch_name: str) -> None:
        """Called when task processing begins.

        For GitHub tasks, this is a no-op since branch creation is handled
        by the worker's execution flow.

        Args:
            task: The task being started
            branch_name: The branch created for this task
        """
        pass

    def on_task_complete(self, task: Task, branch_name: str, pr_url: str) -> None:
        """Called when a task completes successfully.

        Closes GitHub issue and adds a comment with the PR URL.

        Args:
            task: The completed task
            branch_name: The branch used for this task
            pr_url: URL of the created pull request
        """
        repo_path = task.raw.get("_repo_path")
        if repo_path is None:
            logger.warning(f"No repo_path found in task #{task.id}, skipping completion handling")
            return

        close_success = close_issue(repo_path, task.id)

        if close_success:
            comment = f"Completed by PR: {pr_url}"
            comment_success = comment_on_issue(repo_path, task.id, comment)
            if not comment_success:
                logger.warning(f"Failed to add comment to issue #{task.id}")
        else:
            logger.warning(f"Failed to close issue #{task.id}")

    def on_task_failure(self, task: Task, error: str) -> None:
        """Called when a task fails.

        For GitHub tasks, this is a no-op. Error handling is managed
        by the worker's execution flow.

        Args:
            task: The failed task
            error: Error description
        """
        pass

    def on_no_changes(self, task: Task) -> None:
        """Called when no changes were needed for a task.

        Closes GitHub issue with a comment indicating no changes were needed.

        Args:
            task: The task that required no changes
        """
        repo_path = task.raw.get("_repo_path")
        if repo_path is None:
            logger.warning(f"No repo_path found in task #{task.id}, skipping no-changes handling")
            return

        no_changes_comment = (
            "No changes required for this issue. The task has been reviewed and no modifications are needed."
        )
        comment_on_issue(repo_path, task.id, no_changes_comment)
        close_issue(repo_path, task.id)

    def on_max_iterations_reached(self, task: Task, steps_completed: int, total_steps: int, error: str) -> None:
        """Called when the ralph loop reaches max iterations without completing.

        Removes the required label from the issue and adds a failure comment.

        Args:
            task: The task that hit the iteration limit
            steps_completed: Number of steps completed
            total_steps: Total number of steps
            error: Last error message
        """
        repo_path = task.raw.get("_repo_path")
        if repo_path is None:
            logger.warning(f"No repo_path found in task #{task.id}, skipping max-iterations handling")
            return

        failure_comment = (
            f"⚠️ **Task Failed: Maximum Iterations Reached**\n\n"
            f" Ralph loop reached maximum iterations without completing all steps.\n\n"
            f"**Progress:**\n"
            f"- Steps completed: {steps_completed}/{total_steps}\n"
            f"- Last error: {error}\n\n"
            f"This issue will not be processed again automatically."
        )
        comment_on_issue(repo_path, task.id, failure_comment)

        label_removed = remove_label_from_issue(
            repo_path,
            task.id,
            settings.github_issue_worker_required_label,
        )
        if label_removed:
            logger.info(f"Removed required label '{settings.github_issue_worker_required_label}' from issue #{task.id}")
        else:
            logger.warning(f"Failed to remove required label from issue #{task.id}")

    def _filter_renovate_issues(self, issues: List[dict]) -> List[dict]:
        """Filter out issues created by Renovate.

        Args:
            issues: List of issue dictionaries

        Returns:
            List of issues with renovate issues removed
        """
        filtered = []
        for issue in issues:
            if self._is_renovate_issue(issue):
                logger.info(f"Skipping renovate issue #{issue.get('number')}: {issue.get('title')}")
            else:
                filtered.append(issue)
        return filtered

    def _is_renovate_issue(self, issue: dict) -> bool:
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

    def _should_process_issue(self, issue: dict) -> bool:
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

    def _filter_by_label_and_creator(self, issues: List[dict]) -> List[dict]:
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
                logger.info(
                    f"Skipping issue #{issue.get('number')} '{issue.get('title')}': "
                    f"missing label '{settings.github_issue_worker_required_label}' "
                    f"and not created by '{settings.github_issue_worker_allowed_creator}'"
                )
        return filtered
